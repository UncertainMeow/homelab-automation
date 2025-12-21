# GitLab Migration Checklist

**Status**: Planning Complete
**Start Date**: 2025-12-13
**Target Completion**: TBD

---

## Pre-Migration Preparation

- [x] Document current repository structure
- [x] Analyze legacy descartes-stack-master for reusable components
- [x] Identify cross-repository dependencies
- [x] Design functional repository split (4-5 repos)
- [x] Retrieve GitLab root password
- [ ] Backup current repository (git bundle)
- [ ] Install git-filter-repo tool
  ```bash
  brew install git-filter-repo
  ```

---

## Phase 1: GitLab Instance Setup

### 1.1 Initial Access

- [ ] Log in to GitLab at http://10.203.3.204
  - Username: `root`
  - Password: See `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-access.md`
- [ ] Change root password via Web UI
  - Profile Icon → Preferences → Password
- [ ] Add SSH key to GitLab profile
  - Preferences → SSH Keys
  - Use cogito or ergo-sum key from CLAUDE.md
- [ ] Test SSH connection
  ```bash
  ssh -T git@10.203.3.204
  ```

### 1.2 Group & Repository Creation

- [ ] Create `homelab` group
  - Set visibility: Internal
  - Enable group-level CI/CD
- [ ] Create repository: `homelab/infrastructure-core`
  - Visibility: Internal
  - Initialize with README: No (will push from migration)
- [ ] Create repository: `homelab/ai-infrastructure`
- [ ] Create repository: `homelab/homelab-services`
- [ ] Create repository: `homelab/backup-infrastructure`
- [ ] Create repository: `homelab/homelab-docs` (optional)

### 1.3 Verification

- [ ] All repositories created successfully
- [ ] SSH clone URLs work
- [ ] Web UI accessible for all repos

**GitLab URLs Created**:
```
http://10.203.3.204/homelab/infrastructure-core
http://10.203.3.204/homelab/ai-infrastructure
http://10.203.3.204/homelab/homelab-services
http://10.203.3.204/homelab/backup-infrastructure
http://10.203.3.204/homelab/homelab-docs
```

---

## Phase 2: Repository Migration

### 2.0 Setup Working Directory

- [ ] Create migration workspace
  ```bash
  mkdir -p ~/temp-migration
  cd ~/temp-migration
  ```
- [ ] Verify git-filter-repo installed
  ```bash
  git filter-repo --version
  ```

### 2.1 infrastructure-core

- [ ] Clone fresh copy
  ```bash
  git clone /Users/kellen/_Noetica/myt/_code/homelab-automation infrastructure-core
  cd infrastructure-core
  ```
- [ ] Run git filter-repo (preserve history)
  ```bash
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
  ```
- [ ] Reorganize directory structure (if needed)
- [ ] Update README.md for infrastructure-core context
- [ ] Add GitLab remote
  ```bash
  git remote add gitlab git@10.203.3.204:homelab/infrastructure-core.git
  ```
- [ ] Push to GitLab
  ```bash
  git push -u gitlab main
  ```
- [ ] Verify in GitLab Web UI

### 2.2 ai-infrastructure

- [ ] Clone fresh copy
  ```bash
  cd ~/temp-migration
  git clone /Users/kellen/_Noetica/myt/_code/homelab-automation ai-infrastructure
  cd ai-infrastructure
  ```
- [ ] Run git filter-repo
  ```bash
  git filter-repo --path ansible/roles/proxmox-nvidia-gpu \
    --path ansible/roles/nvidia-lxc-ai \
    --path ansible/host_vars/socrates.yml \
    --path services/ai-stack \
    --path services/llm-stack \
    --path README.md \
    --path CLAUDE.md
  ```
- [ ] Create ai-workstation-setup.yml playbook
- [ ] Update README.md for ai-infrastructure context
- [ ] Add GitLab remote
  ```bash
  git remote add gitlab git@10.203.3.204:homelab/ai-infrastructure.git
  ```
- [ ] Push to GitLab
  ```bash
  git push -u gitlab main
  ```
- [ ] Verify in GitLab Web UI

### 2.3 homelab-services

- [ ] Clone fresh copy
  ```bash
  cd ~/temp-migration
  git clone /Users/kellen/_Noetica/myt/_code/homelab-automation homelab-services
  cd homelab-services
  ```
