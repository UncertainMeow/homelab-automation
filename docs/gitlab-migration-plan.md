# GitLab Repository Organization & Migration Plan

**Status**: Planning Phase
**GitLab Instance**: http://10.203.3.204
**Last Updated**: 2025-12-13

---

## Executive Summary

This document outlines the strategy for migrating from a monorepo structure to a functional split across multiple GitLab repositories. The current `homelab-automation` codebase will be split into 3-5 focused repositories, each serving a specific infrastructure function.

**Key Goals**:
- Organize code by functional domain (infrastructure, services, AI workloads)
- Enable independent versioning and CI/CD per domain
- Maintain Git history where practical
- Simplify collaboration and maintenance

---

## Current State Analysis

### Current Repository: `homelab-automation`

**Location**: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`

**Contents**:

```
homelab-automation/
├── ansible/                    # Core infrastructure automation
│   ├── roles/                  # 21 Ansible roles
│   │   ├── proxmox-base        # Base system config
│   │   ├── proxmox-cluster     # Cluster formation
│   │   ├── proxmox-nvidia-gpu  # GPU passthrough
│   │   ├── nvidia-lxc-ai       # AI containers
│   │   ├── gitlab              # GitLab deployment
│   │   ├── technitium-dns      # DNS server
│   │   ├── netbox              # IPAM
│   │   ├── tailscale-subnet-router
│   │   ├── thunderbolt-ring    # MS-01 cluster networking
│   │   └── ...                 # 12 more roles
│   ├── host_vars/              # Per-host configuration
│   ├── group_vars/             # Common settings
│   ├── inventory-prod.ini      # Infrastructure inventory
│   ├── site.yml                # Main playbook
│   └── *.yml                   # Specialized playbooks
├── services/                   # Docker compose stacks
│   ├── ai-stack/               # Karakeep + Meilisearch
│   ├── llm-stack/              # Ollama + Open WebUI
│   ├── gitlab-stack/           # GitLab compose (future)
│   ├── dns-stack/              # Technitium DNS
│   └── netbox-stack/           # NetBox IPAM
├── docs/                       # Documentation
│   ├── architecture/
│   ├── guides/
│   └── reference/
├── external-inspiration/       # Reference material
├── mkdocs.yml                  # Documentation site
├── TODO.md                     # Project tracking
├── README.md
└── CLAUDE.md                   # Project instructions
```

**Infrastructure Inventory** (from `inventory-prod.ini`):
- **zeno** (10.203.3.49): Media server (*arr stack, Jellyfin)
- **rawls** (10.203.3.47): Infra node (GitLab, DNS, Authentik)
- **socrates** (10.203.3.42): AI workstation (2x Tesla P40)
- **MS-01 Cluster**: frege, russell, wittgenstein (10.203.3.11-13)
- **plato** (10.203.3.97): Proxmox Backup Server

**Key Roles by Category**:

1. **Infrastructure Foundation** (7 roles):
   - proxmox-base, user-management, proxmox-community-scripts
   - proxmox-pci-passthrough, proxmox-cluster, thunderbolt-ring
   - nfs-storage

2. **AI/GPU Workloads** (2 roles):
   - proxmox-nvidia-gpu, nvidia-lxc-ai

3. **Services** (6 roles):
   - gitlab, netbox, netbox-dns-sync
   - technitium-dns, docs-site, tailscale-subnet-router

4. **Templates & Tools** (3 roles):
   - vm-templates, lxc-templates, dotfiles-portable

5. **Backup & Recovery** (2 roles):
   - proxmox-backup-server, proxmox-backup-client
   - infra-snapshot

---

### Legacy Repository: `descartes-stack-master`

**Location**: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`

**Status**: Legacy reference codebase (Nov 2025 snapshot)

**Worth Salvaging**:
1. **Architecture Documentation**: Comprehensive ADRs and C4 model diagrams
2. **Deployment Scripts**: Working bash automation (deploy-all.sh, etc.)
3. **Network Discovery**: Python script for UDM Pro integration
4. **Tailscale Integration**: Working patterns for mesh VPN setup

**Patterns to Avoid**:
- Caddy reverse proxy complexity (kept hitting issues)
- Split-horizon DNS complications (NetBox local network routing)
- Over-reliance on interactive scripts (need declarative approach)
- 1Password CLI secrets (no evidence found in current codebase)

