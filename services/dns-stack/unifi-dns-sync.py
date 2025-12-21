#!/usr/bin/env python3
"""
UniFi to Technitium DNS Sync

Pulls client data from UniFi Controller and updates DNS A records.
Designed to run on a schedule via systemd timer.

Usage:
    ./unifi-dns-sync.py              # Normal sync
    ./unifi-dns-sync.py --dry-run    # Preview changes without applying
    ./unifi-dns-sync.py --verbose    # Verbose output
"""

import sys
import json
import re
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("ERROR: requests library required. Install with: pip3 install requests")
    sys.exit(1)

# =============================================================================
# Configuration - Update these values for your environment
# =============================================================================

UNIFI_URL = "https://10.203.3.1"
UNIFI_API_KEY = "KdUEfY_59qUUkMjPyZsJtIpNIeYVfjhA"

DNS_URL = "http://10.203.3.203:5380"
DNS_USER = "admin"
DNS_PASS = "2262-EatonGate"
DNS_ZONE = "hq.doofus.co"
DNS_TTL = 300  # 5 minutes - short TTL for dynamic clients

# Only sync clients from these networks (empty = all networks)
ALLOWED_NETWORKS = ["10.203."]

# Skip these hostnames (case-insensitive patterns)
SKIP_PATTERNS = [
    r"^unknown$",
    r"^$",
    r"^\d+\.\d+\.\d+\.\d+$",  # Skip if hostname is just an IP
]

# =============================================================================
# Classes
# =============================================================================

class UnifiClient:
    """Client for UniFi Controller API"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-KEY": api_key,
            "Accept": "application/json",
        }

    def get_clients(self) -> List[Dict]:
        """Get all active clients from UniFi"""
        try:
            response = requests.get(
                f"{self.base_url}/proxy/network/api/s/default/stat/sta",
                headers=self.headers,
                verify=False,
                timeout=15
            )
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logging.error(f"UniFi API error: {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"UniFi connection error: {e}")
            return []


class TechnitiumDNS:
    """Client for Technitium DNS API"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None

    def login(self) -> bool:
        """Authenticate and get session token"""
        try:
            response = requests.get(
                f"{self.base_url}/api/user/login",
                params={"user": self.username, "pass": self.password},
                timeout=10
            )
            data = response.json()
            if data.get("status") == "ok":
                self.token = data.get("token")
                return True
            logging.error(f"DNS login failed: {data.get('errorMessage')}")
            return False
        except Exception as e:
            logging.error(f"DNS connection error: {e}")
            return False

    def get_records(self, zone: str) -> Dict[str, str]:
        """Get all A records in zone as {hostname: ip}"""
        if not self.token:
            return {}
        try:
            response = requests.get(
                f"{self.base_url}/api/zones/records/get",
                params={"token": self.token, "zone": zone, "listZone": "true"},
                timeout=10
            )
            data = response.json()
            records = {}
            if data.get("status") == "ok":
                for record in data.get("response", {}).get("records", []):
                    if record.get("type") == "A":
                        # Extract hostname from FQDN
                        name = record.get("name", "")
                        if name.endswith(f".{zone}"):
                            name = name[:-len(f".{zone}")]
                        elif name == zone:
                            name = "@"
                        ip = record.get("rData", {}).get("ipAddress", "")
                        if name and ip:
                            records[name.lower()] = ip
            return records
        except Exception as e:
            logging.error(f"Error fetching DNS records: {e}")
            return {}

    def add_or_update_record(self, zone: str, hostname: str, ip: str, ttl: int = 300) -> bool:
        """Add or update an A record"""
        if not self.token:
            return False

        fqdn = f"{hostname}.{zone}"
        try:
            response = requests.get(
                f"{self.base_url}/api/zones/records/add",
                params={
                    "token": self.token,
                    "zone": zone,
                    "domain": fqdn,
                    "type": "A",
                    "ipAddress": ip,
                    "ttl": ttl,
                    "overwrite": "true"
                },
                timeout=10
            )
            data = response.json()
            return data.get("status") == "ok"
        except Exception as e:
            logging.error(f"Error adding record {hostname}: {e}")
            return False

    def delete_record(self, zone: str, hostname: str, ip: str) -> bool:
        """Delete an A record"""
        if not self.token:
            return False

        fqdn = f"{hostname}.{zone}"
        try:
            response = requests.get(
                f"{self.base_url}/api/zones/records/delete",
                params={
                    "token": self.token,
                    "zone": zone,
                    "domain": fqdn,
                    "type": "A",
                    "ipAddress": ip
                },
                timeout=10
            )
            data = response.json()
            return data.get("status") == "ok"
        except Exception as e:
            logging.error(f"Error deleting record {hostname}: {e}")
            return False


