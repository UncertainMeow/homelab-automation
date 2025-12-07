# Proxmox Homelab Automation

Complete infrastructure-as-code solution for Proxmox VE homelab deployment and management.

## 🎯 What This Does

Automates your entire Proxmox setup process from fresh install to production-ready:

- ✅ **Base System**: Repos, updates, essential packages, SSH hardening
- ✅ **Community Scripts**: Post-install, microcode, Netdata monitoring, kernel cleanup
- ✅ **GPU Support**: Auto-detects NVIDIA/AMD GPUs, configures PCI passthrough
- ✅ **Emergency Access**: Tailscale beacon for remote access when network fails
- ✅ **Templates**: VM templates (Debian, Omarchy) and LXC templates ready to deploy
- ✅ **Dotfiles**: Your portable terminal configuration on all nodes
- ✅ **Documentation**: Auto-generates infrastructure "baseball card" snapshots

## 🚀 Quick Start

### Prerequisites

```bash
# Install Ansible on your control machine
brew install ansible  # macOS
# or
apt install ansible   # Linux
```

### Initial Setup

```bash
# Clone this repository
git clone https://github.com/UncertainMeow/homelab-automation.git
cd homelab-automation/ansible

# Configure your inventory
cp inventory.ini inventory-prod.ini
vim inventory-prod.ini
# Add your Proxmox hosts

# Set your variables
vim group_vars/proxmox.yml
# Configure SSH keys, timezone, features

# (Optional) Set up Tailscale auth for emergency beacon
cp group_vars/vault.yml.example group_vars/vault.yml
vim group_vars/vault.yml
ansible-vault encrypt group_vars/vault.yml
```

### Deploy

```bash
# Test connection
ansible -i inventory-prod.ini proxmox -m ping

# Deploy to one node (recommended first time)
ansible-playbook -i inventory-prod.ini site.yml --limit new-node

# Deploy to all nodes
ansible-playbook -i inventory-prod.ini site.yml
```

## 📖 Documentation

- **[QUICK-START.md](docs/QUICK-START.md)** - Get running in 10 minutes
- **[TAILSCALE-AUTH-KEY-SETUP.md](docs/TAILSCALE-AUTH-KEY-SETUP.md)** - Emergency beacon configuration
- **[ROLES.md](docs/ROLES.md)** - Detailed role documentation
- **[USAGE-EXAMPLES.md](docs/USAGE-EXAMPLES.md)** - Common workflows and commands

## 🏗️ Architecture

```
ansible/
├── site.yml                   # Main orchestration playbook
├── inventory.ini             # Example inventory
├── group_vars/
│   ├── proxmox.yml          # Configuration variables
│   └── vault.yml.example    # Secrets template
├── roles/
│   ├── proxmox-base/                # Foundation setup
│   ├── proxmox-community-scripts/   # Helper scripts
│   ├── proxmox-pci-passthrough/     # GPU passthrough
│   ├── proxmox-nvidia-gpu/          # NVIDIA drivers
│   ├── tailscale-subnet-router/     # Emergency beacon
│   ├── vm-templates/                # VM template creation
│   ├── lxc-templates/               # LXC template management
│   ├── dotfiles-portable/           # Terminal configuration
│   └── infra-snapshot/              # Documentation generation
└── docs/                    # Comprehensive documentation
```

## 🎛️ Configuration

### Essential Variables

```yaml
# group_vars/proxmox.yml

# Security - Add your SSH keys!
ssh_public_keys:
  - "ssh-ed25519 AAAAC3... you@desktop"

# Time
timezone: "America/New_York"

# Features (enable as needed)
create_tailscale_router: false  # Emergency beacon
create_vm_templates: false      # VM templates
download_lxc_templates: false   # LXC templates
deploy_dotfiles: true           # Portable dotfiles
```

### Per-Host Customization

```yaml
# host_vars/socrates.yml
description: "Dell R730 with 2x NVIDIA GPUs"
# GPU auto-detected, drivers installed automatically
```

## 🏃 Common Workflows

### Fresh Proxmox Node

```bash
# Full setup
ansible-playbook -i inventory-prod.ini site.yml --limit new-node
```

### Update Existing Nodes

```bash
# Just updates
ansible-playbook -i inventory-prod.ini site.yml --tags updates

# Re-deploy dotfiles
ansible-playbook -i inventory-prod.ini site.yml --tags dotfiles
```

### GPU-Specific Configuration

```bash
# Setup GPU passthrough on specific host
ansible-playbook -i inventory-prod.ini site.yml \
  --tags gpu \
  --limit socrates
```

### Create Emergency Beacon

```bash
# Deploy Tailscale beacon
ansible-playbook -i inventory-prod.ini site.yml \
  --tags tailscale-router \
  --ask-vault-pass
```

### Generate Infrastructure Snapshot

```bash
# Create "baseball card" documentation
ansible-playbook -i inventory-prod.ini site.yml --tags snapshot
```