**Key Lessons Documented**:
- Keep it simple: Direct access > reverse proxy complexity
- LXC > VMs for resource efficiency
- Document decisions in ADRs
- Test DNS configurations thoroughly

---

## Proposed Repository Structure

### Functional Split Strategy

Based on the current codebase analysis, here's the recommended repository organization:

#### **Repo 1: `infrastructure-core`**

**Purpose**: Foundation-level Proxmox cluster automation

**Contents**:
- Proxmox base system configuration
- User management & SSH hardening
- PCI passthrough & hardware support
- Cluster formation & networking
- NFS storage configuration
- Backup client setup

**Ansible Roles**:
- proxmox-base
- user-management
- proxmox-community-scripts
- proxmox-pci-passthrough
- proxmox-cluster
- thunderbolt-ring
- nfs-storage
- proxmox-backup-client
- vm-templates
- lxc-templates
- dotfiles-portable
- infra-snapshot

**Inventory**: Full cluster inventory (proxmox group)

**Playbooks**:
- cluster-base-config.yml
- cluster-setup.yml
- cluster-post-install.yml
- pve-backup-setup.yml

**Why This Grouping**: These roles work together to establish baseline infrastructure. They're run together during initial node setup and rarely change independently.

#### **Repo 2: `ai-infrastructure`**

**Purpose**: GPU-accelerated AI workload management

**Contents**:
- NVIDIA driver installation
- GPU passthrough configuration
- AI container creation & management
- Model storage setup
- Docker compose stacks for AI services

**Ansible Roles**:
- proxmox-nvidia-gpu
- nvidia-lxc-ai

**Services** (from main repo):
- services/ai-stack/ (Karakeep, Meilisearch)
- services/llm-stack/ (Ollama, Open WebUI)

**Host Vars**:
- host_vars/socrates.yml (AI workstation config)

**Playbooks**:
- ai-workstation-setup.yml

**Scripts**:
- scripts/socrates-ai (GPU mode switching)
- scripts/deploy-ai-stack.sh

**Why Separate**: AI infrastructure has unique dependencies (NVIDIA drivers, CUDA), different update cadence, and specialized hardware requirements. Separating allows AI-focused iteration without touching core infrastructure.

#### **Repo 3: `homelab-services`**

**Purpose**: Service deployment & configuration

**Contents**:
- LXC-based service deployments
- Docker compose stacks
- Service-specific configurations
- Integration automation

**Ansible Roles**:
- gitlab
- netbox
- netbox-dns-sync
- technitium-dns
- docs-site
- tailscale-subnet-router

**Services** (from main repo):
- services/gitlab-stack/
- services/dns-stack/
- services/netbox-stack/

**Playbooks**:
- deploy-gitlab.yml
- deploy-netbox.yml
- deploy-dns.yml

**Why Separate**: Services are deployed independently, have different lifecycle cadences, and may be managed by different team members. Each service should be versionable and deployable independently.

#### **Repo 4: `backup-infrastructure`**

**Purpose**: Proxmox Backup Server & disaster recovery

**Contents**:
- PBS server setup
- Backup automation
- Recovery procedures
- Backup verification

**Ansible Roles**:
- proxmox-backup-server

**Playbooks**:
- pbs-setup.yml

**Scripts**:
- backup-verification.sh
- disaster-recovery.sh

**Documentation**:
- Backup procedures
- Recovery runbooks
- Testing schedules

**Why Separate**: Backup infrastructure is critical and should be managed independently. It has its own host (plato), distinct responsibilities, and needs careful change management.

#### **Repo 5: `homelab-docs`** (Optional)

**Purpose**: Centralized documentation site

**Contents**:
- MkDocs documentation
- Architecture diagrams
- Setup guides
- Reference materials

**Current Structure**:
- docs/
- mkdocs.yml
- README.md

**Why Separate**: Documentation changes frequently and independently from code. Separating allows non-technical contributors to improve docs without infrastructure repo access.

**Alternative**: Could be merged into infrastructure-core if documentation is tightly coupled to code.

---

## Repository Dependencies & Shared Code

### Shared Components

**Problem**: Multiple repos need common functionality

**Solutions**:

