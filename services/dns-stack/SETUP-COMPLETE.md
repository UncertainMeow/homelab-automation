# DNS and IPAM Setup - Completion Report

**Date**: December 13, 2025
**Status**: ✅ Complete and Operational

## Summary

Successfully configured integrated DNS and IPAM infrastructure with automated synchronization.

### Components Deployed

1. **Technitium DNS Server**
   - Container: LXC 203 (10.203.3.203)
   - Zone: hq.doofus.co
   - Records: 23 A records imported
   - Forwarders: 1.1.1.1, 8.8.8.8
   - Web UI: http://10.203.3.203:5380

2. **Netbox IPAM**
   - Container: LXC 202 (10.203.3.202)
   - Site: HQ created
   - Prefix: 10.203.3.0/24 configured
   - IPs: 23 addresses with DNS names
   - Web UI: http://10.203.3.202:8080

3. **Automated Sync**
   - Service: netbox-dns-sync.timer
   - Frequency: Every 5 minutes
   - Direction: Netbox → DNS (one-way)
   - Status: Active and running

### Data Imported

From Unifi Controller (API):
- Total clients detected: 32
- Clients with hostnames: 23
- Export saved to: `/tmp/unifi-clients.csv`

Imported to Netbox:
- IP addresses: 23
- DNS names populated: 23
- MAC addresses captured in descriptions

Synced to DNS:
- A records created: 23
- Zone: hq.doofus.co
- TTL: 3600 seconds

### Test Results

DNS resolution tested successfully:

```bash
$ dig @10.203.3.203 socrates.hq.doofus.co +short
10.203.3.42

$ dig @10.203.3.203 rawls.hq.doofus.co +short
10.203.3.47

$ dig @10.203.3.203 google.com +short
142.250.176.206
```

✅ Internal DNS resolution: Working
✅ External DNS forwarding: Working
✅ Automatic sync: Working (next run in 5 minutes)

## Access Information

### Netbox
- **URL**: http://10.203.3.202:8080
- **Username**: admin
- **Password**: changeme
- **API Token**: `0123456789abcdef0123456789abcdef01234567`

### Technitium DNS
- **URL**: http://10.203.3.203:5380
- **Username**: admin
- **Password**: changeme
- **Zone**: hq.doofus.co

### Unifi Controller
- **URL**: https://10.203.3.1
- **API Key**: Configured in setup script

## Configuration Files

Created/Updated:
- `/Users/kellen/_Noetica/myt/_code/homelab-automation/services/dns-stack/setup-dns-ipam.py`
- `/Users/kellen/_Noetica/myt/_code/homelab-automation/services/dns-stack/README.md`
- `/Users/kellen/_Noetica/myt/_code/homelab-automation/ansible/group_vars/all/vault.yml`
- `/Users/kellen/_Noetica/myt/_code/homelab-automation/ansible/host_vars/rawls.yml` (updated)

Inside Netbox Container (LXC 202):
- `/opt/netbox-dns-sync/sync-netbox-to-dns.py`
- `/etc/systemd/system/netbox-dns-sync.service`
- `/etc/systemd/system/netbox-dns-sync.timer`
- `/var/log/netbox-dns-sync.log`

## Next Steps

### 1. Configure Unifi to Use DNS (Critical)

To enable all DHCP clients to use the new DNS server:

1. Login to Unifi Controller: https://10.203.3.1
2. Navigate to: **Settings** → **Networks** → **LAN**
3. Scroll to **DHCP Name Server**
4. Select: **Manual**
5. Set DNS Server 1: `10.203.3.203`
6. Set DNS Server 2: `1.1.1.1` (fallback)
7. Click **Apply Changes**

All DHCP clients will receive the new DNS server on their next DHCP renewal (typically within hours, or immediately after reconnecting).

### 2. Add Static DNS Records

To manually add hosts to DNS:

**Option A: Via Netbox (Recommended)**
1. Login to Netbox: http://10.203.3.202:8080
2. Go to **IPAM** → **IP Addresses** → **Add**
3. Enter:
   - Address: `10.203.3.X/24`
   - DNS Name: `hostname` (without domain)
   - Status: Active
4. Save
5. Wait up to 5 minutes for automatic sync

**Option B: Via DNS Web UI**
1. Login to Technitium: http://10.203.3.203:5380
2. Go to **Zones** → **hq.doofus.co**
3. Click **Add Record**
4. Select **A Record**
5. Enter hostname and IP
6. Save

### 3. Monitor Sync Status