## 🔧 Roles Overview

| Role | Purpose | When to Use |
|------|---------|-------------|
| **proxmox-base** | Foundation setup | Always (runs first) |
| **proxmox-community-scripts** | Helper scripts, monitoring | Always |
| **proxmox-pci-passthrough** | GPU passthrough setup | Auto-detects GPUs |
| **proxmox-nvidia-gpu** | NVIDIA driver install | Auto-detects NVIDIA |
| **tailscale-subnet-router** | Emergency access beacon | Optional, highly recommended |
| **vm-templates** | Debian/Omarchy templates | Optional, useful |
| **lxc-templates** | LXC template downloads | Optional, useful |
| **dotfiles-portable** | Terminal improvements | Optional, recommended |
| **infra-snapshot** | Documentation generation | Optional, for AI context |

## 🎯 Execution Phases

The playbook runs in logical phases:

1. **Phase 1**: Foundation (base system)
2. **Phase 2**: Optimizations (community scripts)
3. **Phase 3**: Hardware support (GPU passthrough)
4. **Phase 4**: Networking (Tailscale beacon)
5. **Phase 5**: Templates (VMs and LXCs)
6. **Phase 6**: User experience (dotfiles)
7. **Phase 7**: Documentation (snapshots)

### Run Specific Phases

```bash
# Only Phase 1 and 2
ansible-playbook site.yml --tags phase1,phase2

# Only GPU setup (Phase 3)
ansible-playbook site.yml --tags phase3
```

## 🔒 Security Features

- **SSH key-only authentication** (no password login)
- **Encrypted secrets** (Ansible Vault for Tailscale keys)
- **Least-privilege Tailscale ACLs**
- **Optional fail2ban** for brute-force protection
- **Auto-updates** with controlled execution
- **Firewall-ready** (IP forwarding configured)

## 🚨 Emergency Access

The Tailscale beacon provides a failsafe when local network fails:

```bash
# From anywhere with internet
ssh root@tailscale-beacon

# Now access your Proxmox host
ssh root@10.203.3.42

# Your network is broken but you're back in!
```

See [TAILSCALE-AUTH-KEY-SETUP.md](docs/TAILSCALE-AUTH-KEY-SETUP.md) for complete setup.

## 🎓 Learning Resources

Each role has a comprehensive README:

```bash
# Read role documentation
cat roles/proxmox-base/README.md
cat roles/tailscale-subnet-router/README.md
# etc.
```

## 🐛 Troubleshooting

### SSH Connection Issues

```bash
# Test SSH manually
ssh root@10.203.3.42

# Test with Ansible
ansible -i inventory-prod.ini proxmox -m ping

# Check inventory
ansible-inventory -i inventory-prod.ini --list
```

### Playbook Fails

```bash
# Run with verbose output
ansible-playbook site.yml -vvv

# Check specific host
ansible-playbook site.yml --limit problematic-host
```

### GPU Not Detected

```bash
# Check GPU presence
ssh root@proxmox-host "lspci | grep -i nvidia"

# Force GPU setup
ansible-playbook site.yml --tags gpu --extra-vars "force_pci_passthrough=true"
```

### Vault Decryption Issues

```bash
# View vault contents
ansible-vault view group_vars/vault.yml

# Edit vault
ansible-vault edit group_vars/vault.yml

# Re-encrypt
ansible-vault rekey group_vars/vault.yml
```

## 📊 Post-Deployment

After successful deployment:

1. **Review info files**: `ssh root@host "cat /root/*-info.txt"`
2. **Access Netdata**: `http://your-host:19999`
3. **Check Proxmox web UI**: `https://your-host:8006`
4. **Test Tailscale beacon** (if enabled)
5. **Reboot if GPU passthrough** was configured

## 🔄 Maintenance

### Regular Tasks

```bash
# Update all nodes monthly
ansible-playbook site.yml --tags updates

# Regenerate snapshots
ansible-playbook site.yml --tags snapshot

# Rotate Tailscale keys quarterly
# See docs/TAILSCALE-AUTH-KEY-SETUP.md
```

### Adding New Nodes

```bash
# Add to inventory
vim inventory-prod.ini

# Deploy
ansible-playbook site.yml --limit new-node
```

## 🤝 Contributing

This is a personal homelab project, but improvements welcome:

1. Test changes on one node first
2. Document what and why
3. Update role README if behavior changes
4. Keep it simple and practical

## 📜 License

MIT License - Use freely, modify as needed.

## 🙏 Credits

- **Community Scripts**: [community-scripts/ProxmoxVE](https://github.com/community-scripts/ProxmoxVE)
- **Portable Dotfiles**: [UncertainMeow/portable-dotfiles](https://github.com/UncertainMeow/portable-dotfiles)
- **InfraSnapshot Concept**: Baseball card documentation for AI agents
- **Tailscale**: Emergency access solution

---

**Built for production homelab use. Deploy with confidence.** 🚀
