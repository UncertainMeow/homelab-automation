# Proxmox Backup Server Setup

Centralized backup infrastructure for all Proxmox VE nodes using Proxmox Backup Server (PBS).

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │         Proxmox Backup Server               │
                    │         plato (10.203.3.97)                 │
                    │                                             │
                    │  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
                    │  │  infra  │ │   ai    │ │  media  │       │
                    │  │datastore│ │datastore│ │datastore│       │
                    │  └─────────┘ └─────────┘ └─────────┘       │
                    └─────────────────────────────────────────────┘
                                      ▲
                                      │ Backup traffic
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              ┌─────┴─────┐     ┌─────┴─────┐     ┌─────┴─────┐
              │ Socrates  │     │  Rawls    │     │   Zeno    │
              │10.203.3.42│     │10.203.3.47│     │10.203.3.49│
              │ AI VMs    │     │ Infra     │     │ Media     │
              └───────────┘     └───────────┘     └───────────┘
```

## Quick Start

### 1. Prerequisites

Before running the playbook:

- PBS must be installed on plato (10.203.3.97)
- Datastores must be created (via PBS web UI or CLI during installation)
- `ansible` user must exist with sudo access
- Network connectivity between PBS and PVE nodes

### 2. Run the Playbook

```bash
cd ansible/
ansible-playbook -i inventory-prod.ini pbs-setup.yml
```

### 3. Save the Token

When the playbook completes, it will display a token secret if one was created. **Save this immediately to 1Password**:

- Item name: `PBS API Token - plato`
- Fields:
  - Token ID: `pve-backup@pam!pve-token`
  - Secret: `<the generated secret>`
  - Fingerprint: `<from /root/pbs-fingerprint.txt>`

### 4. Connect PVE Nodes

On each Proxmox VE node that needs to backup to PBS:

```bash
# Set credentials (get from 1Password)
export PBS_SECRET='your-token-secret'
export PBS_HOST='10.203.3.97'

# Get fingerprint from PBS
FINGERPRINT=$(ssh root@$PBS_HOST cat /root/pbs-fingerprint.txt | grep -v "^#" | head -1)

# Add PBS storage
pvesh create /storage \
  --storage pbs-ai \
  --type pbs \
  --server $PBS_HOST \
  --datastore ai \
  --username 'pve-backup@pam!pve-token' \
  --password "$PBS_SECRET" \
  --fingerprint "$FINGERPRINT" \
  --content backup
```

### 5. Create Backup Jobs

Example for Socrates AI containers:

```bash
pvesh create /cluster/backup \
  --storage pbs-ai \
  --vmid 200,201,202 \
  --schedule "03:15" \
  --mode snapshot \
  --compress zstd \
  --enabled 1 \
  --comment "nightly-ai-containers"
```

## Datastores

| Datastore | Purpose | Priority | Retention |
|-----------|---------|----------|-----------|
| `infra` | Critical infrastructure (GitLab, DNS, NetBox) | High | 7d/4w/6m/1y |
| `ai` | AI containers from Socrates | High | 7d/4w/6m/1y |
| `media` | Media stack (Jellyfin, *arr) | Medium | 7d/4w/3m |

## Retention Policy

Default retention (configurable per datastore):

- **Daily**: 7 backups
- **Weekly**: 4 backups
- **Monthly**: 6 backups
- **Yearly**: 1 backup

## Maintenance Schedule

| Task | Schedule | Purpose |
|------|----------|---------|
| Prune | Daily | Remove old backups per retention policy |
| Verify (weekly) | Saturday 04:30 | Full backup verification |
| Verify (daily) | Daily | Incremental verification |
| Garbage Collection | Sunday 05:15 | Reclaim space from deleted chunks |
| ZFS Scrub | Sunday 02:30 | Filesystem integrity check |

## Backup Strategy

### Phase 1: Socrates (Current)

Priority targets:
- `ai-unified` (VMID 200) - Dual-GPU container, 48GB VRAM
- `ai-gpu0` (VMID 201) - GPU 0 container
- `ai-gpu1` (VMID 202) - GPU 1 container

Schedule: Daily at 03:15

### Phase 2: Infrastructure (Planned)

- GitLab (rawls)
- Technitium DNS (rawls)
- NetBox (rawls)

### Phase 3: Media & Cluster (Future)

- Media stack (zeno)
- MS-01 cluster nodes (frege, russell, wittgenstein)

## Restore Procedures

### Restore a VM

1. Open PBS Web UI: https://10.203.3.97:8007
2. Navigate to Datastore > Content
3. Select the backup to restore
4. Click "Restore" and choose target PVE node

### CLI Restore

```bash
# On the PVE node
proxmox-backup-client restore \
  host/ai-gpu0/2024-01-15T03:15:00Z \
  vm/201.conf \
  --repository pve-backup@pam@10.203.3.97:ai
```

### Test Restore (Recommended Monthly)

1. Restore to a test VM ID (e.g., 9999)
2. Boot and verify functionality
3. Delete test VM
4. Document test results

## Monitoring

### Check Backup Status

```bash
# On PBS
proxmox-backup-manager task list

# Check last backup times
proxmox-backup-manager backup list infra
```

### Email Notifications

Configure email notifications in PBS Web UI:
1. Datacenter > Options > Email from address
2. Configure SMTP server
3. Set notification recipient per datastore

## Troubleshooting

### Connection Failed

```bash
# Test connectivity
ping 10.203.3.97

# Test port
nc -zv 10.203.3.97 8007

# Check fingerprint
openssl s_client -connect 10.203.3.97:8007 </dev/null 2>/dev/null \
  | openssl x509 -fingerprint -noout -sha256
```

### Authentication Failed

1. Verify token exists on PBS:
   ```bash
   proxmox-backup-manager user list-tokens pve-backup@pam
   ```

2. Verify ACLs:
   ```bash
   proxmox-backup-manager acl list
   ```

3. Regenerate token if needed:
   ```bash
   proxmox-backup-manager user delete-token pve-backup@pam pve-token
   proxmox-backup-manager user generate-token pve-backup@pam pve-token
   # Save new secret to 1Password!
   ```

### Backup Failed - No Space

```bash
# Check datastore usage
proxmox-backup-manager datastore list

# Force garbage collection
proxmox-backup-manager garbage-collection start infra

# Check ZFS pool
zpool list
zfs list
```

## File Locations

On PBS host (plato):
- `/root/pbs-info.txt` - Configuration summary
- `/root/pbs-fingerprint.txt` - TLS fingerprint for PVE setup
- `/etc/proxmox-backup/` - PBS configuration

On PVE nodes:
- `/etc/pve/storage.cfg` - Storage configuration including PBS

## References

- [Proxmox Backup Server Documentation](https://pbs.proxmox.com/docs/)
- [PBS API Reference](https://pbs.proxmox.com/docs/api-viewer/)
- [Ansible Role: proxmox-backup-server](../ansible/roles/proxmox-backup-server/)