1. **Ansible Collections** (Recommended):
   - Create `homelab.common` Ansible collection
   - Include shared variables, filters, plugins
   - Version independently
   - Install via `requirements.yml`

2. **Git Submodules** (For shared roles):
   - Create `homelab-ansible-roles` repo
   - Reference as submodule in each repo
   - Update independently

3. **Copy on Split** (Simplest):
   - Duplicate common code into each repo
   - Accept some redundancy for simplicity
   - Consolidate later if needed

**Recommendation**: Start with option 3 (copy on split) for initial migration, then migrate to Ansible collections once patterns stabilize.

### Cross-Repository Inventory

**Challenge**: Multiple repos need access to the same inventory

**Solution**:
- Store inventory in `infrastructure-core` as source of truth
- Other repos reference via Git submodule or copy
- Use dynamic inventory from NetBox (future enhancement)

---

## Migration Strategy

### Phase 1: Preparation (1-2 hours)

#### 1.1: Set Up GitLab Instance

```bash
# SSH to Rawls (Proxmox host running GitLab container)
ssh ansible@10.203.3.47

# Enter GitLab container
sudo pct enter 204

# Get or reset root password
cat /etc/gitlab/initial_root_password
# If expired (>24h), reset:
gitlab-rake "gitlab:password:reset[root]"

# Exit container
exit
```

**Access GitLab**: http://10.203.3.204
**Login**: root / (password from above)

#### 1.2: Create GitLab Group Structure

In GitLab UI:
1. Log in as root
2. Create group: `homelab`
3. Set group visibility: Internal
4. Enable group-level CI/CD settings

#### 1.3: Create Empty Repositories

Create these projects under the `homelab` group:

```
homelab/infrastructure-core
homelab/ai-infrastructure
homelab/homelab-services
homelab/backup-infrastructure
homelab/homelab-docs (optional)
```

**GitLab URLs** (for reference):
- http://10.203.3.204/homelab/infrastructure-core
- http://10.203.3.204/homelab/ai-infrastructure
- http://10.203.3.204/homelab/homelab-services
- http://10.203.3.204/homelab/backup-infrastructure
- http://10.203.3.204/homelab/homelab-docs

**Clone URLs** (SSH):
```
git@10.203.3.204:homelab/infrastructure-core.git
git@10.203.3.204:homelab/ai-infrastructure.git
git@10.203.3.204:homelab/homelab-services.git
git@10.203.3.204:homelab/backup-infrastructure.git
git@10.203.3.204:homelab/homelab-docs.git
```

### Phase 2: Split Repository (2-3 hours)

#### 2.1: Infrastructure Core

**Strategy**: Use `git filter-repo` to preserve history

```bash
# Create working directory
mkdir -p ~/temp-migration
cd ~/temp-migration

# Clone fresh copy
git clone /Users/kellen/_Noetica/myt/_code/homelab-automation infrastructure-core
cd infrastructure-core

# Install git-filter-repo if needed
brew install git-filter-repo

# Keep only infrastructure-related files
git filter-repo --path ansible/roles/proxmox-base \
  --path ansible/roles/user-management \
  --path ansible/roles/proxmox-community-scripts \
  --path ansible/roles/proxmox-pci-passthrough \
  --path ansible/roles/proxmox-cluster \
  --path ansible/roles/thunderbolt-ring \
  --path ansible/roles/nfs-storage \
  --path ansible/roles/proxmox-backup-client \
  --path ansible/roles/vm-templates \
  --path ansible/roles/lxc-templates \
  --path ansible/roles/dotfiles-portable \
  --path ansible/roles/infra-snapshot \
  --path ansible/inventory-prod.ini \
  --path ansible/group_vars \
  --path ansible/host_vars \
  --path ansible/cluster-base-config.yml \
  --path ansible/cluster-setup.yml \
  --path ansible/cluster-post-install.yml \
  --path ansible/pve-backup-setup.yml \
  --path ansible/site.yml \
  --path README.md \
  --path CLAUDE.md

# Reorganize structure (flatten ansible/)
# Manual step: Move ansible/* to root, update paths

# Add GitLab remote
git remote add gitlab git@10.203.3.204:homelab/infrastructure-core.git

# Push to GitLab
git push -u gitlab main
```

#### 2.2: AI Infrastructure

