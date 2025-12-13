# DNS and Netbox IPAM Setup

This document describes the deployment and operation of Technitium DNS and Netbox IPAM on Rawls, with automatic synchronization from Netbox to DNS.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ Rawls (10.203.3.47) - Proxmox VE Host                                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ LXC 201 - Netbox (10.203.3.201)                                 │ │
│  │                                                                  │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │ │
│  │  │ Netbox :8080  │  │ PostgreSQL    │  │ Redis         │        │ │
│  │  │ (Docker)      │  │ (Docker)      │  │ (Docker)      │        │ │
│  │  └───────────────┘  └───────────────┘  └───────────────┘        │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐       │ │
│  │  │ Sync Script (systemd timer, every 5 min)             │       │ │
│  │  │ Reads IPs from Netbox → Creates DNS records          │       │ │
│  │  └──────────────────────────────────────────────────────┘       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                      │                                │
│                                      │ HTTP (port 5380)               │
│                                      ▼                                │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ LXC 203 - DNS (10.203.3.203)                                    │ │
│  │                                                                  │ │
│  │  ┌───────────────────────────────────────────────────────┐      │ │
│  │  │ Technitium DNS                                        │      │ │
│  │  │ - Port 53 (DNS)                                       │      │ │
│  │  │ - Port 5380 (Web UI + API)                            │      │ │
│  │  │ - Zone: hq.doofus.co                                     │      │ │
│  │  └───────────────────────────────────────────────────────┘      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Proxmox VE host (Rawls) with LXC support
- Debian 12 LXC template available: `local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst`
- Network connectivity on 10.203.3.0/24 subnet
- Ansible vault with secrets configured

## Deployment

### Quick Start

Deploy all infrastructure services to Rawls:

```bash
cd ansible
ansible-playbook -i inventory-prod.ini site.yml --limit rawls --tags infra-services
```

Or deploy components individually:

```bash
# DNS only
ansible-playbook -i inventory-prod.ini site.yml --limit rawls --tags dns

# Netbox only
ansible-playbook -i inventory-prod.ini site.yml --limit rawls --tags netbox

# Sync only (requires DNS and Netbox to exist)
ansible-playbook -i inventory-prod.ini site.yml --limit rawls --tags netbox-dns-sync
```

### Post-Deployment Steps

1. **Access Netbox**: http://10.203.3.201:8080
   - Login with admin credentials (from vault)
   - Create an API token: Admin → API Tokens

2. **Configure API Token for Sync**:
   ```bash
   # Add to ansible/group_vars/vault.yml
   vault_netbox_api_token: "your-token-here"
   ```

3. **Re-run sync role to enable automatic sync**:
   ```bash
   ansible-playbook -i inventory-prod.ini site.yml --limit rawls --tags netbox-dns-sync
   ```

4. **Access DNS Web UI**: http://10.203.3.203:5380
   - Login with admin credentials (from vault)
   - Verify `hq.doofus.co` zone exists

5. **Configure client DNS**:
   - Point devices to 10.203.3.203 as DNS server
   - Or configure your router/DHCP to distribute this DNS

## Services

### Technitium DNS (LXC 203)

| Property | Value |
|----------|-------|
| Container IP | 10.203.3.203 |
| DNS Port | 53 (UDP/TCP) |
| Web UI | http://10.203.3.203:5380 |
| Zone | hq.doofus.co |
| Data Directory | /opt/technitium-dns/data |

Access container:
```bash
pct enter 203
```

### Netbox IPAM (LXC 201)

| Property | Value |
|----------|-------|
| Container IP | 10.203.3.201 |
| Web UI | http://10.203.3.201:8080 |
| API | http://10.203.3.201:8080/api/ |
| Data Directory | /opt/netbox |

Access container:
```bash
pct enter 201
```

Docker services inside container:
- netbox (main application)
- netbox-worker (background jobs)
- netbox-housekeeping (maintenance)
- postgres (database)
- redis (cache and queue)
- redis-cache (caching layer)

## Synchronization

The sync runs inside the Netbox container and pushes DNS records to Technitium.

### How It Works

1. Sync script runs every 5 minutes via systemd timer
2. Queries Netbox API for all IP addresses with DNS names
3. Creates/updates A records in Technitium for `hq.doofus.co` zone
4. Logs to `/var/log/netbox-dns-sync.log`

### Manual Operations

From inside Netbox container (pct enter 201):

```bash
# Run sync manually
/opt/netbox-dns-sync/sync-netbox-to-dns.py

# Check timer status
systemctl status netbox-dns-sync.timer

# View recent logs
journalctl -u netbox-dns-sync -n 50

# Disable automatic sync
systemctl disable --now netbox-dns-sync.timer
```

### Adding New Hosts

1. In Netbox, create an IP address
2. Set the DNS Name field (e.g., `myhost` or `myhost.hq.doofus.co`)
3. Wait up to 5 minutes for sync, or run manually
4. Verify: `dig myhost.hq.doofus.co @10.203.3.203`

## Variables Reference

### DNS Variables (defaults in role)

| Variable | Default | Description |
|----------|---------|-------------|
| dns_vmid | 203 | LXC container VMID |
| dns_container_ip | 10.203.3.203 | Container IP address |
| dns_cores | 2 | CPU cores |
| dns_memory | 1024 | RAM in MB |
| dns_disk | 8G | Storage size |
| dns_domain | hq.doofus.co | DNS zone |
| dns_web_port | 5380 | Web UI port |

### Netbox Variables (defaults in role)

| Variable | Default | Description |
|----------|---------|-------------|
| netbox_vmid | 201 | LXC container VMID |
| netbox_container_ip | 10.203.3.201 | Container IP address |
| netbox_cores | 4 | CPU cores |
| netbox_memory | 4096 | RAM in MB |
| netbox_disk | 20G | Storage size |
| netbox_web_port | 8080 | Web UI port |

### Vault Variables (required)

```yaml
vault_dns_admin_password: "your-secure-password"
vault_netbox_db_password: "your-secure-password"
vault_netbox_redis_password: "your-secure-password"
vault_netbox_superuser_password: "your-secure-password"
vault_netbox_secret_key: "your-long-random-string"
vault_netbox_api_token: "your-api-token"  # Create after first login
```

## Troubleshooting

### DNS not resolving

1. Check Technitium is running:
   ```bash
   pct exec 203 -- docker ps
   ```

2. Test DNS directly:
   ```bash
   dig @10.203.3.203 hq.doofus.co SOA
   ```

3. Check zone exists in Technitium Web UI

### Sync not working

1. Check API token is set:
   ```bash
   pct exec 201 -- grep NETBOX_TOKEN /opt/netbox-dns-sync/sync-netbox-to-dns.py
   ```

2. Run sync manually and check errors:
   ```bash
   pct exec 201 -- /opt/netbox-dns-sync/sync-netbox-to-dns.py
   ```

3. Check DNS connectivity from Netbox container:
   ```bash
   pct exec 201 -- curl http://10.203.3.203:5380/
   ```

### Netbox slow to start

Netbox takes 2-3 minutes to fully initialize after container start. Check progress:
```bash
pct exec 201 -- docker logs -f netbox
```

## Security Notes

- DNS container binds to port 53 on container IP only
- Netbox API requires token authentication
- Sync credentials stored in templated script (readable by root only)
- Consider firewall rules to restrict access to management ports

## Related Documentation

- [Technitium DNS Server](https://technitium.com/dns/)
- [Netbox Documentation](https://docs.netbox.dev/)
- [Agent Briefing](../docs/agent-briefings/02-dns-netbox.md)
