# GitLab Repository Migration - Complete Package

**Status**: Planning Complete - Ready to Execute
**Created**: 2025-12-13
**GitLab Instance**: http://10.203.3.204

---

## What's Been Completed

I've completed a comprehensive analysis and planning phase for migrating your homelab-automation monorepo to a functional split across multiple GitLab repositories.

### Analysis Performed

1. **Current Repository Structure**: Analyzed all 21 Ansible roles, 5 service stacks, and supporting files
2. **Legacy Repository Review**: Examined descartes-stack-master for reusable components and lessons learned
3. **Infrastructure Inventory**: Mapped all 7 hosts and their roles
4. **Dependency Analysis**: Identified cross-repository dependencies and shared components
5. **GitLab Access**: Retrieved root password and verified instance is operational

### Documents Created

Six comprehensive planning documents are now available in the `/docs/` directory:

1. **gitlab-migration-plan.md** (9,000+ words)
   - Complete migration strategy
   - Detailed repository breakdown
   - Git history preservation approach
   - Step-by-step migration commands
   - Rollback procedures

2. **gitlab-access.md**
   - GitLab login credentials
   - SSH access instructions
   - Container management commands
   - Troubleshooting guide

3. **MIGRATION-SUMMARY.md**
   - Quick reference overview
   - Repository structure at a glance
   - Migration phases summary
   - Key decisions documented

4. **repository-structure.md**
   - Visual diagrams of repository organization
   - Current vs. future state comparison
   - Dependency flow visualization
   - Access patterns and workflows

5. **MIGRATION-CHECKLIST.md**
   - Complete task checklist
   - Phase-by-phase tracking
   - Success criteria
   - Notes section for issues

6. **This file** (GITLAB-MIGRATION-README.md)
   - Navigation guide for all documents
   - Quick start instructions

---

## Proposed Repository Structure

Your monorepo will be split into **4-5 functional repositories**:

### 1. infrastructure-core
**Purpose**: Foundation Proxmox cluster automation
**Contents**: 12 roles (base, cluster, hardware, storage, templates)
**Size**: ~60 files (largest repository)

### 2. ai-infrastructure
**Purpose**: GPU-accelerated AI workload management
**Contents**: 2 roles (NVIDIA GPU, AI containers) + AI service stacks
**Size**: ~20 files

### 3. homelab-services
**Purpose**: Service deployment & configuration
**Contents**: 6 roles (GitLab, DNS, NetBox, Tailscale) + service stacks
**Size**: ~30 files

### 4. backup-infrastructure
**Purpose**: Proxmox Backup Server & disaster recovery
**Contents**: 1 role (PBS) + backup automation scripts
**Size**: ~10 files

### 5. homelab-docs (Optional)
**Purpose**: Centralized documentation site
**Contents**: MkDocs documentation and guides
**Size**: ~50 files

---

## Why This Structure?

**Functional Separation**: Each repository serves a distinct infrastructure domain
**Independent Versioning**: Components can evolve at different rates
**Focused CI/CD**: Test and deploy only what changed
**Better Collaboration**: Grant access to specific areas only
**Clear Dependencies**: Logical deployment order (infrastructure → AI → services → backups)

---

## Quick Start Guide

### Step 1: Access GitLab (5 minutes)

```bash
# 1. Open GitLab in browser
open http://10.203.3.204

# 2. Log in with credentials from docs/gitlab-access.md
Username: root
Password: (see docs/gitlab-access.md or reset via gitlab-rake)

# 3. Change password immediately via Web UI
# Profile Icon → Preferences → Password

# 4. Add your SSH key
# Preferences → SSH Keys
# Use cogito or ergo-sum key from CLAUDE.md
```

### Step 2: Create Repository Structure (10 minutes)

```bash
# In GitLab Web UI:

1. Create group: "homelab"
   - Set visibility: Internal
   - Enable group-level CI/CD

2. Create projects under homelab/:
   - infrastructure-core
   - ai-infrastructure
   - homelab-services
   - backup-infrastructure
   - homelab-docs (optional)

3. All projects:
   - Visibility: Internal
   - Initialize README: No (will push from migration)
```

### Step 3: Install Migration Tools (2 minutes)

```bash
# Install git-filter-repo for history preservation
brew install git-filter-repo

# Create working directory
mkdir -p ~/temp-migration
```

### Step 4: Execute Migration (2-3 hours)

Follow the detailed commands in:
- **docs/gitlab-migration-plan.md** (Phase 2: Split Repository)
- **docs/MIGRATION-CHECKLIST.md** (Phase 2 section)