- [ ] Run git filter-repo
  ```bash
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
  ```
- [ ] Create service deployment playbooks
- [ ] Update README.md for services context
- [ ] Add GitLab remote
  ```bash
  git remote add gitlab git@10.203.3.204:homelab/homelab-services.git
  ```
- [ ] Push to GitLab
  ```bash
  git push -u gitlab main
  ```
- [ ] Verify in GitLab Web UI

### 2.4 backup-infrastructure

- [ ] Clone fresh copy
  ```bash
  cd ~/temp-migration
  git clone /Users/kellen/_Noetica/myt/_code/homelab-automation backup-infrastructure
  cd backup-infrastructure
  ```
- [ ] Run git filter-repo
  ```bash
  git filter-repo --path ansible/roles/proxmox-backup-server \
    --path ansible/pbs-setup.yml \
    --path ansible/host_vars/plato.yml \
    --path README.md \
    --path CLAUDE.md
  ```
- [ ] Create backup scripts directory
- [ ] Update README.md for backup context
- [ ] Add GitLab remote
  ```bash
  git remote add gitlab git@10.203.3.204:homelab/backup-infrastructure.git
  ```
- [ ] Push to GitLab
  ```bash
  git push -u gitlab main
  ```
- [ ] Verify in GitLab Web UI

### 2.5 homelab-docs (Optional)

- [ ] Clone fresh copy
  ```bash
  cd ~/temp-migration
  git clone /Users/kellen/_Noetica/myt/_code/homelab-automation homelab-docs
  cd homelab-docs
  ```
- [ ] Run git filter-repo
  ```bash
  git filter-repo --path docs \
    --path mkdocs.yml \
    --path README.md
  ```
- [ ] Update README.md for documentation context
- [ ] Add GitLab remote
  ```bash
  git remote add gitlab git@10.203.3.204:homelab/homelab-docs.git
  ```
- [ ] Push to GitLab
  ```bash
  git push -u gitlab main
  ```
- [ ] Verify in GitLab Web UI

---

## Phase 3: Verification & Testing

### 3.1 Repository Content Verification

For each repository:
- [ ] infrastructure-core: Check all 12 roles present
- [ ] ai-infrastructure: Check 2 roles + services/
- [ ] homelab-services: Check 6 roles + services/
- [ ] backup-infrastructure: Check 1 role + playbook
- [ ] homelab-docs: Check docs/ and mkdocs.yml

### 3.2 Git History Verification

- [ ] infrastructure-core: Verify commit history preserved
- [ ] ai-infrastructure: Verify commit history preserved
- [ ] homelab-services: Verify commit history preserved
- [ ] backup-infrastructure: Verify commit history preserved

### 3.3 SSH Clone Testing

```bash
cd ~/temp-migration/testing
git clone git@10.203.3.204:homelab/infrastructure-core.git
git clone git@10.203.3.204:homelab/ai-infrastructure.git
git clone git@10.203.3.204:homelab/homelab-services.git
git clone git@10.203.3.204:homelab/backup-infrastructure.git
```

- [ ] All repositories clone successfully
- [ ] File structure correct in each repo
- [ ] Ansible directory structure intact

### 3.4 Ansible Playbook Testing

- [ ] infrastructure-core: Test with `--check` mode
  ```bash
  cd infrastructure-core
  ansible-playbook -i inventory-prod.ini site.yml --check --limit zeno
  ```
- [ ] ai-infrastructure: Test with `--check` mode
  ```bash
  cd ai-infrastructure
  ansible-playbook -i inventory.ini ai-workstation-setup.yml --check --limit socrates
  ```
- [ ] homelab-services: Test individual playbooks
  ```bash
  cd homelab-services
  ansible-playbook deploy-gitlab.yml --check
  ```
- [ ] backup-infrastructure: Test PBS playbook
  ```bash
  cd backup-infrastructure
  ansible-playbook pbs-setup.yml --check --limit plato
  ```

### 3.5 Cross-Repository Testing

- [ ] Verify inventory files work independently
- [ ] Check for any broken role dependencies
- [ ] Test that shared variables still accessible

---

## Phase 4: Documentation Updates

### 4.1 Update READMEs

- [ ] infrastructure-core: Add repo-specific overview
- [ ] ai-infrastructure: Document GPU setup workflow
- [ ] homelab-services: List all services with URLs
- [ ] backup-infrastructure: Document backup procedures
- [ ] homelab-docs: Add index of all repositories