# =============================================================================
# Helper Functions
# =============================================================================

def sanitize_hostname(name: str) -> str:
    """Convert name to valid DNS hostname"""
    if not name:
        return ""
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[\s_]+', '-', name)
    # Remove invalid characters (keep only a-z, 0-9, hyphen)
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Collapse multiple hyphens
    name = re.sub(r'-+', '-', name)
    # Truncate to 63 chars (DNS label limit)
    return name[:63]


def should_skip(hostname: str) -> bool:
    """Check if hostname should be skipped"""
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, hostname, re.IGNORECASE):
            return True
    return False


def is_allowed_network(ip: str) -> bool:
    """Check if IP is in allowed networks"""
    if not ALLOWED_NETWORKS:
        return True
    return any(ip.startswith(net) for net in ALLOWED_NETWORKS)


# =============================================================================
# Main Sync Logic
# =============================================================================

def sync(dry_run: bool = False, verbose: bool = False) -> Tuple[int, int, int]:
    """
    Sync UniFi clients to DNS.
    Returns: (added, updated, errors)
    """
    added = updated = errors = 0

    # Connect to UniFi
    logging.info("Connecting to UniFi Controller...")
    unifi = UnifiClient(UNIFI_URL, UNIFI_API_KEY)
    clients = unifi.get_clients()

    if not clients:
        logging.warning("No clients retrieved from UniFi")
        return 0, 0, 1

    logging.info(f"Retrieved {len(clients)} clients from UniFi")

    # Connect to DNS
    logging.info("Connecting to Technitium DNS...")
    dns = TechnitiumDNS(DNS_URL, DNS_USER, DNS_PASS)
    if not dns.login():
        logging.error("Failed to authenticate with DNS server")
        return 0, 0, 1

    # Get existing records
    existing = dns.get_records(DNS_ZONE)
    logging.info(f"Found {len(existing)} existing A records in {DNS_ZONE}")

    # Process clients
    processed = set()
    for client in clients:
        ip = client.get("ip", "")

        # Get hostname (prefer hostname, fall back to name)
        hostname = client.get("hostname") or client.get("name") or ""
        hostname = sanitize_hostname(hostname)

        # Skip invalid entries
        if not ip or not hostname:
            continue
        if should_skip(hostname):
            continue
        if not is_allowed_network(ip):
            continue
        if hostname in processed:
            continue  # Skip duplicates

        processed.add(hostname)
        current_ip = existing.get(hostname.lower())

        if current_ip == ip:
            if verbose:
                logging.debug(f"  [unchanged] {hostname} -> {ip}")
            continue

        action = "update" if current_ip else "add"

        if dry_run:
            if current_ip:
                logging.info(f"  [DRY-RUN] Would update: {hostname} {current_ip} -> {ip}")
            else:
                logging.info(f"  [DRY-RUN] Would add: {hostname} -> {ip}")
        else:
            if dns.add_or_update_record(DNS_ZONE, hostname, ip, DNS_TTL):
                if current_ip:
                    logging.info(f"  [updated] {hostname}: {current_ip} -> {ip}")
                    updated += 1
                else:
                    logging.info(f"  [added] {hostname} -> {ip}")
                    added += 1
            else:
                logging.error(f"  [FAILED] {hostname} -> {ip}")
                errors += 1

    return added, updated, errors


def main():
    parser = argparse.ArgumentParser(description="Sync UniFi clients to DNS")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("=" * 60)
    logging.info("UniFi to DNS Sync")
    logging.info(f"Zone: {DNS_ZONE}")
    if args.dry_run:
        logging.info("MODE: DRY-RUN (no changes will be made)")
    logging.info("=" * 60)

    added, updated, errors = sync(dry_run=args.dry_run, verbose=args.verbose)

    logging.info("=" * 60)
    logging.info(f"Sync complete: {added} added, {updated} updated, {errors} errors")
    logging.info("=" * 60)

    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
