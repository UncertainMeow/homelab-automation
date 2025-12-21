# DNS and IPAM Stack

Integrated DNS server (Technitium) and IPAM (Netbox) with automated synchronization.

## Architecture

```
Unifi Controller (10.203.3.1)
     |
     | API Pull
     v
[setup-dns-ipam.py] -----> Netbox IPAM (10.203.3.202:8080)
     |                           |
     |                           | API Sync (automated)
     v                           v
Technitium DNS (10.203.3.203:5380)
     |
     | DNS Resolution (port 53)
     v
Network Clients
```

## Components

### Technitium DNS Server
- **IP**: 10.203.3.203
- **Web UI**: http://10.203.3.203:5380
- **DNS Port**: 53 (UDP/TCP)
- **Zone**: hq.doofus.co
- **Forwarders**: 1.1.1.1, 8.8.8.8

### Netbox IPAM
- **IP**: 10.203.3.202
- **Web UI**: http://10.203.3.202:8080
- **Site**: HQ
- **Prefix**: 10.203.3.0/24

### Sync Service
- **Location**: Runs inside Netbox container
- **Frequency**: Every 15 minutes (systemd timer)
- **Script**: `/opt/netbox-dns-sync/sync-netbox-to-dns.py`
- **Direction**: Netbox → DNS (one-way sync)

## Quick Start

### Initial Setup

Run the setup script to populate both services from Unifi:

```bash
cd /Users/kellen/_Noetica/myt/_code/homelab-automation/services/dns-stack
./setup-dns-ipam.py
```

This will:
1. Pull all clients from Unifi Controller
2. Create site and prefix in Netbox
3. Import all IP addresses with hostnames to Netbox
4. Create DNS zone in Technitium
5. Add all A records to DNS

### Enable Automatic Sync

After initial setup, enable sync to keep DNS updated from Netbox:

1. **Create Netbox API Token**:
   - Login to Netbox: http://10.203.3.202:8080
   - Navigate to: Admin → API Tokens
   - Click "Add Token"
   - User: admin
   - Copy the generated token

2. **Save Token to Vault**:
   ```yaml
   # ansible/group_vars/all/vault.yml
   vault_netbox_api_token: "your-token-here"
   ```

3. **Enable Sync in Host Vars**:
   ```yaml
   # ansible/host_vars/rawls.yml
   sync_run_initial: true
   sync_enable_timer: true
   ```

4. **Deploy Sync Service**:
   ```bash
   cd /Users/kellen/_Noetica/myt/_code/homelab-automation
   ansible-playbook -i ansible/inventory.yml ansible/proxmox-config.yml \
     --tags netbox-dns-sync \
     --limit rawls
   ```

## Configuration

### DNS Credentials
- Username: `admin`
- Password: `changeme` (override with `vault_dns_admin_password`)

### Netbox Credentials
- Username: `admin`
- Password: `changeme` (override with `vault_netbox_superuser_password`)

### Unifi API
- Base URL: `https://10.203.3.1/proxy/network/api/`
- API Key: Configured in `setup-dns-ipam.py`

## Usage

### Add New Host

**Option 1: Via Netbox (Recommended)**
1. Login to Netbox
2. Go to IPAM → IP Addresses → Add
3. Enter IP address with /24 CIDR
4. Set DNS Name (hostname only, no domain)
5. Save
6. Wait up to 15 minutes for automatic sync, or run sync manually

**Option 2: Via DNS (Manual)**
1. Login to Technitium DNS
2. Go to Zones → hq.doofus.co
3. Click "Add Record"
4. Type: A
5. Name: hostname
6. IPv4 Address: IP
7. TTL: 3600
8. Save

### Manual Sync

To trigger sync immediately (from Proxmox host):

```bash
pct exec 202 -- /opt/netbox-dns-sync/sync-netbox-to-dns.py
```

### View Sync Logs

```bash
# Enter Netbox container
pct enter 202

# View logs
journalctl -u netbox-dns-sync -f

# Or check log file
tail -f /var/log/netbox-dns-sync.log
```

### Check Sync Timer Status

```bash
pct exec 202 -- systemctl status netbox-dns-sync.timer
```

## Testing

### Test DNS Resolution

From any network host:

```bash
# Test specific host
dig @10.203.3.203 socrates.hq.doofus.co

# Test from local machine
nslookup socrates.hq.doofus.co 10.203.3.203
```

### Verify DNS Records

1. Login to Technitium: http://10.203.3.203:5380
2. Go to Zones → hq.doofus.co
3. View all A records

### Verify Netbox Data

1. Login to Netbox: http://10.203.3.202:8080
2. Go to IPAM → IP Addresses
3. Filter by Status: Active
4. Verify DNS names are populated

## Configure Network Clients

### Option 1: Configure Unifi DHCP (Recommended)

