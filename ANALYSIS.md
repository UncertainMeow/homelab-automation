# Homelab Automation Analysis & Recommendations

**Date:** 2025-12-07
**Based on:** Personal setup documentation, InfraSnapshot concept, dotfiles, and Proxmox setup process

---

## 📋 Executive Summary

After analyzing your documentation, I've identified **8 key configurations** you perform on every Proxmox node, plus opportunities to integrate your dotfiles and infrastructure snapshot tooling into a comprehensive automation suite.

---

## 🎯 Your Actual Proxmox Setup Process

### From: `0-My_Proxmox_Setup_process.pdf`

**1. Post-Install Helper Scripts (Community Scripts)**
- Correct apt sources (remove enterprise, add no-subscription)
- Update all packages
- Kill subscription nag dialog
- Install processor microcode (Intel/AMD)
- Add Netdata monitoring agent
- Kernel cleanup

**2. IOMMU/PCI Passthrough Setup**
- Enable IOMMU in BIOS
- Detect boot manager (GRUB vs systemd-boot)
- Add kernel parameters (`intel_iommu=on iommu=pt`)
- Load VFIO modules for passthrough
- Update initramfs

**3. NVIDIA GPU Setup (if applicable)**
- Detect NVIDIA GPUs
- Install NVIDIA drivers on host
- Configure driver availability for LXC containers
- Add KVM options for better GPU compatibility
- Create test LXC to verify GPU passthrough works

**4. Additional Configuration** (implied from your environment)
- SSH key deployment
- Timezone configuration
- Essential package installation
- tmux/zsh setup for remote work

---

## 💡 Key Insights from Your Documentation

### From InfraSnapshot (1-InfraSnapshot)

You've built a **"Baseball Card"** system for documenting infrastructure:
- **Level 1 (Baseball Card)**: Quick facts for AI agents - status, IP, CPU, RAM, running services
- **Level 2 (Work Friend)**: Detailed troubleshooting info - logs, disk usage, performance metrics
- **Philosophy**: "Stop hand-waving, start snapshotting" - give AI accurate current state

**Recommendation**: Integrate snapshot generation into our playbooks as a **final validation step**

### From Your Dotfiles (2-MyDotfiles, 3-portable-dotfiles)

**Main Dotfiles Features:**
- Modular zsh config (aliases, functions, history, completion)
- Modern tools: eza, fzf, zoxide, powerlevel10k
- Ghostty + Alacritty terminal configs with Catppuccin Mocha theme
- tmux configuration optimized for SSH work
- OS-specific modules (macOS, Arch, NixOS, Bazzite)
- Environment launcher (Hammerspoon hotkeys for dev containers)
- Scripts library integration

**Portable Dotfiles:**
- Lightweight subset for SSH sessions
- Zero dependencies beyond zsh and git
- Essential aliases (ll, gs, gd, etc.)
- Core functions (mkcd, extract, ports, serve)
- One-liner curl install
- Perfect for LXC containers and remote Proxmox hosts

**Your Preferences:**
- Safety aliases (rm -i, cp -i, mv -i)
- Directory navigation shortcuts (.., ..., ll, la)
- Git workflow aliases (gs, gst, gco, gp, gl)
- Modern replacements over defaults
- Clean, modular structure
- Documentation-heavy approach

**Recommendation**: Add portable dotfiles deployment to Proxmox playbook, offer full dotfiles as optional

---

## 🔧 ProxMenuX Insights (A-ProxmenuXDocs)

ProxMenuX is a TUI (Terminal UI) menu system for Proxmox management. While interesting, it's:
- **Better for**: Interactive one-off tasks via menu navigation
- **Our approach is better for**: Repeatable, automated, infrastructure-as-code setups

**Useful ideas to steal:**
- Comprehensive checklist approach to setup
- LXC template downloads
- Backup configuration wizards
- Network testing utilities

**Verdict**: Not needed for our use case, but validates the importance of systematic Proxmox setup

---

## 📊 Recommended Playbook Structure

Based on your actual workflow, here's what we should build:

