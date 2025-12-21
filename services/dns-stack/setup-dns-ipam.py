#!/usr/bin/env python3
"""
Homelab DNS and IPAM Setup Script

This script:
1. Pulls device data from Unifi Controller
2. Populates Netbox with sites, prefixes, and IP addresses
3. Configures Technitium DNS zones and records
4. Sets up automatic sync between Netbox and DNS

Author: Homelab Automation
"""

import sys
import json
import requests
import urllib3
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
UNIFI_URL = "https://10.203.3.1"
UNIFI_API_KEY = "KdUEfY_59qUUkMjPyZsJtIpNIeYVfjhA"
NETBOX_URL = "http://10.203.3.202:8080"
NETBOX_TOKEN = "0123456789abcdef0123456789abcdef01234567"  # Get from Django shell or web UI
NETBOX_USER = "admin"
NETBOX_PASS = "changeme"
DNS_URL = "http://10.203.3.203:5380"
DNS_USER = "admin"
DNS_PASS = "changeme"
DNS_ZONE = "hq.doofus.co"
DNS_UPSTREAM = ["1.1.1.1", "8.8.8.8"]

# Site configuration
SITE_NAME = "HQ"
SITE_SLUG = "hq"
PREFIX_NETWORK = "10.203.3.0/24"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiController:
    """Client for Unifi Controller API"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "X-API-KEY": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_clients(self) -> List[Dict]:
        """Get all clients from Unifi controller"""
        try:
            url = f"{self.base_url}/proxy/network/api/s/default/stat/sta"
            response = requests.get(
                url,
                headers=self.headers,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                clients = data.get("data", [])
                logger.info(f"Retrieved {len(clients)} clients from Unifi")
                return clients
            else:
                logger.error(f"Unifi API error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching clients from Unifi: {e}")
            return []

    def export_to_csv(self, clients: List[Dict], filename: str):
        """Export clients to CSV file"""
        import csv

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['hostname', 'ip', 'mac', 'name', 'type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for client in clients:
                writer.writerow({
                    'hostname': client.get('hostname', client.get('name', 'unknown')),
                    'ip': client.get('ip', ''),
                    'mac': client.get('mac', ''),
                    'name': client.get('name', client.get('hostname', '')),
                    'type': 'wireless' if client.get('is_wired', False) is False else 'wired'
                })

        logger.info(f"Exported {len(clients)} clients to {filename}")


class NetboxClient:
    """Client for Netbox API"""

    def __init__(self, base_url: str, token: str = None, username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # If token provided, set it immediately
        if token:
            self.headers["Authorization"] = f"Token {token}"

    def login(self) -> bool:
        """Login and get API token"""
        # If token already set, verify it works
        if self.token:
            try:
                response = requests.get(
                    f"{self.base_url}/api/status/",
                    headers=self.headers,
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info("Successfully authenticated with Netbox using provided token")
                    return True
            except Exception as e:
                logger.error(f"Token verification failed: {e}")
                return False

        # Otherwise try username/password
        try:
            # First, try to get or create API token
            response = requests.post(
                f"{self.base_url}/api/users/tokens/provision/",
                auth=(self.username, self.password),
                json={"username": self.username},
                timeout=10
            )

            if response.status_code in [200, 201]:
                data = response.json()
                self.token = data.get("key")
                self.headers["Authorization"] = f"Token {self.token}"
                logger.info("Successfully authenticated with Netbox")
                return True
            else:
                logger.error(f"Netbox login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Netbox login error: {e}")
            return False

    def create_site(self, name: str, slug: str) -> Optional[int]:
        """Create a site in Netbox"""
        try:
            # Check if site exists
            response = requests.get(
                f"{self.base_url}/api/dcim/sites/",
                headers=self.headers,
                params={"slug": slug},
                timeout=10
            )

            if response.status_code == 200:
                sites = response.json().get("results", [])
                if sites:
                    site_id = sites[0]["id"]
                    logger.info(f"Site '{name}' already exists (ID: {site_id})")
                    return site_id

            # Create new site
            response = requests.post(
                f"{self.base_url}/api/dcim/sites/",
                headers=self.headers,
                json={
                    "name": name,
                    "slug": slug,
                    "status": "active"
                },
                timeout=10
            )

            if response.status_code == 201:
                site_id = response.json()["id"]
                logger.info(f"Created site '{name}' (ID: {site_id})")
                return site_id
            else:
                logger.error(f"Failed to create site: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating site: {e}")
            return None

    def create_prefix(self, prefix: str, site_id: int) -> Optional[int]:
        """Create a prefix in Netbox"""
        try:
            # Check if prefix exists
            response = requests.get(
                f"{self.base_url}/api/ipam/prefixes/",
                headers=self.headers,
                params={"prefix": prefix},
                timeout=10
            )

            if response.status_code == 200:
                prefixes = response.json().get("results", [])
                if prefixes:
                    prefix_id = prefixes[0]["id"]
                    logger.info(f"Prefix '{prefix}' already exists (ID: {prefix_id})")
                    return prefix_id

            # Create new prefix
            response = requests.post(
                f"{self.base_url}/api/ipam/prefixes/",
                headers=self.headers,
                json={
                    "prefix": prefix,
                    "site": site_id,
                    "status": "active"
                },
                timeout=10
            )

            if response.status_code == 201:
                prefix_id = response.json()["id"]
                logger.info(f"Created prefix '{prefix}' (ID: {prefix_id})")
                return prefix_id
            else:
                logger.error(f"Failed to create prefix: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating prefix: {e}")
            return None

    def create_ip_address(self, ip: str, dns_name: str, description: str = "") -> bool:
        """Create an IP address in Netbox"""
        try:
            # Check if IP exists
            response = requests.get(
                f"{self.base_url}/api/ipam/ip-addresses/",
                headers=self.headers,
                params={"address": f"{ip}/24"},
                timeout=10
            )

            if response.status_code == 200:
                ips = response.json().get("results", [])
                if ips:
                    # Update existing IP
                    ip_id = ips[0]["id"]
                    response = requests.patch(
                        f"{self.base_url}/api/ipam/ip-addresses/{ip_id}/",
                        headers=self.headers,
                        json={
                            "dns_name": dns_name,
                            "description": description
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        logger.info(f"Updated IP {ip} -> {dns_name}")
                        return True
                    return False

            # Create new IP
            response = requests.post(
                f"{self.base_url}/api/ipam/ip-addresses/",
                headers=self.headers,
                json={
                    "address": f"{ip}/24",
                    "dns_name": dns_name,
                    "status": "active",
                    "description": description
                },
                timeout=10
            )

            if response.status_code == 201:
                logger.info(f"Created IP {ip} -> {dns_name}")
                return True
            else:
                logger.error(f"Failed to create IP {ip}: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error creating IP {ip}: {e}")
            return False


class TechnitiumDNS:
    """Client for Technitium DNS Server API"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None

    def login(self) -> bool:
        """Authenticate with Technitium DNS server"""
        try:
            response = requests.get(
                f"{self.base_url}/api/user/login",
                params={
                    "user": self.username,
                    "pass": self.password,
                    "includeInfo": "false"
                },
                timeout=10
            )
            data = response.json()
            if data.get("status") == "ok":
                self.token = data.get("token")
                logger.info("Successfully authenticated with DNS server")
                return True
            else:
                logger.error(f"DNS login failed: {data.get('errorMessage', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"DNS login error: {e}")
            return False

    def create_zone(self, zone: str) -> bool:
        """Create a primary zone"""
        if not self.token:
            return False

        try:
            response = requests.get(
                f"{self.base_url}/api/zones/create",
                params={
                    "token": self.token,
                    "zone": zone,
                    "type": "Primary"
                },
                timeout=10
            )
            data = response.json()
            if data.get("status") == "ok":
                logger.info(f"Created DNS zone: {zone}")
                return True
            elif "already exists" in data.get("errorMessage", "").lower():
                logger.info(f"DNS zone already exists: {zone}")
                return True
            else:
                logger.error(f"Failed to create zone: {data.get('errorMessage', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error creating zone: {e}")
            return False

    def add_record(self, zone: str, hostname: str, ip: str) -> bool:
        """Add an A record to the zone"""
        if not self.token:
            return False

        fqdn = f"{hostname}.{zone}" if not hostname.endswith(zone) else hostname

        try:
            response = requests.get(
                f"{self.base_url}/api/zones/records/add",
                params={
                    "token": self.token,
                    "zone": zone,
                    "domain": fqdn,
                    "type": "A",
                    "ipAddress": ip,
                    "ttl": 3600,
                    "overwrite": "true"
                },
                timeout=10
            )
            data = response.json()
            if data.get("status") == "ok":
                logger.info(f"Added DNS record: {fqdn} -> {ip}")
                return True
            else:
                logger.error(f"Failed to add record {fqdn}: {data.get('errorMessage', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error adding record {fqdn}: {e}")
            return False

    def configure_forwarders(self, forwarders: List[str]) -> bool:
        """Configure upstream DNS forwarders"""
        if not self.token:
            return False

        try:
            response = requests.get(
                f"{self.base_url}/api/settings/set",
                params={
                    "token": self.token,
                    "forwarders": ",".join(forwarders)
                },
                timeout=10
            )
            data = response.json()
            if data.get("status") == "ok":
                logger.info(f"Configured DNS forwarders: {', '.join(forwarders)}")
                return True
            else:
                logger.error(f"Failed to set forwarders: {data.get('errorMessage', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error setting forwarders: {e}")
            return False


def main():
    """Main execution flow"""
    logger.info("=" * 70)
    logger.info("Homelab DNS and IPAM Setup")
    logger.info("=" * 70)

    # Step 1: Pull data from Unifi
    logger.info("\n[1/5] Pulling device data from Unifi Controller...")
    unifi = UnifiController(UNIFI_URL, UNIFI_API_KEY)
    clients = unifi.get_clients()

    if not clients:
        logger.warning("No clients retrieved from Unifi. Continuing with setup anyway...")
    else:
        # Export to CSV
        csv_file = "/tmp/unifi-clients.csv"
        unifi.export_to_csv(clients, csv_file)
        logger.info(f"Exported client list to: {csv_file}")

    # Step 2: Setup Netbox
    logger.info("\n[2/5] Configuring Netbox IPAM...")
    netbox = NetboxClient(NETBOX_URL, token=NETBOX_TOKEN, username=NETBOX_USER, password=NETBOX_PASS)

    if not netbox.login():
        logger.error("Failed to authenticate with Netbox. Exiting.")
        sys.exit(1)

    # Create site
    site_id = netbox.create_site(SITE_NAME, SITE_SLUG)
    if not site_id:
        logger.error("Failed to create site. Exiting.")
        sys.exit(1)

    # Create prefix
    prefix_id = netbox.create_prefix(PREFIX_NETWORK, site_id)
    if not prefix_id:
        logger.error("Failed to create prefix. Exiting.")
        sys.exit(1)

    # Import IPs from Unifi
    logger.info("\n[3/5] Importing IP addresses to Netbox...")
    success_count = 0
    for client in clients:
        ip = client.get("ip")
        hostname = client.get("hostname") or client.get("name") or "unknown"
        mac = client.get("mac", "")

        if ip and hostname != "unknown":
            description = f"MAC: {mac}"
            if netbox.create_ip_address(ip, hostname, description):
                success_count += 1

    logger.info(f"Imported {success_count}/{len(clients)} IP addresses to Netbox")

    # Step 3: Configure DNS
    logger.info("\n[4/5] Configuring Technitium DNS...")
    dns = TechnitiumDNS(DNS_URL, DNS_USER, DNS_PASS)

    if not dns.login():
        logger.error("Failed to authenticate with DNS server. Exiting.")
        sys.exit(1)

    # Create zone
    if not dns.create_zone(DNS_ZONE):
        logger.error("Failed to create DNS zone. Exiting.")
        sys.exit(1)

    # Configure forwarders
    dns.configure_forwarders(DNS_UPSTREAM)

    # Add DNS records
    logger.info(f"Adding DNS records to zone {DNS_ZONE}...")
    dns_success = 0
    for client in clients:
        ip = client.get("ip")
        hostname = client.get("hostname") or client.get("name")

        if ip and hostname and hostname != "unknown":
            if dns.add_record(DNS_ZONE, hostname, ip):
                dns_success += 1

    logger.info(f"Added {dns_success}/{len(clients)} DNS records")

    # Step 4: Display summary
    logger.info("\n[5/5] Setup Complete!")
    logger.info("=" * 70)
    logger.info("Summary:")
    logger.info(f"  - Netbox:     http://10.203.3.202:8080 (admin/changeme)")
    logger.info(f"  - DNS:        http://10.203.3.203:5380 (admin/changeme)")
    logger.info(f"  - Zone:       {DNS_ZONE}")
    logger.info(f"  - IPs added:  {success_count}")
    logger.info(f"  - DNS records: {dns_success}")
    logger.info("")
    logger.info("Next Steps:")
    logger.info("  1. Create Netbox API token:")
    logger.info("     - Login to Netbox")
    logger.info("     - Go to Admin > API Tokens")
    logger.info("     - Create token, copy it")
    logger.info("")
    logger.info("  2. Save token to vault:")
    logger.info("     vault_netbox_api_token: '<your-token>'")
    logger.info("")
    logger.info("  3. Enable sync in rawls.yml:")
    logger.info("     sync_run_initial: true")
    logger.info("")
    logger.info("  4. Configure Unifi DHCP to use DNS server 10.203.3.203")
    logger.info("")
    logger.info("  5. Test DNS resolution:")
    logger.info(f"     dig @10.203.3.203 <hostname>.{DNS_ZONE}")
    logger.info("=" * 70)

    # Save Netbox token for reference
    logger.info(f"\nNetbox API Token (save this): {netbox.token}")


if __name__ == "__main__":
    main()
