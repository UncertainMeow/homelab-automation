# GitLab Migration - Quick Reference

**Status**: Planning Complete - Ready to Execute
**Created**: 2025-12-13

---

## Overview

Migration from monorepo to 4-5 functional repositories on local GitLab instance.

**GitLab**: http://10.203.3.204
**Root Password**: See `gitlab-access.md`

---

## Proposed Repository Structure

```
homelab/ (GitLab group)
├── infrastructure-core      # Proxmox base, cluster, hardware
├── ai-infrastructure        # NVIDIA GPU, AI containers, LLM stacks
├── homelab-services        # GitLab, DNS, NetBox, Tailscale
├── backup-infrastructure   # Proxmox Backup Server
└── homelab-docs           # Documentation site (optional)
```

---

## Repository Contents Summary

### 1. infrastructure-core

**Purpose**: Foundation Proxmox automation

**Roles**: proxmox-base, user-management, proxmox-community-scripts, proxmox-pci-passthrough, proxmox-cluster, thunderbolt-ring, nfs-storage, proxmox-backup-client, vm-templates, lxc-templates, dotfiles-portable, infra-snapshot

**Playbooks**: cluster-setup.yml, cluster-base-config.yml, cluster-post-install.yml, pve-backup-setup.yml

**Inventory**: Full cluster (zeno, rawls, socrates, MS-01 cluster, plato)

### 2. ai-infrastructure

**Purpose**: GPU & AI workloads

**Roles**: proxmox-nvidia-gpu, nvidia-lxc-ai

**Services**: ai-stack/, llm-stack/

**Host**: socrates (2x Tesla P40)

### 3. homelab-services

**Purpose**: Service deployments

**Roles**: gitlab, netbox, netbox-dns-sync, technitium-dns, docs-site, tailscale-subnet-router

**Services**: gitlab-stack/, dns-stack/, netbox-stack/

### 4. backup-infrastructure

**Purpose**: Backup automation

**Roles**: proxmox-backup-server

**Playbooks**: pbs-setup.yml

**Host**: plato (PBS)

### 5. homelab-docs (Optional)

**Purpose**: Documentation site

**Contents**: docs/, mkdocs.yml

---

## Migration Steps

### Phase 1: GitLab Setup (30 min)

```bash
# 1. Log in to GitLab
open http://10.203.3.204
# Username: root
# Password: (see gitlab-access.md)

# 2. Change root password (via Web UI)

# 3. Create group: "homelab"

# 4. Create empty repositories:
#    - homelab/infrastructure-core
#    - homelab/ai-infrastructure
#    - homelab/homelab-services
#    - homelab/backup-infrastructure
#    - homelab/homelab-docs (optional)

# 5. Add SSH key to GitLab profile
```

### Phase 2: Split Repositories (2-3 hours)

```bash
# Install git-filter-repo
brew install git-filter-repo

# Create working directory
mkdir -p ~/temp-migration
cd ~/temp-migration

# For each repository:
# 1. Clone fresh copy from monorepo
# 2. Use git filter-repo to extract paths
# 3. Add GitLab remote
# 4. Push to GitLab

# See full commands in gitlab-migration-plan.md Phase 2
```

### Phase 3: Verification (30 min)

```bash
# Test each repository
git clone git@10.203.3.204:homelab/infrastructure-core.git
cd infrastructure-core
ansible-playbook -i inventory-prod.ini site.yml --check --limit zeno

# Repeat for each repo
```

### Phase 4: Archive Monorepo (After validation)

```bash
# Add deprecation notice to README
# Archive (don't delete) original repository
# Keep for 3-6 months as safety net
```

---

## Git URLs

**SSH Clone URLs**:
```
git@10.203.3.204:homelab/infrastructure-core.git
git@10.203.3.204:homelab/ai-infrastructure.git
git@10.203.3.204:homelab/homelab-services.git
git@10.203.3.204:homelab/backup-infrastructure.git
git@10.203.3.204:homelab/homelab-docs.git
```

**Web URLs**:
```
http://10.203.3.204/homelab/infrastructure-core
http://10.203.3.204/homelab/ai-infrastructure
http://10.203.3.204/homelab/homelab-services
http://10.203.3.204/homelab/backup-infrastructure
http://10.203.3.204/homelab/homelab-docs
```

---

## Key Decisions

1. **Functional split** (not layer-based): Organize by infrastructure domain
2. **History preservation**: Use git-filter-repo for infrastructure-core
3. **Shared code**: Copy initially, consolidate to Ansible collection later
4. **Inventory**: Copy to each repo, migrate to NetBox dynamic inventory later
5. **Docs**: Start merged with infrastructure-core, split if needed

---

## Current State

**Current Repo**: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`

**Status**:
- Git working tree: Modified (ansible roles, services/ directory)
- Branch: main
- Recent commits: NVIDIA GPU roles, AI containers

**Legacy Repo**: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`

**Lessons Learned**:
- Keep it simple (avoid reverse proxy complexity)
- LXC > VMs for efficiency
- Document decisions in ADRs
- Test DNS thoroughly

---

## Rollback Plan

If migration fails:
1. Original monorepo stays unchanged
2. Delete GitLab repositories and retry
3. Temp migration directory preserved
4. Continue using monorepo

---

## Next Actions

**TODAY**:
1. ✅ Planning complete
2. ✅ GitLab password retrieved
3. ⏭️ Log in to GitLab
4. ⏭️ Create homelab group
5. ⏭️ Create empty repositories

**THIS WEEKEND**:
6. Backup monorepo (git bundle)
7. Execute Phase 2 migration
8. Test and validate

**NEXT WEEK**:
9. Complete all repository migrations
10. Update documentation
11. Archive monorepo

---

## Documents

**Primary**:
- **Migration Plan**: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-migration-plan.md`
- **GitLab Access**: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-access.md`
- **This Summary**: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/MIGRATION-SUMMARY.md`

**Reference**:
- Current TODO: `/Users/kellen/_Noetica/myt/_code/homelab-automation/TODO.md`
- Inventory: `/Users/kellen/_Noetica/myt/_code/homelab-automation/ansible/inventory-prod.ini`
- Legacy docs: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`

---

## Questions?

See the full plan in `gitlab-migration-plan.md` for:
- Detailed repository contents
- Complete migration commands
- Git history considerations
- Dependency management strategies
- Troubleshooting guidance

---

**Ready to proceed!** Start with Phase 1 (GitLab setup) when ready.