```
ansible/
├── proxmox-setup.yml                 # Main orchestration playbook
├── inventory.ini                     # Your Proxmox hosts
├── group_vars/
│   └── proxmox.yml                  # Common variables
├── host_vars/
│   ├── socrates.yml                 # Per-host configs (GPU settings, etc.)
│   └── rawls.yml
├── roles/
│   ├── common/                      # Base system setup
│   │   ├── tasks/main.yml
│   │   └── templates/
│   ├── proxmox-base/                # Proxmox-specific base config
│   │   ├── tasks/main.yml
│   │   ├── tasks/post-install.yml
│   │   ├── tasks/microcode.yml
│   │   ├── tasks/netdata.yml
│   │   └── tasks/kernel-clean.yml
│   ├── pci-passthrough/             # IOMMU/VFIO setup
│   │   ├── tasks/main.yml
│   │   ├── tasks/detect-bootmgr.yml
│   │   ├── tasks/grub.yml
│   │   ├── tasks/systemd-boot.yml
│   │   └── tasks/vfio-modules.yml
│   ├── nvidia-gpu/                  # NVIDIA driver setup
│   │   ├── tasks/main.yml
│   │   ├── tasks/detect-gpu.yml
│   │   ├── tasks/install-drivers.yml
│   │   ├── tasks/lxc-config.yml
│   │   └── tasks/test-lxc.yml
│   ├── dotfiles/                    # Dotfiles deployment
│   │   ├── tasks/main.yml
│   │   ├── tasks/portable.yml
│   │   └── tasks/full.yml
│   └── infra-snapshot/              # Baseball card generation
│       ├── tasks/main.yml
│       └── templates/
│           └── baseball-card.md.j2
└── README.md                        # Comprehensive documentation
```

---

## 🚀 Priority Implementation Order

### Phase 1: Core Proxmox Setup ✅ (Mostly Done)
- [x] Repository configuration
- [x] System updates
- [x] Essential packages
- [x] SSH hardening
- [x] Time sync
- [ ] **Add:** Community helper scripts integration
- [ ] **Add:** Netdata monitoring

### Phase 2: Hardware Optimization
- [ ] IOMMU/PCI passthrough detection and setup
- [ ] Boot manager detection (GRUB vs systemd-boot)
- [ ] VFIO module loading
- [ ] Kernel parameter configuration

### Phase 3: GPU Support (Conditional)
- [ ] Detect NVIDIA GPUs
- [ ] Install NVIDIA drivers
- [ ] Configure LXC GPU access
- [ ] Create test LXC container
- [ ] Validate GPU passthrough

### Phase 4: User Experience
- [ ] Deploy portable dotfiles to Proxmox root
- [ ] Optional: Full dotfiles for workstation-like nodes
- [ ] tmux configuration
- [ ] zsh as default shell (optional)

### Phase 5: Documentation & Validation
- [ ] Generate infrastructure snapshot (baseball card)
- [ ] Create AGENTS.md for AI context
- [ ] Validation tests
- [ ] Rollback procedures

---

## 🎨 Configuration Philosophy Alignment

Your documentation reveals these principles:

**1. "Stop Hand-Waving, Start Snapshotting"**
- Always capture actual state
- Give AI agents real data, not vague descriptions
- Automate documentation generation

**2. Modular & Maintainable**
- Separate concerns into logical units
- Easy to understand and modify
- Rich documentation

**3. Professional but Practical**
- Production-ready infrastructure
- Homelab flexibility
- No over-engineering

**4. Terminal-First Workflow**
- SSH-friendly configurations
- tmux for session persistence
- Modern CLI tools for productivity

**5. Safety & Reversibility**
- Always backup before changes
- Idempotent operations
- Easy rollback

---

## 📝 Specific Enhancements Needed

### 1. Community Scripts Integration

Add these tasks to the playbook:

```yaml
- name: Run pve-post-install script
  shell: bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/post-pve-install.sh)"
  args:
    creates: /var/log/pve-post-install.done

- name: Install microcode
  shell: bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/microcode.sh)"

- name: Install Netdata
  shell: bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/addon/netdata.sh)"
```

### 2. IOMMU/PCI Passthrough

Detect boot manager and configure appropriately:

