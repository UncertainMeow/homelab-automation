# Homelab Automation - Project Status & Roadmap

## Project Vision

Infrastructure-as-code for a Proxmox-based homelab with focus on:
- **AI/ML workloads** - GPU-accelerated LLM inference and AI applications
- **Reproducibility** - Any node can be rebuilt from scratch with Ansible
- **Security** - SSH-only access, proper user management, no root login
- **Automation** - One-command deployment, self-documenting infrastructure

---

## What We've Built

### Infrastructure

| Host | Hardware | Role | Status |
|------|----------|------|--------|
| **Socrates** | Dell R730, 2x Tesla P40 | AI Workstation | ✅ Configured |
| **Zeno** | Proxmox node | Media Server (*arr, Jellyfin, Usenet) | 📋 In inventory |
| **Rawls** | Proxmox node | Infra Node (GitLab, DNS, Authentik) | 📋 In inventory |
| **Frege** | MS-01 | HA Cluster Node | 📋 Future chapter |
| **Russell** | MS-01 | HA Cluster Node | 📋 Future chapter |
| **Wittgenstein** | MS-01 | HA Cluster Node | 📋 Future chapter |

### Ansible Roles (12 total)

| Role | Status | Description |
|------|--------|-------------|
| `proxmox-base` | ✅ Working | Base system config, updates, timezone |
| `user-management` | ✅ Working | kellen + ansible users, SSH hardening |
| `proxmox-community-scripts` | ✅ Working | tteck scripts, microcode updates |
| `proxmox-pci-passthrough` | ✅ Working | IOMMU, VFIO, kernel params |
| `proxmox-nvidia-gpu` | ✅ Working | NVIDIA drivers, CUDA, P40 tuning |
| `nvidia-lxc-ai` | ✅ Working | GPU-enabled LXC containers |
| `tailscale-subnet-router` | ✅ Working | Emergency network access beacons |
| `thunderbolt-ring` | 📋 Ready | MS-01 cluster networking |
| `vm-templates` | ✅ Working | Cloud-init VM templates |
| `lxc-templates` | ✅ Working | Download LXC templates |
| `dotfiles-portable` | ✅ Working | Shell customization |
| `infra-snapshot` | ✅ Working | Infrastructure documentation |

### Docker Service Stacks (created, not deployed)

| Stack | Container | Services | Status |
|-------|-----------|----------|--------|
| `llm-stack` | ai-gpu0 | Ollama, Open WebUI, Khoj | 📋 Created |
| `ai-stack` | ai-gpu1 | Karakeep, Meilisearch | 📋 Created |

### Security Posture

- ✅ SSH key-only authentication (cogito + ergo-sum)
- ✅ Root SSH disabled
- ✅ Passwordless sudo for kellen and ansible users
- ✅ Inventory uses `ansible_user=kellen` with become

---

## Lessons Learned

### Technical Discoveries

1. **Kernel Compatibility**: Proxmox VE 9's kernel 6.17 is incompatible with NVIDIA drivers. Must pin to kernel 6.14.x.

2. **Ansible Reserved Variables**: Never use `ansible_user` as a role variable - it shadows the connection variable. Use `automation_user` instead.

3. **Community Scripts**: Many tteck scripts use `whiptail` (interactive TUI). Set `enable_*: false` for those and run manually if needed.

4. **LXC GPU Passthrough**: Requires specific cgroup2 configuration and device major numbers (195, 509, 234 for NVIDIA).

5. **P40 Power Management**: Tesla P40s need persistence mode and power limit settings to perform well in a server environment.

### Process Lessons

1. **Monitor Long-Running Tasks**: Never wait more than 20 minutes for a playbook. Check progress every 2-3 minutes. (See CLAUDE.md)

2. **Test Users Before Lockdown**: Always verify SSH works as new users before disabling root.

3. **Incremental Deployment**: Run playbooks with `--limit` and `--tags` during development.

---

## Roadmap

### Phase 1: Socrates Completion (Current)

- [ ] **Deploy Docker stacks to AI containers**
  - [ ] SSH into ai-gpu0, deploy llm-stack
  - [ ] SSH into ai-gpu1, deploy ai-stack
  - [ ] Verify Ollama is GPU-accelerated
  - [ ] Pull initial models (llama3.2:3b, llava:7b)

- [ ] **Verify GPU containers**
  - [ ] Start ai-gpu0, verify GPU access with `nvidia-smi`
  - [ ] Start ai-unified, verify both GPUs accessible
  - [ ] Test exclusive GPU mode (only one container per GPU)

- [ ] **Model storage setup**
  - [ ] Create /srv/ai-models on Socrates
  - [ ] Mount to containers (defined in host_vars)

### Phase 2: Expand to Other Hosts

- [ ] **Configure Zeno**
  - [ ] Create ansible/host_vars/zeno.yml
  - [ ] Determine Zeno's role and hardware
  - [ ] Run playbook with `--limit zeno`