Check sync is running:
```bash
# On Proxmox host (rawls)
pct exec 202 -- systemctl status netbox-dns-sync.timer

# View sync logs
pct exec 202 -- journalctl -u netbox-dns-sync -f

# Or check log file
pct exec 202 -- tail -f /var/log/netbox-dns-sync.log
```

### 4. Test DNS from Clients

Once Unifi DHCP is configured, test from any network client:

```bash
# Test internal resolution
dig socrates.hq.doofus.co

# Test external resolution
dig google.com

# Check which DNS server you're using
cat /etc/resolv.conf  # Linux/Mac
ipconfig /all         # Windows
```

### 5. Security (Optional but Recommended)

Encrypt the vault file:
```bash
cd /Users/kellen/_Noetica/myt/_code/homelab-automation
ansible-vault encrypt ansible/group_vars/all/vault.yml
```

Change default passwords:
- Netbox: Admin → Users → admin → Change password
- DNS: Settings → Change admin password
- Update vault.yml with new passwords

## Sample DNS Records Created

```
wittgenstein.hq.doofus.co    → 10.203.3.13
kellen-noetica.hq.doofus.co  → 10.203.1.165
frege.hq.doofus.co           → 10.203.3.11
plato.hq.doofus.co           → 10.203.3.97
rawls.hq.doofus.co           → 10.203.3.47
socrates.hq.doofus.co        → 10.203.3.42
ai-gpu0.hq.doofus.co         → 10.203.3.184
dockge.hq.doofus.co          → 10.203.3.200
russell.hq.doofus.co         → 10.203.3.12
idrac.hq.doofus.co           → 10.203.3.8
zeno.hq.doofus.co            → 10.203.3.49
tsb-rawls.hq.doofus.co       → 10.203.3.141
```

And 11 more records for IoT/wireless devices.

## Maintenance

### Update from Unifi

To refresh all data from Unifi:
```bash
cd /Users/kellen/_Noetica/myt/_code/homelab-automation/services/dns-stack
source venv/bin/activate
python3 setup-dns-ipam.py
```

This will:
- Pull latest client list from Unifi
- Update existing records in Netbox
- Create new records for new devices
- Sync changes to DNS

### Manual Sync Trigger

To force an immediate sync:
```bash
# On Proxmox host
pct exec 202 -- /opt/netbox-dns-sync/sync-netbox-to-dns.py

# Or via SSH
ssh ansible@10.203.3.47 'sudo pct exec 202 -- /opt/netbox-dns-sync/sync-netbox-to-dns.py'
```

### View Sync History

```bash
pct exec 202 -- journalctl -u netbox-dns-sync --since "1 hour ago"
```

### Backup

DNS data is in: `pct:/203/opt/technitium-dns/data/`
Netbox data is in: PostgreSQL in container 202

To backup:
```bash
# Snapshot both containers
pct snapshot 202 netbox-backup-$(date +%Y%m%d)
pct snapshot 203 dns-backup-$(date +%Y%m%d)
```

## Troubleshooting

### DNS Not Resolving

1. Check DNS service: `pct exec 203 -- docker ps`
2. Test DNS directly: `dig @10.203.3.203 google.com`
3. Check firewall: Port 53 UDP/TCP must be open
4. Verify zone exists: Login to DNS web UI

### Sync Not Working

1. Check timer: `pct exec 202 -- systemctl status netbox-dns-sync.timer`
2. Check logs: `pct exec 202 -- journalctl -u netbox-dns-sync -n 50`
3. Test manually: `pct exec 202 -- /opt/netbox-dns-sync/sync-netbox-to-dns.py`
4. Verify API token in: `/opt/netbox-dns-sync/sync-netbox-to-dns.py`

### Netbox Not Accessible

1. Check container: `pct status 202`
2. Check services: `pct exec 202 -- docker-compose -f /opt/netbox/docker-compose.yml ps`
3. View logs: `pct exec 202 -- docker logs netbox`

## Documentation

Full documentation available at:
- `/Users/kellen/_Noetica/myt/_code/homelab-automation/services/dns-stack/README.md`
- Netbox docs: https://docs.netbox.dev/
- Technitium docs: https://technitium.com/dns/

## Notes

- Sync runs every 5 minutes via systemd timer
- DNS zone is Primary (not Secondary or Forwarder)
- All changes should be made in Netbox for consistency
- Direct DNS changes will be overwritten by sync
- Export file refreshed on each setup script run

---

**Setup completed successfully!** 🎉

Your homelab now has production-ready DNS and IPAM with automatic synchronization.