```yaml
- name: Detect boot manager
  shell: efibootmgr -v
  register: efi_check
  failed_when: false
  changed_when: false

- name: Configure GRUB for IOMMU
  when: efi_check.rc != 0  # GRUB/BIOS
  lineinfile:
    path: /etc/default/grub
    regexp: '^GRUB_CMDLINE_LINUX_DEFAULT='
    line: 'GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"'
  notify: update-grub

- name: Configure systemd-boot for IOMMU
  when: efi_check.rc == 0 and 'systemd' in efi_check.stdout
  # Add kernel parameters to /etc/kernel/cmdline
```

### 3. NVIDIA GPU Support

Full role with detection, driver install, LXC config, and validation:

```yaml
- name: Detect NVIDIA GPUs
  shell: lspci | grep -i nvidia
  register: nvidia_check
  failed_when: false
  changed_when: false

- name: Install NVIDIA drivers
  when: nvidia_check.rc == 0
  # Follow Digital Spaceport guide
```

### 4. Portable Dotfiles Deployment

```yaml
- name: Deploy portable dotfiles to root
  shell: |
    curl -fsSL https://raw.githubusercontent.com/UncertainMeow/portable-dotfiles/main/bootstrap-portable.sh | bash
  args:
    creates: ~/.portable-dotfiles
```

### 5. Infrastructure Snapshot Generation

```yaml
- name: Generate baseball card snapshot
  template:
    src: baseball-card.md.j2
    dest: /root/infrastructure-snapshot.md
```

---

## 🎯 Variables You'll Need

Based on your setup:

```yaml
# group_vars/proxmox.yml
timezone: "America/New_York"
enable_netdata: true
enable_kernel_clean: true

# GPU hosts
nvidia_gpu_hosts:
  - socrates  # Dell R730 with 2x GPUs

# Dotfiles
deploy_portable_dotfiles: true
deploy_full_dotfiles: false  # Only on workstation-like nodes

# Monitoring
netdata_config: /etc/netdata/netdata.conf

# SSH keys
ssh_public_keys:
  - "{{ lookup('file', '~/.ssh/id_ed25519.pub') }}"
```

---

## 📚 Documentation Standards

Based on your preferences, all playbooks and roles should have:

1. **Inline comments** explaining WHY, not just WHAT
2. **README.md** in each role with:
   - Purpose and scope
   - Variables required
   - Example usage
   - Troubleshooting
3. **Tags** for selective execution
4. **Idempotency** - safe to run multiple times
5. **Validation tasks** after critical changes
6. **Baseball card generation** as final step

---

## 🔄 Workflow Integration

### Daily Use:
```bash
# Initial setup of new Proxmox node
ansible-playbook -i inventory.ini proxmox-setup.yml --limit new-node

# Update all nodes
ansible-playbook -i inventory.ini proxmox-setup.yml --tags updates

# Just GPU setup
ansible-playbook -i inventory.ini proxmox-setup.yml --tags nvidia --limit socrates

# Generate infrastructure snapshot
ansible-playbook -i inventory.ini infra-snapshot.yml
```

### After Changes:
```bash
# Regenerate baseball card
ansible-playbook -i inventory.ini infra-snapshot.yml

# Update AGENTS.md for AI context
cat snapshots/baseball-card-*.md >> ~/AGENTS.md
```

---

## ✅ Next Steps

1. **Implement Phase 2**: IOMMU/PCI passthrough role
2. **Implement Phase 3**: NVIDIA GPU detection and setup
3. **Implement Phase 4**: Dotfiles deployment
4. **Implement Phase 5**: Baseball card generation
5. **Testing**: Run on a test node before production
6. **Documentation**: Rich README for each component

---

## 🤝 Alignment with Your Philosophy

This approach matches your documented preferences:

✅ **Infrastructure as Code** - Everything automated and versioned
✅ **Modular Design** - Like your dotfiles structure
✅ **Rich Documentation** - README-first approach
✅ **AI-Friendly** - Baseball card snapshots for context
✅ **Production-Ready** - Professional but practical
✅ **Safety First** - Idempotent, reversible, validated
✅ **Terminal-Optimized** - SSH-friendly, tmux-ready

---

*This analysis is based on your actual setup process, not generic Proxmox best practices. Ready to build?*
