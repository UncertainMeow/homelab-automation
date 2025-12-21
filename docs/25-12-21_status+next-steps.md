# Project Status & Next Steps

**Date**: 2025-12-21
**Repository**: homelab-automation
**Branch**: main

---

## Current State

**homelab-automation** is a comprehensive infrastructure-as-code repository for a Proxmox-based homelab with 7 hosts across 3 physical clusters:

| Cluster | Hosts | Purpose |
|---------|-------|---------|
| AI Workstation | socrates | GPU workloads (2x Tesla P40) |
| MS-01 Cluster | frege, russell, wittgenstein | HA compute cluster (Thunderbolt ring) |
| Infrastructure | rawls, zeno, plato | Services, media, backups |

### Ansible Roles (21 total)

**Infrastructure Foundation**:
- proxmox-base, user-management, proxmox-community-scripts
- proxmox-pci-passthrough, proxmox-cluster, thunderbolt-ring
- nfs-storage, proxmox-backup-client, proxmox-backup-server
- vm-templates, lxc-templates, dotfiles-portable, infra-snapshot

**AI/GPU Workloads**:
- proxmox-nvidia-gpu, nvidia-lxc-ai

**Services**:
- gitlab, netbox, netbox-dns-sync
- technitium-dns, docs-site, tailscale-subnet-router

### Service Stacks

| Stack | Purpose | Status |
|-------|---------|--------|
| `llm-stack` | Ollama + Open WebUI | Deployed on ai-gpu0 |
| `ai-stack` | Karakeep + Meilisearch | Deployed on ai-gpu1 |
| `dns-stack` | Technitium DNS + UniFi sync | Ready to deploy |
| `homepage-stack` | Dashboard for all services | Ready to deploy |
| `gitlab-stack` | GitLab container deployment | Deployed on rawls |

### Infrastructure Inventory

| Host | IP | Role | Status |
|------|-----|------|--------|
| socrates | 10.203.3.42 | AI Workstation (2x Tesla P40) | Configured |
| rawls | 10.203.3.47 | Infrastructure (GitLab, DNS, NetBox) | Configured |
| zeno | 10.203.3.49 | Media Server | In inventory |
| frege | 10.203.3.11 | MS-01 Cluster Node 1 (primary) | Ready |
| russell | 10.203.3.12 | MS-01 Cluster Node 2 | Ready |
| wittgenstein | 10.203.3.13 | MS-01 Cluster Node 3 | Ready |
| plato | 10.203.3.97 | Proxmox Backup Server | Ready |

---

## Latest Changes (2025-12-21)

### Commit: fa6b4c9

**GitLab Migration Planning**:
- Complete strategy to split monorepo into 4-5 functional GitLab repositories
- Migration checklist, summary, and structure diagrams
- GitLab access documentation (credentials secured)

**New Service Stacks**:
- `dns-stack`: Technitium DNS setup with UniFi sync scripts
- `homepage-stack`: Dashboard configuration for homelab services

**Configuration Updates**:
- Consolidated NFS storage to single share (frege.yml)
- Enabled NetBox DNS sync timer (rawls.yml)
- Added cluster playbooks (cluster-base-config.yml, cluster-post-install.yml)

**Housekeeping**:
- Added comprehensive .gitignore
- Removed .DS_Store from tracking
- Removed exposed credentials from documentation

---

## Major Milestones

| Milestone | Status |
|-----------|--------|
| Phase 1: Socrates (AI workstation) | Complete |
| Phase 2: Rawls (GitLab, DNS, NetBox) | Complete |
| Phase 3: MS-01 cluster roles | Complete |
| Phase 4: PBS backup roles | Complete |
| GitLab migration planning | Complete |
| **GitLab migration execution** | Ready to execute |
| Service deployment to production | Pending |
| Monitoring stack | Planned |

---

## Immediate Next Steps

### 1. Execute GitLab Migration (Optional)