```bash
cd ~/temp-migration
git clone /Users/kellen/_Noetica/myt/_code/homelab-automation ai-infrastructure
cd ai-infrastructure

# Keep only AI-related files
git filter-repo --path ansible/roles/proxmox-nvidia-gpu \
  --path ansible/roles/nvidia-lxc-ai \
  --path ansible/host_vars/socrates.yml \
  --path services/ai-stack \
  --path services/llm-stack \
  --path README.md \
  --path CLAUDE.md

# Reorganize structure
# Create ai-workstation-setup.yml playbook

# Add GitLab remote and push
git remote add gitlab git@10.203.3.204:homelab/ai-infrastructure.git
git push -u gitlab main
```

#### 2.3: Homelab Services

```bash
cd ~/temp-migration
git clone /Users/kellen/_Noetica/myt/_code/homelab-automation homelab-services
cd homelab-services

# Keep only service-related files
git filter-repo --path ansible/roles/gitlab \
  --path ansible/roles/netbox \
  --path ansible/roles/netbox-dns-sync \
  --path ansible/roles/technitium-dns \
  --path ansible/roles/docs-site \
  --path ansible/roles/tailscale-subnet-router \
  --path services/gitlab-stack \
  --path services/dns-stack \
  --path services/netbox-stack \
  --path README.md \
  --path CLAUDE.md

# Add GitLab remote and push
git remote add gitlab git@10.203.3.204:homelab/homelab-services.git
git push -u gitlab main
```

#### 2.4: Backup Infrastructure

```bash
cd ~/temp-migration
git clone /Users/kellen/_Noetica/myt/_code/homelab-automation backup-infrastructure
cd backup-infrastructure

# Keep only backup-related files
git filter-repo --path ansible/roles/proxmox-backup-server \
  --path ansible/pbs-setup.yml \
  --path ansible/host_vars/plato.yml \
  --path README.md \
  --path CLAUDE.md

# Add GitLab remote and push
git remote add gitlab git@10.203.3.204:homelab/backup-infrastructure.git
git push -u gitlab main
```

#### 2.5: Homelab Docs (Optional)

```bash
cd ~/temp-migration
git clone /Users/kellen/_Noetica/myt/_code/homelab-automation homelab-docs
cd homelab-docs

# Keep only documentation
git filter-repo --path docs \
  --path mkdocs.yml \
  --path README.md

# Add GitLab remote and push
git remote add gitlab git@10.203.3.204:homelab/homelab-docs.git
git push -u gitlab main
```

### Phase 3: Verification (30 minutes)

#### 3.1: Verify Repository Contents

For each repository:
1. Browse in GitLab UI
2. Check file structure is correct
3. Verify Git history is preserved (for files included in filter)
4. Test clone via SSH

#### 3.2: Test Ansible Playbooks

```bash
# Infrastructure core
git clone git@10.203.3.204:homelab/infrastructure-core.git
cd infrastructure-core
ansible-playbook -i inventory-prod.ini site.yml --check --limit zeno

# AI infrastructure
git clone git@10.203.3.204:homelab/ai-infrastructure.git
cd ai-infrastructure
ansible-playbook -i inventory.ini ai-workstation-setup.yml --check --limit socrates
```

#### 3.3: Update Documentation

For each repository:
1. Update README.md with repository-specific overview
2. Add migration notes
3. Document cross-repo dependencies
4. Link to other repos in homelab group

### Phase 4: Deprecate Monorepo (After validation)

**Do NOT delete the original monorepo immediately**

1. Add notice to original README:
```markdown
# ⚠️ REPOSITORY MIGRATED

This repository has been split into functional repositories:
- Infrastructure: http://10.203.3.204/homelab/infrastructure-core
- AI Workloads: http://10.203.3.204/homelab/ai-infrastructure
- Services: http://10.203.3.204/homelab/homelab-services
- Backups: http://10.203.3.204/homelab/backup-infrastructure

This repository is archived for reference only.
```

2. Archive the repository (not delete)
3. Keep for 3-6 months as safety net

---

## Git History Considerations

### What Gets Preserved

**Full History** (via git filter-repo):
- Files included in filter path will retain complete commit history
- Branch history maintained
- Author information preserved
- Commit timestamps maintained

**Partial History**:
- Commits that only touched filtered files will appear
- Commits spanning multiple filtered areas will be split