**OR** for a quick test, start with just one repository:

```bash
# Migrate infrastructure-core first (test run)
cd ~/temp-migration
git clone /Users/kellen/_Noetica/myt/_code/homelab-automation infrastructure-core
cd infrastructure-core

# Use git filter-repo to extract infrastructure files
# (See full command in gitlab-migration-plan.md section 2.1)

# Push to GitLab
git remote add gitlab git@10.203.3.204:homelab/infrastructure-core.git
git push -u gitlab main
```

### Step 5: Verify & Test (30 minutes)

```bash
# Clone from GitLab
cd ~/temp-migration/testing
git clone git@10.203.3.204:homelab/infrastructure-core.git

# Test Ansible playbook
cd infrastructure-core
ansible-playbook -i inventory-prod.ini site.yml --check --limit zeno

# If successful, proceed with remaining repositories
```

---

## Document Navigation

### Start Here
- **This file**: Overview and quick start

### Planning & Strategy
- **docs/gitlab-migration-plan.md**: Complete migration strategy (READ THIS FIRST)
- **docs/MIGRATION-SUMMARY.md**: Quick reference summary
- **docs/repository-structure.md**: Visual diagrams and structure

### Execution
- **docs/MIGRATION-CHECKLIST.md**: Task-by-task checklist
- **docs/gitlab-access.md**: Access credentials and commands

### Current State
- **TODO.md**: Project status and roadmap
- **ansible/inventory-prod.ini**: Infrastructure inventory
- **ansible/site.yml**: Main playbook

---

## Key Information

### GitLab Instance
- **URL**: http://10.203.3.204
- **Container**: VMID 204 on rawls (10.203.3.47)
- **SSH Access**: `ssh kellen@10.203.3.47` then `sudo pct enter 204`

### SSH Clone URLs (After Creation)
```
git@10.203.3.204:homelab/infrastructure-core.git
git@10.203.3.204:homelab/ai-infrastructure.git
git@10.203.3.204:homelab/homelab-services.git
git@10.203.3.204:homelab/backup-infrastructure.git
```

### Current Repository
- **Location**: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`
- **Status**: Active (will be archived after migration)
- **Git Branch**: main
- **Recent Work**: NVIDIA GPU roles, AI containers

### Legacy Reference
- **Location**: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`
- **Status**: Reference only (Nov 2025 snapshot)
- **Useful**: ADR documentation, deployment scripts, network discovery

---

## Migration Phases Overview

```
Phase 1: GitLab Setup (30 min)
├── Log in and change password
├── Create homelab group
└── Create empty repositories

Phase 2: Split Repository (2-3 hours)
├── Setup working directory
├── Migrate infrastructure-core
├── Migrate ai-infrastructure
├── Migrate homelab-services
├── Migrate backup-infrastructure
└── Migrate homelab-docs (optional)

Phase 3: Verification (30 min)
├── Check repository contents
├── Verify Git history preserved
├── Test SSH clone
└── Test Ansible playbooks

Phase 4: Documentation Updates (1 hour)
├── Update READMEs per repo
├── Add cross-repository links
└── Update CLAUDE.md files

Phase 5: Monorepo Deprecation (after validation)
├── Add deprecation notice
├── Create git bundle backup
└── Archive original repository

Phase 6: Workflow Transition
├── Clone new repositories to working location
├── Update automation scripts
└── Document new workflow
```

---

## Safety & Rollback

**Safety Measures**:
- Original monorepo remains unchanged during migration
- All work done in separate `~/temp-migration` directory
- GitLab repositories can be deleted and recreated if needed
- Git bundle backup created before archiving monorepo

**Rollback Procedure**:
1. Stop migration process
2. Delete GitLab repositories via Web UI
3. Original repo unchanged at current location
4. Clean up temp directory and retry

**No Risk to Current Work**: Your working repository at `/Users/kellen/_Noetica/myt/_code/homelab-automation/` is not touched until you explicitly archive it in Phase 5.

---

## Key Decisions Made

1. **Functional Split**: Organized by infrastructure domain (not layers like ansible/docker)
2. **History Preservation**: Use git-filter-repo for infrastructure-core (most valuable)
3. **Repository Count**: 4-5 repos balances separation with manageability
4. **Shared Code**: Copy initially, consolidate to Ansible collection later
5. **Inventory**: Copy to each repo initially, migrate to NetBox dynamic inventory later
6. **Documentation**: Start merged with infrastructure-core, split if needed

---

## Success Criteria

Migration is considered successful when:

