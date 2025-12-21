# Unifi DHCP DNS Configuration

**Critical Step**: Configure Unifi to distribute the new DNS server to all DHCP clients.

## Quick Steps

1. **Login**: https://10.203.3.1
2. **Navigate**: Settings → Networks → LAN
3. **Find**: DHCP Name Server section
4. **Change**:
   - Mode: Manual
   - DNS Server 1: `10.203.3.203`
   - DNS Server 2: `1.1.1.1`
5. **Apply**: Click "Apply Changes"

## Detailed Instructions

### Via Web UI

1. Open Unifi Controller: https://10.203.3.1
2. Login with your credentials
3. Click **Settings** (gear icon in bottom left)
4. Select **Networks** from the left menu
5. Click on your **LAN** network (typically "Default")
6. Scroll down to **DHCP**
7. Find **DHCP Name Server** section
8. Change from "Auto" to **Manual**
9. Enter:
   ```
   DNS Server 1: 10.203.3.203
   DNS Server 2: 1.1.1.1
   ```
10. Click **Apply Changes** button
11. Wait for changes to propagate (1-2 minutes)

### Via API (Alternative)

If you prefer API configuration:

```bash
curl -k -X PUT \
  -H "X-API-KEY: KdUEfY_59qUUkMjPyZsJtIpNIeYVfjhA" \
  -H "Content-Type: application/json" \
  -d '{
    "dhcp_dns_1": "10.203.3.203",
    "dhcp_dns_2": "1.1.1.1",
    "dhcp_dns_enabled": true
  }' \
  https://10.203.3.1/proxy/network/api/s/default/rest/networkconf/<network_id>
```

(Replace `<network_id>` with your LAN network ID)

## Verification

### Check DHCP Server Configuration

1. In Unifi UI, go to Settings → Networks → LAN
2. Verify DNS servers show:
   - Primary: 10.203.3.203
   - Secondary: 1.1.1.1

### Test from Clients

**New DHCP Leases**:
New devices connecting will immediately receive the DNS server.

**Existing Clients**:
Existing clients will update on next DHCP renewal:
- Typical renewal: 4-24 hours
- Force renewal:
  - **Windows**: `ipconfig /release && ipconfig /renew`
  - **macOS**: System Preferences → Network → Advanced → TCP/IP → Renew DHCP Lease
  - **Linux**: `sudo dhclient -r && sudo dhclient`
  - **iOS/Android**: Disconnect and reconnect to WiFi

**Check DNS Assignment**:

Linux/macOS:
```bash
cat /etc/resolv.conf
# Should show: nameserver 10.203.3.203
```

Windows:
```powershell
ipconfig /all
# Look for "DNS Servers" - should list 10.203.3.203
```

**Test Resolution**:
```bash
# Test internal DNS
nslookup socrates.hq.doofus.co

# Should return: 10.203.3.42
```

## Static IP Devices

For devices with static IP configuration (servers, network equipment):

### Linux (Debian/Ubuntu)
Edit `/etc/resolv.conf` or `/etc/netplan/01-netcfg.yaml`:
```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses: [10.203.3.X/24]
      gateway4: 10.203.3.1
      nameservers:
        addresses: [10.203.3.203, 1.1.1.1]
```

### Proxmox
Edit `/etc/network/interfaces`:
```
iface vmbr0 inet static
    address 10.203.3.X/24
    gateway 10.203.3.1
    dns-nameservers 10.203.3.203 1.1.1.1
```

Then: `systemctl restart networking`

### Windows Server
1. Network Adapters → Properties → TCP/IPv4
2. Use the following DNS server addresses:
   - Preferred: `10.203.3.203`
   - Alternate: `1.1.1.1`

### Network Equipment (Switches, APs)
Configure via device management interface:
- Primary DNS: 10.203.3.203
- Secondary DNS: 1.1.1.1

## Rollback

If you need to revert to previous DNS configuration:

1. Unifi UI: Settings → Networks → LAN
2. DHCP Name Server: Change back to **Auto**
3. Or set to your previous DNS servers
4. Apply Changes

## Monitoring

### Check DHCP Leases
In Unifi UI: Insights → Active Clients
- Click on any client
- Look for "IP Configuration" → DNS servers
- Should show 10.203.3.203

### DNS Query Logs
View DNS usage in Technitium:
1. http://10.203.3.203:5380
2. Dashboard → Query Logs
3. Monitor for queries from your network

## Troubleshooting

### DNS Not Working After Configuration

1. **Verify Unifi Config**: Check Settings → Networks → LAN
2. **Force DHCP Renew**: On client device, release and renew
3. **Check DNS Service**: `dig @10.203.3.203 google.com`
4. **Firewall**: Ensure port 53 UDP/TCP is allowed from LAN
5. **Test Directly**: `dig @10.203.3.203 socrates.hq.doofus.co`

### Some Clients Not Using New DNS

- **Wait**: DHCP lease must expire (up to 24 hours)
- **Manual**: Force DHCP renewal on each client
- **Reboot**: Restart client devices
- **Static**: Check static IP devices are manually configured

### DNS Queries Failing

1. Check DNS container: `pct status 203`
2. Check Docker: `pct exec 203 -- docker ps`
3. View logs: `pct exec 203 -- docker logs technitium-dns`
4. Test forwarders: Ensure 1.1.1.1 and 8.8.8.8 are reachable

## Network Segmentation

If you have multiple networks/VLANs in Unifi:

1. Repeat configuration for each network:
   - Settings → Networks → [Network Name]
   - Set DNS to 10.203.3.203
2. Ensure firewall rules allow DNS queries from all VLANs to 10.203.3.0/24

## Advanced Options

### Custom DNS Suffixes
In Unifi, you can also set domain search suffix:
- Settings → Networks → LAN
- DHCP → Domain Name: `hq.doofus.co`

This allows clients to resolve short names (e.g., `socrates` instead of `socrates.hq.doofus.co`)

### DNS Over HTTPS/TLS
Technitium supports DoH/DoT. To enable:
1. http://10.203.3.203:5380
2. Settings → DNS Server
3. Enable DNS-over-HTTPS
4. Configure certificate (Let's Encrypt or self-signed)

---

**Important**: After configuring Unifi DHCP, it may take several hours for all clients to receive the new DNS server. Be patient or manually renew DHCP on critical devices.