### What Gets Lost

**Not Preserved**:
- History for files NOT in filter paths
- Cross-file refactoring context (commits touching multiple repos)
- Full git blame for restructured files

### Alternative: Fresh Start

For simpler migration, could create fresh repositories without history:

**Pros**:
- Cleaner structure from day one
- No filter-repo complexity
- Faster migration

**Cons**:
- Lose commit history (blame, debugging)
- Can't trace evolution of configuration

**Recommendation**: Preserve history for infrastructure-core (most valuable), consider fresh start for smaller repos if git-filter-repo proves complicated.

---

## Migration Checklist

### Pre-Migration

- [ ] Document current repository structure
- [ ] Identify all cross-repository dependencies
- [ ] Back up current repository (git bundle)
- [ ] Set up GitLab instance and verify access
- [ ] Install git-filter-repo tool

### GitLab Setup

- [ ] Log in to GitLab as root
- [ ] Create `homelab` group
- [ ] Create empty repositories
- [ ] Configure SSH key access
- [ ] Test git clone/push

### Repository Splitting

- [ ] Split infrastructure-core
- [ ] Split ai-infrastructure
- [ ] Split homelab-services
- [ ] Split backup-infrastructure
- [ ] Split homelab-docs (optional)

### Post-Migration

- [ ] Verify all repositories accessible
- [ ] Test ansible playbooks in each repo
- [ ] Update cross-repo references
- [ ] Document new workflow
- [ ] Update CLAUDE.md in each repo

### Cleanup

- [ ] Archive original monorepo
- [ ] Add deprecation notice
- [ ] Update external documentation
- [ ] Notify any collaborators

---

## Rollback Plan

If migration fails or causes issues:

1. **Keep original repository unchanged** during migration
2. **GitLab repos can be deleted** and recreated
3. **Temp migration directory** preserved until validated

**Rollback Steps**:
```bash
# Delete GitLab repositories via UI
# Original repo at /Users/kellen/_Noetica/myt/_code/homelab-automation unchanged
# Continue using monorepo
```

---

## Next Steps

**Immediate** (Today):
1. Retrieve GitLab root password
2. Log in and create `homelab` group
3. Create empty repositories in GitLab

**Short Term** (This Weekend):
4. Backup current repository (git bundle)
5. Execute Phase 2 migration for infrastructure-core
6. Test and validate

**Medium Term** (Next Week):
7. Complete remaining repository migrations
8. Update documentation across all repos
9. Archive monorepo

**Long Term** (Future):
10. Set up CI/CD per repository
11. Consider Ansible collection for shared code
12. Implement dynamic inventory from NetBox

---

## References

**Current Repository**:
- Main: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`
- TODO: `/Users/kellen/_Noetica/myt/_code/homelab-automation/TODO.md`
- Inventory: `/Users/kellen/_Noetica/myt/_code/homelab-automation/ansible/inventory-prod.ini`

**Legacy Repository**:
- Location: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`
- Lessons: ADR documentation, architecture patterns

**GitLab Instance**:
- URL: http://10.203.3.204
- Host: rawls (10.203.3.47)
- Container: VMID 204

**Tools**:
- `git-filter-repo`: https://github.com/newren/git-filter-repo
- Ansible collections: https://docs.ansible.com/ansible/latest/collections_guide/

---

## Questions & Decisions

### Open Questions

1. **Docs Repository**: Separate or merge with infrastructure-core?
   - **Recommendation**: Start merged, split later if needed

2. **Shared Inventory**: How to handle across repos?
   - **Recommendation**: Copy initially, move to dynamic inventory (NetBox) later

3. **Media Stack**: Where does it belong?
   - **Current**: Not in current monorepo structure
   - **Recommendation**: Create separate `media-services` repo if needed

4. **Git History**: Full preservation or fresh start?
   - **Recommendation**: Preserve for infrastructure-core, fresh start acceptable for others

### Decisions Made

- **Functional split**: Chose over layer-based (ansible/docker) split
- **Repository count**: 4-5 repos provides good balance of separation and manageability
- **Migration tool**: git-filter-repo for history preservation
- **Rollback strategy**: Keep original monorepo unchanged during migration

---

**Status**: Ready to proceed with Phase 1 (GitLab setup)
**Next Action**: Retrieve GitLab root password and log in