- [ ] All repositories created and accessible in GitLab
- [ ] Git history preserved for key files
- [ ] Ansible playbooks pass `--check` validation in each repo
- [ ] SSH clone/push/pull works for all repositories
- [ ] Documentation updated with cross-links
- [ ] Original monorepo safely archived
- [ ] New multi-repo workflow documented

---

## Next Actions

**Immediate** (Today/This Weekend):
1. Log in to GitLab and change root password
2. Create homelab group and repositories
3. Install git-filter-repo tool
4. Create git bundle backup of current repository
5. Execute Phase 2 migration (start with infrastructure-core)

**Short Term** (Next Week):
6. Complete remaining repository migrations
7. Verify all playbooks work independently
8. Update documentation across all repos

**Long Term** (Future):
9. Set up CI/CD pipelines per repository
10. Create Ansible collection for shared code
11. Implement dynamic inventory from NetBox
12. Archive original monorepo (after 3-6 months)

---

## Questions or Issues?

If you encounter any issues during migration:

1. **Check the detailed plan**: docs/gitlab-migration-plan.md has troubleshooting sections
2. **Review the checklist**: docs/MIGRATION-CHECKLIST.md has a notes section
3. **Rollback if needed**: Safe to delete GitLab repos and retry
4. **Ask for help**: Original repo is unchanged, no risk to current work

---

## Infrastructure Context

### Hosts in Inventory
- **zeno** (10.203.3.49): Media server
- **rawls** (10.203.3.47): Infrastructure node (hosts GitLab container)
- **socrates** (10.203.3.42): AI workstation (2x Tesla P40 GPUs)
- **frege, russell, wittgenstein** (10.203.3.11-13): MS-01 cluster
- **plato** (10.203.3.97): Proxmox Backup Server

### Current Capabilities
- 21 Ansible roles for complete infrastructure automation
- GPU passthrough and AI container management
- Service deployments (GitLab, DNS, NetBox)
- Backup automation
- Cluster networking (Thunderbolt ring for MS-01)

---

## Lessons from Legacy Repository

From analyzing descartes-stack-master:

**What Worked Well**:
- Comprehensive ADR documentation
- LXC containers over VMs for efficiency
- Tailscale mesh VPN integration
- Infrastructure discovery automation

**What to Avoid**:
- Caddy reverse proxy complexity (kept hitting issues)
- Split-horizon DNS complications
- Over-reliance on interactive scripts (need declarative approach)

**Key Insight**: "Keep it simple" - Direct access often better than proxy layers

---

## File Locations

**Migration Planning Documents**:
```
/Users/kellen/_Noetica/myt/_code/homelab-automation/
├── GITLAB-MIGRATION-README.md (this file)
└── docs/
    ├── gitlab-migration-plan.md      (9,000+ word complete strategy)
    ├── gitlab-access.md               (credentials & access)
    ├── MIGRATION-SUMMARY.md           (quick reference)
    ├── repository-structure.md        (visual diagrams)
    └── MIGRATION-CHECKLIST.md         (task tracking)
```

**Current Infrastructure Code**:
```
/Users/kellen/_Noetica/myt/_code/homelab-automation/
├── ansible/
│   ├── roles/               (21 roles to be split)
│   ├── inventory-prod.ini   (infrastructure inventory)
│   └── site.yml             (main playbook)
├── services/                (Docker compose stacks)
├── TODO.md                  (project roadmap)
└── README.md                (current overview)
```

**Legacy Reference**:
```
/Users/kellen/_Noetica/myt/_code/descartes-stack-master/
├── CURRENT-STATUS.md        (lessons learned)
├── architecture/            (ADR documentation)
└── scripts/                 (deployment automation)
```

---

## Ready to Begin!

You now have:
- Complete migration strategy documented
- GitLab instance ready and accessible
- Detailed step-by-step instructions
- Safety measures and rollback procedures
- Visual diagrams and checklists

**Start when ready**: Follow docs/gitlab-migration-plan.md Phase 1, or use the Quick Start Guide above.

**No code has been pushed yet** - this is pure planning and documentation. You're in full control of when to proceed.

---

## Summary

I've analyzed your current homelab-automation monorepo, examined the legacy descartes-stack-master for lessons learned, and designed a functional split into 4-5 GitLab repositories. All planning documents are complete and ready for execution.

The migration preserves Git history, maintains Ansible functionality, and provides clear separation of concerns. Your original repository remains unchanged until you explicitly archive it.

**Total Planning Output**: 6 comprehensive documents, ~15,000 words of strategy and guidance.

**Ready to proceed with Phase 1 when you are!**