### 4.2 Cross-Repository Links

- [ ] Link from infrastructure-core to ai-infrastructure
- [ ] Link from infrastructure-core to homelab-services
- [ ] Link from all repos to homelab-docs
- [ ] Update migration plan with actual results

### 4.3 Update CLAUDE.md

- [ ] infrastructure-core: Add infrastructure-specific instructions
- [ ] ai-infrastructure: Add AI/GPU-specific instructions
- [ ] homelab-services: Add service deployment instructions
- [ ] backup-infrastructure: Add backup/recovery instructions

---

## Phase 5: Monorepo Deprecation

### 5.1 Archive Original Repository

- [ ] Add deprecation notice to README.md
  ```markdown
  # ⚠️ REPOSITORY MIGRATED

  This repository has been split into functional repositories:
  - Infrastructure: http://10.203.3.204/homelab/infrastructure-core
  - AI Workloads: http://10.203.3.204/homelab/ai-infrastructure
  - Services: http://10.203.3.204/homelab/homelab-services
  - Backups: http://10.203.3.204/homelab/backup-infrastructure

  This repository is archived for reference only.
  Last active: 2025-12-13
  ```
- [ ] Commit deprecation notice
- [ ] Create git tag: `v1.0-archived`
- [ ] Move to archived location
  ```bash
  mv /Users/kellen/_Noetica/myt/_code/homelab-automation \
     /Users/kellen/_Noetica/myt/_code/homelab-automation-archived
  ```

### 5.2 Safety Net

- [ ] Keep archived monorepo for 3-6 months
- [ ] Create git bundle backup
  ```bash
  cd /Users/kellen/_Noetica/myt/_code/homelab-automation-archived
  git bundle create ~/backups/homelab-automation-backup.bundle --all
  ```
- [ ] Store bundle in safe location
- [ ] Document restore procedure

---

## Phase 6: Workflow Transition

### 6.1 Clone New Repositories

- [ ] Clone infrastructure-core to working location
  ```bash
  cd /Users/kellen/_Noetica/myt/_code
  git clone git@10.203.3.204:homelab/infrastructure-core.git
  ```
- [ ] Clone ai-infrastructure
- [ ] Clone homelab-services
- [ ] Clone backup-infrastructure
- [ ] Update workspace organization

### 6.2 Update Automation Scripts

- [ ] Update any deployment scripts referencing old paths
- [ ] Update CI/CD references (if any)
- [ ] Update documentation references

### 6.3 Workflow Documentation

- [ ] Document new clone workflow
- [ ] Document multi-repo development process
- [ ] Document when to use each repository

---

## Success Criteria

- [ ] All 4-5 repositories successfully created in GitLab
- [ ] Git history preserved where intended
- [ ] All Ansible playbooks pass `--check` validation
- [ ] SSH clone/push/pull works for all repos
- [ ] Documentation updated and cross-linked
- [ ] Original monorepo archived safely
- [ ] New workflow documented

---

## Rollback Procedure (If Needed)

If migration encounters critical issues:

1. [ ] Stop migration process
2. [ ] Delete GitLab repositories via Web UI
3. [ ] Original monorepo remains unchanged at:
   `/Users/kellen/_Noetica/myt/_code/homelab-automation/`
4. [ ] Clean up temp migration directory:
   ```bash
   rm -rf ~/temp-migration
   ```
5. [ ] Review migration plan, adjust, retry

---

## Notes & Issues

(Use this section to track any issues encountered during migration)

**Date**: 2025-12-13
**Issue**: (none yet)
**Resolution**: (n/a)

---

## Completion Status

**Started**: (not yet)
**Completed**: (not yet)
**Duration**: (TBD)

---

## Post-Migration Tasks

(After all phases complete)

- [ ] Set up CI/CD pipelines per repository
- [ ] Configure branch protection rules
- [ ] Create Ansible collection for shared code
- [ ] Implement dynamic inventory from NetBox
- [ ] Schedule periodic sync checks
- [ ] Delete temp migration directory
- [ ] Delete archived monorepo (after 3-6 months)

---

**Documents**:
- Migration Plan: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-migration-plan.md`
- GitLab Access: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-access.md`
- Repository Structure: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/repository-structure.md`
- This Checklist: `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/MIGRATION-CHECKLIST.md`