1. Login to Unifi Controller: https://10.203.3.1
2. Navigate to: Settings → Networks → LAN
3. Under DHCP Name Server, set:
   - DNS Server 1: `10.203.3.203`
   - DNS Server 2: `1.1.1.1` (fallback)
4. Save

All DHCP clients will now use the internal DNS server.

### Option 2: Manual Client Configuration

For static hosts, manually configure DNS:

**Linux/macOS**:
```bash
# Edit /etc/resolv.conf
nameserver 10.203.3.203
nameserver 1.1.1.1
```

**Windows**:
1. Network Settings → Change Adapter Options
2. Right-click adapter → Properties
3. Internet Protocol Version 4 → Properties
4. Use the following DNS server addresses:
   - Preferred: `10.203.3.203`
   - Alternate: `1.1.1.1`

## Maintenance

### Backup DNS Configuration

DNS data is stored in the container at `/opt/technitium-dns/data`.

Backup via Proxmox:

```bash
# Create snapshot
pct snapshot 203 dns-backup-$(date +%Y%m%d)

# Or backup data directory
pct exec 203 -- tar czf /tmp/dns-backup.tar.gz /opt/technitium-dns/data
pct pull 203 /tmp/dns-backup.tar.gz ./dns-backup-$(date +%Y%m%d).tar.gz
```

### Backup Netbox Database

Netbox uses PostgreSQL in Docker:

```bash
# Enter Netbox container
pct enter 202

# Backup database
docker exec netbox-postgres pg_dump -U netbox netbox > /tmp/netbox-backup.sql

# Exit and pull backup
exit
pct pull 202 /tmp/netbox-backup.sql ./netbox-backup-$(date +%Y%m%d).sql
```

### Update DNS Records in Bulk

Use the Technitium API or web UI for bulk operations.

For scripted updates, see `/opt/netbox-dns-sync/sync-netbox-to-dns.py` as a reference.

### Re-sync from Unifi

To refresh all data from Unifi:

```bash
./setup-dns-ipam.py
```

This is idempotent and will update existing records.

## Troubleshooting

### DNS Not Resolving

1. **Check DNS service is running**:
   ```bash
   pct exec 203 -- docker ps
   ```

2. **Check DNS is listening**:
   ```bash
   pct exec 203 -- netstat -tulpn | grep :53
   ```

3. **Test DNS directly**:
   ```bash
   dig @10.203.3.203 google.com
   ```

4. **Check DNS logs**:
   ```bash
   pct exec 203 -- docker logs technitium-dns
   ```

### Sync Not Working

1. **Verify API token is set**:
   ```bash
   # Check if token is configured
   pct exec 202 -- grep NETBOX_TOKEN /opt/netbox-dns-sync/sync-netbox-to-dns.py
   ```

2. **Run sync manually to see errors**:
   ```bash
   pct exec 202 -- /opt/netbox-dns-sync/sync-netbox-to-dns.py
   ```

3. **Check timer is enabled**:
   ```bash
   pct exec 202 -- systemctl list-timers
   ```

### Netbox Web UI Not Accessible

1. **Check container is running**:
   ```bash
   pct status 202
   ```

2. **Check Netbox services**:
   ```bash
   pct exec 202 -- docker-compose -f /opt/netbox/docker-compose.yml ps
   ```

3. **View Netbox logs**:
   ```bash
   pct exec 202 -- docker logs netbox
   ```

## API Reference

### Unifi Controller API

```bash
# Get all clients
curl -k -H "X-API-KEY: $API_KEY" \
  https://10.203.3.1/proxy/network/api/s/default/stat/sta
```

### Netbox API

```bash
# Get IP addresses
curl -H "Authorization: Token $TOKEN" \
  http://10.203.3.202:8080/api/ipam/ip-addresses/

# Create IP address
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"address":"10.203.3.50/24","dns_name":"test","status":"active"}' \
  http://10.203.3.202:8080/api/ipam/ip-addresses/
```

### Technitium DNS API

```bash
# Login
curl "http://10.203.3.203:5380/api/user/login?user=admin&pass=changeme"

# Add DNS record
curl "http://10.203.3.203:5380/api/zones/records/add?token=$TOKEN&zone=hq.doofus.co&domain=test.hq.doofus.co&type=A&ipAddress=10.203.3.50"
```

## Files

- `setup-dns-ipam.py` - Initial setup script (this directory)
- `/opt/netbox-dns-sync/sync-netbox-to-dns.py` - Sync script (inside Netbox container)
- `/etc/systemd/system/netbox-dns-sync.service` - Systemd service (inside Netbox container)
- `/etc/systemd/system/netbox-dns-sync.timer` - Systemd timer (inside Netbox container)
- `/var/log/netbox-dns-sync.log` - Sync log file (inside Netbox container)

## Related Documentation

- Technitium DNS: https://technitium.com/dns/
- Netbox: https://docs.netbox.dev/
- Unifi API: https://ubntwiki.com/products/software/unifi-controller/api
