# Proxmox Community Scripts Role

Integrates the trusted [Proxmox VE Helper-Scripts](https://community-scripts.github.io/ProxmoxVE/) that you use in your setup process.

## What This Role Does

### Post-Install Script
- Corrects APT sources (removes enterprise, adds no-subscription)
- Disables subscription nag dialog
- Updates package lists
- Essential first step after fresh Proxmox install

### Processor Microcode
- Installs Intel or AMD microcode automatically
- Critical for CPU security patches and stability
- Detects CPU vendor and installs appropriate package

### Netdata Monitoring
- Installs Netdata monitoring agent
- Configured to listen on all interfaces (port 19999)
- Real-time performance metrics
- Web UI: `http://your-proxmox-ip:19999`

### Kernel Cleanup
- Removes old/unused kernels
- Frees up `/boot` space
- **Critical**: Has fixed boot issues in your setup before
- Keeps only current and previous kernel

### PVE Scripts Local
- Installs all community scripts locally
- No internet required after installation
- Available via `/usr/local/bin/pve-scripts`
- Useful for offline environments

### IP Tag (Optional)
- Adds IP address tag to Proxmox web UI
- Purely cosmetic but helpful for identification
- Shows IP next to node name in UI

## Variables

All features enabled by default (matching your workflow):

```yaml
enable_post_install: true
enable_microcode: true
enable_netdata: true
enable_kernel_clean: true
enable_pve_scripts_local: true
enable_iptag: true
```

## Usage

### In Playbook
```yaml
- hosts: proxmox
  roles:
    - proxmox-base
    - proxmox-community-scripts
```

### Disable Specific Scripts
```yaml
- hosts: proxmox
  roles:
    - role: proxmox-community-scripts
      vars:
        enable_iptag: false  # Skip cosmetic IP tag
```

### Tags
```bash
# Run all community scripts
ansible-playbook site.yml --tags community-scripts

# Only Netdata
ansible-playbook site.yml --tags community-scripts,netdata

# Only kernel cleanup
ansible-playbook site.yml --tags community-scripts,kernel-clean
```

## Post-Installation

### Access Netdata
```bash
# Open in browser
http://10.203.3.42:19999

# Or check status
systemctl status netdata
```

### Use Local Scripts
```bash
# List available scripts
pve-scripts

# Run specific script
pve-scripts <script-name>
```

### Verify Microcode
```bash
# Check if microcode is loaded
dmesg | grep microcode
```

## Order of Operations

Run after `proxmox-base`:

1. `proxmox-base`
2. `proxmox-community-scripts` ← **You are here**
3. Other roles...

## Idempotency

Safe to run multiple times:
- Post-install: Skips if already run
- Microcode: Only updates if needed
- Netdata: Only installs if not present
- Kernel cleanup: Removes only old kernels
- PVE Scripts: Only installs if not present

## Why These Scripts?

These are the **exact scripts from your PDF** setup process. Community-tested, maintained, and proven in production homelabs.

**Source**: https://github.com/community-scripts/ProxmoxVE

## Troubleshooting

**Netdata not accessible:**
```bash
# Check if running
systemctl status netdata

# Check port
netstat -tlnp | grep 19999

# Restart
systemctl restart netdata
```

**Kernel cleanup removed too much:**
```bash
# List kernels
dpkg --list | grep pve-kernel

# Should see current + previous kernel
# If issues, Proxmox includes recovery options in GRUB
```

**Scripts fail to download:**
```bash
# Check internet
ping github.com

# Check DNS
dig raw.githubusercontent.com

# Manual run
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/post-pve-install.sh)"
```