If proceeding with repository split:

```bash
# Log into GitLab
open http://10.203.3.204

# Reset root password (from rawls)
ssh kellen@10.203.3.47
sudo pct exec 204 -- gitlab-rake "gitlab:password:reset[root]"

# Create homelab group and repositories
# Follow docs/gitlab-migration-plan.md
```

**Target Repositories**:
- `infrastructure-core` - Proxmox foundation (12 roles)
- `ai-infrastructure` - GPU/AI workloads (2 roles + stacks)
- `homelab-services` - Service deployments (6 roles)
- `backup-infrastructure` - PBS automation

### 2. Deploy Services

**DNS Stack**:
```bash
# Deploy Technitium DNS to rawls/dns container
ansible-playbook -i inventory-prod.ini site.yml --limit rawls --tags dns
```

**Homepage Dashboard**:
- Deploy to a container on rawls or socrates
- Configure with services/homepage-stack/

**NetBox-DNS Sync**:
- Create API tokens in NetBox and Technitium
- Configure sync timer

### 3. MS-01 Cluster Setup

```bash
# Base configuration on fresh MS-01 nodes
ansible-playbook -i inventory-prod.ini ansible/cluster-base-config.yml

# Post-install configuration
ansible-playbook -i inventory-prod.ini ansible/cluster-post-install.yml

# Initialize cluster on frege (primary)
# Join russell and wittgenstein
```

### 4. Future Enhancements

- vLLM tensor parallelism on ai-unified (dual GPU)
- Monitoring stack (Prometheus + Grafana or Netdata)
- CI/CD pipelines for playbook testing
- Dynamic inventory from NetBox

---

## Quick Reference

### Service URLs

| Service | URL | Host |
|---------|-----|------|
| Ollama API | http://10.203.3.184:11434 | ai-gpu0 |
| Open WebUI | http://10.203.3.184:8080 | ai-gpu0 |
| Karakeep | http://10.203.3.153:3000 | ai-gpu1 |
| GitLab | http://10.203.3.204 | rawls/gitlab |
| Technitium DNS | http://10.203.3.203:5380 | rawls/dns |
| NetBox | http://10.203.3.202:8080 | rawls/netbox |

### Key Commands

```bash
# Full playbook on specific host
ansible-playbook -i inventory-prod.ini site.yml --limit socrates

# Check connectivity
ansible -i inventory-prod.ini all -m ping

# SSH to hosts
ssh kellen@10.203.3.42  # socrates
ssh kellen@10.203.3.47  # rawls

# Enter containers (from Proxmox host)
sudo pct enter 204  # gitlab
sudo pct enter 203  # dns
sudo pct enter 202  # netbox
```

### Key Documentation

- `docs/gitlab-migration-plan.md` - Complete migration strategy
- `docs/MIGRATION-CHECKLIST.md` - Task-by-task checklist
- `docs/repository-structure.md` - Visual diagrams
- `TODO.md` - Project roadmap and session log

---

## Repository Structure

```
homelab-automation/
├── ansible/
│   ├── roles/              # 21 Ansible roles
│   ├── host_vars/          # Per-host configuration
│   ├── group_vars/         # Common settings
│   ├── inventory-prod.ini  # Infrastructure inventory
│   ├── site.yml            # Main playbook
│   ├── cluster-base-config.yml
│   └── cluster-post-install.yml
├── services/
│   ├── ai-stack/           # Karakeep + Meilisearch
│   ├── llm-stack/          # Ollama + Open WebUI
│   ├── dns-stack/          # Technitium + UniFi sync
│   ├── homepage-stack/     # Dashboard
│   ├── gitlab-stack/       # GitLab compose
│   └── netbox-stack/       # NetBox IPAM
├── docs/                   # Documentation
├── mkdocs.yml              # Documentation site config
├── TODO.md                 # Project tracking
├── README.md
└── CLAUDE.md               # AI assistant instructions
```