- [ ] **Configure Rawls**
  - [ ] Create ansible/host_vars/rawls.yml
  - [ ] Determine Rawls' role and hardware
  - [ ] Run playbook with `--limit rawls`

### Phase 3: Network & Services

- [ ] **DNS Configuration**
  - [ ] Set up Technitium DNS server
  - [ ] Create local domain (e.g., lab.local)
  - [ ] DNS records for all hosts and services

- [ ] **Reverse Proxy**
  - [ ] Traefik or Caddy for service routing
  - [ ] SSL certificates (Let's Encrypt or internal CA)
  - [ ] Expose services: Open WebUI, Khoj, Karakeep

- [ ] **Monitoring Stack**
  - [ ] Netdata or Prometheus + Grafana
  - [ ] GPU monitoring dashboards
  - [ ] Alert on container/service failures

### Phase 4: Advanced AI Setup

- [ ] **vLLM Tensor Parallelism**
  - [ ] Deploy vLLM to ai-unified (both GPUs)
  - [ ] Test 70B+ models with tensor_parallel_size=2
  - [ ] Benchmark throughput vs single-GPU

- [ ] **Model Management**
  - [ ] Centralized model storage strategy
  - [ ] Model download/caching automation
  - [ ] Version tracking for models

- [ ] **AI Application Integration**
  - [ ] Connect Khoj to document sources
  - [ ] Set up Karakeep for bookmarking
  - [ ] API access for external applications

### Phase 5: Hardening & Documentation

- [ ] **Backup Strategy**
  - [ ] PBS (Proxmox Backup Server) integration
  - [ ] Container snapshot automation
  - [ ] Offsite backup consideration

- [ ] **Security Audit**
  - [ ] Fail2ban on all hosts
  - [ ] Firewall rules review
  - [ ] Service access controls

- [ ] **Documentation**
  - [ ] Update README.md with complete setup guide
  - [ ] Network diagram
  - [ ] Runbook for common operations

---

## Future Chapters (Out of Scope - Current Module)

These are significant pieces of work that will be tackled separately:

### Chapter: HA Proxmox Cluster
- Take 3 fresh MS-01 Proxmox nodes
- Create high-availability Proxmox cluster
- Configure Thunderbolt ring for Ceph/cluster networking
- Shared storage across nodes

### Chapter: NAS Integration
- Add NAS to architecture and inventory
- Configure NFS shares
- Create shared storage pools in Proxmox
- Mount points for containers/VMs

### Chapter: Proxmox Backup Server
- Configure PBS instance (10.203.3.97)
- Fresh install setup
- Connect to relevant Proxmox nodes
- Backup schedules and retention policies

---

## Ideas & Future Possibilities

### Near-term
- **GPU Scheduling**: Script to switch between unified/split GPU modes
- **CI/CD**: GitHub Actions to lint and test playbooks

### Long-term
- **Kubernetes**: K3s cluster on MS-01 nodes for container orchestration
- **Multi-GPU Inference**: Explore Ray or other distributed frameworks
- **Home Assistant Integration**: Automation triggers based on AI inference

---

## Quick Reference

### Key Commands

```bash
# Full playbook on Socrates
cd ansible
ansible-playbook -i inventory-prod.ini site.yml --limit socrates

# Bootstrap NEW node (ansible user doesn't exist yet)
ansible-playbook -i inventory-prod.ini site.yml --limit <newhost> -e ansible_user=kellen --tags users

# Just user management
ansible-playbook -i inventory-prod.ini site.yml --limit socrates --tags users

# Check connectivity
ansible -i inventory-prod.ini all -m ping

# SSH to containers (from Socrates)
pct enter 200  # ai-unified
pct enter 201  # ai-gpu0
pct enter 202  # ai-gpu1
```

### Key Files

- `ansible/inventory-prod.ini` - Host inventory (gitignored)
- `ansible/group_vars/proxmox.yml` - Common settings for all hosts
- `ansible/host_vars/socrates.yml` - Socrates-specific config
- `services/llm-stack/` - Ollama + Open WebUI + Khoj
- `services/ai-stack/` - Karakeep + Meilisearch

### SSH Access

```bash
# As kellen (primary)
ssh kellen@10.203.3.42  # socrates
ssh kellen@10.203.3.49  # zeno
ssh kellen@10.203.3.47  # rawls

# Root is disabled - use sudo after login
```

---

## Uncommitted Changes

As of last session:
- `ansible/host_vars/socrates.yml` (modified)
- `ansible/roles/nvidia-lxc-ai/*` (modified)
- `ansible/roles/proxmox-nvidia-gpu/*` (modified)
- `ansible/roles/proxmox-pci-passthrough/*` (modified)
- `services/` (new directory, untracked)

**Action**: Review and commit these changes.

---

*Last updated: Session continuation*
