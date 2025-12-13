# Ansible Roles Reference

This page documents all Ansible roles available in the homelab automation.

## Role Categories

### Base System Roles

| Role | Description |
|------|-------------|
| `proxmox-base` | Base Proxmox configuration: apt sources, updates, timezone |
| `user-management` | Creates admin and automation users with SSH keys |
| `proxmox-community-scripts` | Runs tteck community helper scripts |
| `dotfiles-portable` | Deploys portable shell configuration |
| `infra-snapshot` | Generates infrastructure documentation |

### Hardware Roles

| Role | Description |
|------|-------------|
| `proxmox-pci-passthrough` | Configures IOMMU and VFIO for device passthrough |
| `proxmox-nvidia-gpu` | Installs NVIDIA drivers, configures GPU for LXC access |
| `thunderbolt-ring` | Configures Thunderbolt networking for MS-01 cluster |

### Container Roles

| Role | Description |
|------|-------------|
| `lxc-templates` | Downloads LXC container templates |
| `vm-templates` | Creates cloud-init VM templates |
| `nvidia-lxc-ai` | Creates GPU-enabled LXC containers for AI workloads |

### Service Roles

| Role | Description |
|------|-------------|
| `gitlab` | Deploys GitLab CE in LXC container |
| `technitium-dns` | Deploys Technitium DNS server |
| `netbox` | Deploys Netbox IPAM/DCIM |
| `netbox-dns-sync` | Syncs Netbox IP data to DNS records |
| `docs-site` | Deploys this documentation site |

### Backup Roles

| Role | Description |
|------|-------------|
| `proxmox-backup-server` | Configures Proxmox Backup Server host |
| `proxmox-backup-client` | Configures backup jobs on Proxmox nodes |

### Cluster Roles

| Role | Description |
|------|-------------|
| `proxmox-cluster` | Creates/joins Proxmox HA cluster |
| `nfs-storage` | Configures NFS shared storage for cluster |

### Network Roles

| Role | Description |
|------|-------------|
| `tailscale-subnet-router` | Creates Tailscale subnet router for remote access |

---

## Using Roles

### Run Full Playbook

```bash
cd ansible
ansible-playbook -i inventory-prod.ini site.yml --limit <hostname>
```

### Run Specific Tags

Most roles have tags matching their name:

```bash
# Just user management
ansible-playbook -i inventory-prod.ini site.yml --limit socrates --tags users

# Just GPU setup
ansible-playbook -i inventory-prod.ini site.yml --limit socrates --tags nvidia

# Just dotfiles
ansible-playbook -i inventory-prod.ini site.yml --limit socrates --tags dotfiles
```

### Role Variables

Each role has a `defaults/main.yml` file with configurable variables. Host-specific overrides go in `host_vars/<hostname>.yml`.

Example from `host_vars/socrates.yml`:

```yaml
# Enable GPU-specific roles
enable_pci_passthrough: true
enable_nvidia_setup: true

# Container definitions
ai_containers:
  - name: ai-gpu0
    vmid: 201
    gpu_ids: [0]
```

---

## Adding New Roles

1. Create role structure:
   ```bash
   mkdir -p ansible/roles/my-role/{tasks,defaults,templates,handlers}
   ```

2. Add `tasks/main.yml` with the role logic

3. Add `defaults/main.yml` with default variables

4. Include in `site.yml` or create a dedicated playbook

5. Document the role in this file

---

## Role Dependencies

Some roles depend on others:

```
proxmox-nvidia-gpu
└── requires: proxmox-pci-passthrough

nvidia-lxc-ai
└── requires: proxmox-nvidia-gpu

netbox-dns-sync
└── requires: netbox, technitium-dns

proxmox-backup-client
└── requires: proxmox-backup-server (on PBS host)
```

The main `site.yml` playbook handles these dependencies through proper ordering.
