# MS-01 Cluster Setup Guide

This guide covers setting up a 3-node Proxmox VE high-availability cluster using Minisforum MS-01 mini PCs with Thunderbolt ring networking and NFS shared storage.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MS-01 Cluster                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐     Thunderbolt     ┌─────────┐                  │
│   │  Frege  │◄───────────────────►│ Russell │                  │
│   │ (node1) │     ~25 Gbps        │ (node2) │                  │
│   └────┬────┘                     └────┬────┘                  │
│        │                               │                        │
│        │ Thunderbolt                   │ Thunderbolt            │
│        │ ~25 Gbps                      │ ~25 Gbps               │
│        │                               │                        │
│        └───────────┐     ┌─────────────┘                        │
│                    ▼     ▼                                      │
│               ┌─────────────┐                                   │
│               │Wittgenstein │                                   │
│               │  (node3)    │                                   │
│               └─────────────┘                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Management Network (1 Gbps)
                              │ 10.203.3.x
                              ▼
                    ┌─────────────────┐
                    │   stuffs NAS    │
                    │  10.203.3.99    │
                    │   (NFS)         │
                    └─────────────────┘
```

## Cluster Nodes

| Node | Hostname | IP | Role | Thunderbolt ID |
|------|----------|-----|------|----------------|
| 1 | frege | 10.203.3.11 | Primary | 1 |
| 2 | russell | 10.203.3.12 | Member | 2 |
| 3 | wittgenstein | 10.203.3.13 | Member | 3 |

## Prerequisites

1. **Hardware**
   - 3x Minisforum MS-01 with Proxmox VE installed
   - 3x Thunderbolt 4 cables (for ring topology)
   - Network connectivity to all nodes (management LAN)

2. **Software**
   - Proxmox VE 8.x installed on all nodes
   - SSH access configured (ansible user with key auth)

3. **NAS**
   - stuffs NAS (10.203.3.99) with NFS exports configured:
     - `/volume1/proxmox/vms` - VM disk storage
     - `/volume1/proxmox/isos` - ISO and template storage
     - `/volume1/proxmox/backups` - Backup storage

## Deployment Phases

### Phase 1: Base Configuration

Configures base system, users, and essential tools on all nodes.

```bash
cd ansible
ansible-playbook -i inventory-prod.ini cluster-setup.yml --tags phase1
```

**What it does:**
- Configures base Proxmox settings
- Creates users (kellen, ansible)
- Installs community scripts
- Deploys dotfiles

### Phase 2: Thunderbolt Networking

Configures high-speed Thunderbolt ring network between nodes.

**Before running:**
1. Connect Thunderbolt cables in ring topology:
   - Cable 1: Frege ↔ Russell
   - Cable 2: Russell ↔ Wittgenstein
   - Cable 3: Wittgenstein ↔ Frege

```bash
ansible-playbook -i inventory-prod.ini cluster-setup.yml --tags phase2
```

**What it does:**
- Loads thunderbolt kernel modules
- Configures network interfaces (en05, en06)
- Sets up IRQ affinity for performance
- Installs diagnostic tools (lldpd, iperf3)

**After running:**
- Reboot all nodes
- Verify links: `lldpctl`
- Test bandwidth: `iperf3 -c 169.254.1.X`

### Phase 3: Cluster Formation

Creates the Proxmox cluster and joins all nodes.

```bash
ansible-playbook -i inventory-prod.ini cluster-setup.yml --tags phase3
```

**What it does:**
- Creates cluster on frege (primary)
- Joins russell and wittgenstein (members)
- Waits between joins for stability

**Verify:**
```bash
pvecm status
pvecm nodes
```

### Phase 4: NFS Storage

Adds NFS shared storage for VM high availability.

```bash
ansible-playbook -i inventory-prod.ini cluster-setup.yml --tags phase4
```

**What it does:**
- Installs NFS client packages
- Configures Proxmox storage from stuffs NAS
- Verifies storage accessibility

**Verify:**
```bash
pvesm status
```

### Full Deployment

Run all phases in sequence:

```bash
ansible-playbook -i inventory-prod.ini cluster-setup.yml
```

## Post-Deployment Steps

### 1. Configure HA

In Proxmox web UI (any node):

1. Go to **Datacenter → HA → Groups**
2. Create group: `ms01-cluster` with all nodes
3. Set priorities if desired (frege=100, russell=50, wittgenstein=50)

### 2. Create Test VM

1. Create VM on `nfs-vms` storage
2. Go to **Datacenter → HA → Resources**
3. Add the VM with group `ms01-cluster`
4. Set max_restart and max_relocate values

### 3. Test Failover

1. Note which node the test VM is running on
2. Shutdown that node: `shutdown -h now`
3. Verify VM restarts on another node (may take 1-2 minutes)

## Troubleshooting

### Cluster Issues

```bash
# Check cluster status
pvecm status

# Check corosync
corosync-quorumtool -s

# View corosync logs
journalctl -u corosync

# Force expected votes (dangerous!)
pvecm expected 1
```

### Thunderbolt Issues

```bash
# Check if modules loaded
lsmod | grep thunderbolt

# Check interface status
ip addr show en05 en06

# View link status
lldpctl

# Test bandwidth
iperf3 -s  # On one node
iperf3 -c 169.254.1.X  # From another
```

### NFS Issues

```bash
# Check mounts
mount | grep nfs

# Test NFS server
showmount -e 10.203.3.99

# Check storage in Proxmox
pvesm status
pvesm list nfs-vms
```

## Network Details

### Management Network
- Subnet: 10.203.3.0/24
- Gateway: 10.203.3.1
- Used for: Web UI, SSH, general traffic

### Thunderbolt Ring Network
- Subnet: 169.254.1.0/24 (link-local)
- Used for: Cluster communication (corosync), future Ceph
- Speed: ~25 Gbps per link

### IP Addressing

| Host | Management IP | Thunderbolt IP |
|------|---------------|----------------|
| frege | 10.203.3.11 | 169.254.1.1 |
| russell | 10.203.3.12 | 169.254.1.2 |
| wittgenstein | 10.203.3.13 | 169.254.1.3 |

## Future Enhancements

### Adding Ceph Storage

When NVMe drives are added to the MS-01 nodes:

1. Create `ceph-cluster` role
2. Add OSD disks to each node
3. Configure Ceph pool for VMs
4. Enable live migration (currently HA failover only)

### Performance Tuning

- Consider dedicated NIC for management vs storage traffic
- Tune NFS mount options for workload
- Adjust corosync timing for faster failover

## Files Reference

| File | Description |
|------|-------------|
| `ansible/cluster-setup.yml` | Main cluster playbook |
| `ansible/host_vars/frege.yml` | Frege configuration |
| `ansible/host_vars/russell.yml` | Russell configuration |
| `ansible/host_vars/wittgenstein.yml` | Wittgenstein configuration |
| `ansible/roles/proxmox-cluster/` | Cluster formation role |
| `ansible/roles/nfs-storage/` | NFS storage role |
| `ansible/roles/thunderbolt-ring/` | Thunderbolt networking role |
