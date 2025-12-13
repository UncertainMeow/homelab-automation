# Agent Briefing: Proxmox Backup Server

## Mission

Deploy and configure Proxmox Backup Server (PBS) on a dedicated host to provide automated backups for all VMs and containers in the homelab.

## Business Outcomes (Success Criteria)

- [ ] PBS running and accessible at 10.203.3.97
- [ ] Socrates connected to PBS as a backup target
- [ ] Automated backup schedules for critical VMs/containers
- [ ] Retention policies defined (daily, weekly, monthly)
- [ ] Tested restore process (at least one test restore)
- [ ] Independent of main infrastructure - survives if Socrates fails
- [ ] Ansible-driven deployment where possible

## Network Topology

```
PBS Host: 10.203.3.97
Status: Needs fresh Proxmox Backup Server install

Backup Sources (Phase 1):
- Socrates (10.203.3.42): VMs and LXC containers
  - ai-gpu0 (VMID 201)
  - ai-gpu1 (VMID 202)
  - ai-unified (VMID 200)

Future Backup Sources:
- Rawls (10.203.3.47)
- Zeno (10.203.3.49)
- MS-01 Cluster (10.203.3.11-13)
```

## Reference Materials

### PBS Documentation
- Official: https://pbs.proxmox.com/docs/
- Installation: https://pbs.proxmox.com/docs/installation.html

### Existing Infrastructure Patterns
Location: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`

- `ansible/site.yml` - Main playbook structure
- `ansible/host_vars/socrates.yml` - Example host config
- `CLAUDE.md` - SSH keys and user standards

### Key Standards
- Primary user: `kellen` with full sudo, SSH-key only
- Automation user: `ansible` with passwordless sudo
- SSH keys:
  - cogito: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN7jefck23Q1wCFLAS3shg6uVpiOXKdVRPiPqRQc2gNz`
  - ergo-sum: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEIBPoFy/oe9j6lvXyVgnaPRb72EznbsuJQUDhQYxu2l`

## Constraints

1. **Fresh install needed**: PBS is not currently running
2. **Ansible-driven where possible**: Create role in `ansible/roles/proxmox-backup-server/`
3. **Feature branch**: Work in `feature/pbs-setup` branch
4. **Storage planning**: Determine disk layout for backup storage
5. **No hardcoded secrets**: Use variables for API tokens

## What NOT To Do

1. **Don't store backups on the same physical disks as production** - defeats the purpose
2. **Don't skip encryption** - backups should be encrypted at rest
3. **Don't forget to test restores** - untested backups aren't backups
4. **Don't over-complicate retention** - start simple (7 daily, 4 weekly, 3 monthly)

## Suggested Approach

1. **Phase 1: PBS Installation**
   - Install PBS on 10.203.3.97 (may need ISO boot)
   - Configure storage (datastore)
   - Set up admin user and API tokens
   - Document initial access

2. **Phase 2: Connect Socrates**
   - Add PBS as storage in Socrates Proxmox
   - Configure backup jobs for key VMs/containers
   - Set retention policy

3. **Phase 3: Automation**
   - Create Ansible role for PBS configuration
   - Automate backup job creation
   - Set up monitoring/alerts for backup failures

## Deliverables

1. `ansible/roles/proxmox-backup-server/` - PBS configuration role
2. `ansible/host_vars/pbs.yml` - PBS-specific configuration
3. Updated inventory to include PBS host
4. Documentation in `docs/pbs-setup.md`
5. Backup schedule documentation

## Storage Considerations

Questions to answer:
- What disks are available on 10.203.3.97?
- How much backup storage is needed? (Rule of thumb: 2-3x the data size)
- ZFS, ext4, or XFS for the datastore?
- Deduplication enabled? (saves space but uses CPU)

## Backup Strategy Suggestion

| What | Frequency | Retention | Priority |
|------|-----------|-----------|----------|
| AI containers (gpu0, gpu1) | Daily | 7 daily, 4 weekly | High |
| Config/small VMs | Daily | 7 daily, 4 weekly, 3 monthly | Medium |
| Large data VMs | Weekly | 4 weekly | Low |

## Communication

When complete, report back with:
1. PBS access URL and credentials location
2. Storage configuration (size, type)
3. Which VMs/containers are being backed up
4. Backup schedule
5. How to trigger manual backup
6. How to restore (tested!)
7. Any issues encountered
