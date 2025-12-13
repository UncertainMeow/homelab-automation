# Agent Briefing: DNS + Netbox on Rawls

## Mission

Deploy Technitium DNS server and Netbox IPAM on Rawls, with synchronization between them so that IP address management in Netbox automatically creates DNS records.

## Business Outcomes (Success Criteria)

- [ ] Stop typing IP addresses - use hostnames everywhere (`socrates.lab.local`, `gitlab.lab.local`, etc.)
- [ ] Netbox as single source of truth for IP allocations
- [ ] DNS records auto-generated from Netbox IPAM data
- [ ] All existing hosts documented in Netbox (Socrates, Rawls, Zeno, etc.)
- [ ] Bidirectional sync preferred; if too complex, Netbox → DNS one-way is acceptable
- [ ] Ansible-driven deployment (idempotent, reproducible)

## Network Topology

```
Host: Rawls (Proxmox node)
IP: 10.203.3.47

Services should run as LXC containers or Docker:
- Technitium DNS: Port 53 (DNS), 5380 (Web UI)
- Netbox: Port 8080 (Web UI)

Prior art locations:
- DNS was on rseau (10.203.3.3)
- Netbox was on rawls (10.203.3.201)

Consolidating both on Rawls makes sense for the "infra node" concept.
```

## Existing Infrastructure to Document

| Hostname | IP | Purpose |
|----------|-----|---------|
| socrates | 10.203.3.42 | AI Workstation (Dell R730, 2x P40) |
| rawls | 10.203.3.47 | Infra Node |
| zeno | 10.203.3.49 | Media Server |
| ai-gpu0 | 10.203.3.184 | GPU container on Socrates |
| ai-gpu1 | 10.203.3.153 | GPU container on Socrates |
| pbs | 10.203.3.97 | Proxmox Backup Server |
| frege | 10.203.3.11 | MS-01 Cluster Node |
| russell | 10.203.3.12 | MS-01 Cluster Node |
| wittgenstein | 10.203.3.13 | MS-01 Cluster Node |

## Reference Materials

### Prior Work (descartes-stack)
Location: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`

Relevant files:
- `dns-data/` - DNS zone configurations
- `docker-compose-dns-local.yml` - Technitium setup
- `ansible/playbooks/` - Deployment patterns
- `QUICKSTART-UDM-NETBOX.md` - Netbox integration notes

### Existing Infrastructure Patterns
Location: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`

- `ansible/site.yml` - Main playbook structure
- `ansible/roles/` - Role patterns to follow

## Constraints

1. **Ansible-driven**: Create roles in `ansible/roles/technitium-dns/` and `ansible/roles/netbox/`
2. **Idempotent**: Running the playbook twice should be safe
3. **Feature branch**: Work in `feature/dns-netbox` branch
4. **Domain**: Use `lab.local` as the internal domain
5. **No hardcoded secrets**: Use variables for admin passwords

## What NOT To Do

1. **Don't copy the Tailscale/Caddy reverse proxy setup** - research current Tailscale best practices (Tailscale Services, tsidp are new)
2. **Don't make DNS a single point of failure** - clients should fall back gracefully
3. **Don't over-complicate the sync** - start with one-way Netbox → DNS if bidirectional is too complex
4. **Don't forget to update client DNS settings** - document how to point hosts at new DNS

## Suggested Approach

1. **Phase 1: Technitium DNS**
   - Deploy Technitium as Docker container or LXC
   - Create `lab.local` zone
   - Add initial records manually
   - Test resolution

2. **Phase 2: Netbox**
   - Deploy Netbox as Docker container
   - Document existing infrastructure
   - Add IP prefixes and addresses

3. **Phase 3: Sync**
   - Research Netbox → DNS sync options
   - Could be: webhook, cron job, custom script, or plugin
   - Implement and test

## Deliverables

1. `ansible/roles/technitium-dns/` - DNS server role
2. `ansible/roles/netbox/` - IPAM role
3. `ansible/roles/netbox-dns-sync/` - Sync mechanism (if separate)
4. `services/dns-stack/` or `services/netbox-stack/` - Docker compose if using Docker
5. Documentation in `docs/dns-netbox-setup.md`
6. Initial Netbox data (can be YAML/JSON for import)

## Questions to Research

- Netbox + Technitium sync - any existing integrations?
- Technitium API for programmatic record management?
- Should DNS run on port 53 on Rawls, or use a dedicated IP?
- How to handle split-horizon DNS (if needed for remote access)?

## Communication

When complete, report back with:
1. DNS server URL and admin access
2. Netbox URL and admin access
3. How the sync works
4. How to add new hosts going forward
5. Any issues encountered
