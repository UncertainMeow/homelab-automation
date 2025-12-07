# Proxmox Base Configuration Role

Core system setup for Proxmox VE hosts. This role handles the foundational configuration that every Proxmox node needs.

## What This Role Does

### Repository Management
- Removes enterprise repository (requires paid subscription)
- Adds no-subscription repository (free updates)
- Updates package cache

### System Updates
- Full dist-upgrade of all packages
- Auto-removal of unnecessary packages
- Can be disabled for controlled update windows

### Essential Packages
Installs must-have utilities:
- **Editors**: vim
- **Network**: curl, wget, net-tools, dnsutils
- **Monitoring**: htop, iotop, ncdu
- **Multiplexing**: tmux, screen
- **Infrastructure**: git, rsync, jq
- **Storage**: lvm2
- **Proxmox**: ifupdown2 (modern network config)

### Network Configuration
- Enables IPv4 forwarding (required for VMs/containers)
- Optional IPv6 forwarding
- Persistent across reboots

### Security Hardening
- SSH key-only authentication (disables password login)
- Deploys your SSH public keys
- Optional fail2ban installation
- Configures secure SSH defaults

### Time Synchronization
- Enables systemd-timesyncd
- Sets timezone
- Ensures accurate system time

### Quality of Life
- Custom MOTD showing host is Ansible-managed
- Consistent configuration across all nodes

## Variables

### Required
```yaml
ssh_public_keys:
  - "ssh-ed25519 AAAAC3... user@host"
```

### Optional
```yaml
# System updates
proxmox_run_updates: true          # Set false to skip updates

# Security
install_fail2ban: false             # Install brute-force protection
enable_ipv6: false                  # Enable IPv6 forwarding

# Time
timezone: "America/New_York"        # Your timezone
```

## Usage

### Include in Playbook
```yaml
- hosts: proxmox
  roles:
    - proxmox-base
```

### With Custom Variables
```yaml
- hosts: proxmox
  roles:
    - role: proxmox-base
      vars:
        install_fail2ban: true
        timezone: "America/Los_Angeles"
```

### Tags
```bash
# Full base setup
ansible-playbook site.yml --tags base

# Only repository configuration
ansible-playbook site.yml --tags base,repos

# Only updates
ansible-playbook site.yml --tags base,updates

# Only packages
ansible-playbook site.yml --tags base,packages

# Only security configuration
ansible-playbook site.yml --tags base,security
```

## Dependencies

None. This is the foundation role.

## Example Inventory

```ini
[proxmox]
socrates ansible_host=10.203.3.42
rawls ansible_host=10.203.3.47

[proxmox:vars]
ansible_user=root
ansible_python_interpreter=/usr/bin/python3
ssh_public_keys=["ssh-ed25519 AAAAC3... you@desktop"]
timezone=America/New_York
```

## Post-Installation

After this role runs, you'll have:
- ✅ Up-to-date Proxmox system
- ✅ Essential tools installed
- ✅ SSH key access configured
- ✅ Time synchronized
- ✅ Network forwarding enabled
- ✅ Secure defaults applied

## Troubleshooting

**SSH still asks for password:**
- Verify your SSH key is in `ssh_public_keys` variable
- Check `/root/.ssh/authorized_keys` on the host
- Ensure your private key is loaded: `ssh-add -l`

**Updates fail:**
- Check internet connectivity: `ping 1.1.1.1`
- Verify DNS: `dig debian.org`
- Try manually: `apt update && apt dist-upgrade`

**Time not syncing:**
- Check service status: `systemctl status systemd-timesyncd`
- Verify NTP servers: `timedatectl show-timesync`

## Order of Operations

This role should run **first** before other Proxmox configuration roles:

1. `proxmox-base` ← **You are here**
2. `proxmox-community-scripts`
3. `proxmox-pci-passthrough`
4. `proxmox-nvidia-gpu`
5. Other roles...

## Idempotency

Safe to run multiple times. All tasks are idempotent and won't cause issues on repeated execution.
