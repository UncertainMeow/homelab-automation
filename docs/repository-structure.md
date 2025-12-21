# Repository Structure Diagram

This document provides visual representation of the proposed GitLab repository organization.

---

## Current State: Monorepo

```
homelab-automation/ (Current)
├── ansible/
│   ├── roles/
│   │   ├── proxmox-base              ──┐
│   │   ├── user-management            │
│   │   ├── proxmox-community-scripts  │
│   │   ├── proxmox-pci-passthrough    │ Infrastructure
│   │   ├── proxmox-cluster            │ Foundation
│   │   ├── thunderbolt-ring           │ (12 roles)
│   │   ├── nfs-storage                │
│   │   ├── proxmox-backup-client      │
│   │   ├── vm-templates               │
│   │   ├── lxc-templates              │
│   │   ├── dotfiles-portable          │
│   │   ├── infra-snapshot            ──┘
│   │   ├── proxmox-nvidia-gpu        ──┐ AI/GPU
│   │   ├── nvidia-lxc-ai             ──┘ (2 roles)
│   │   ├── gitlab                    ──┐
│   │   ├── netbox                     │
│   │   ├── netbox-dns-sync            │ Services
│   │   ├── technitium-dns             │ (6 roles)
│   │   ├── docs-site                  │
│   │   ├── tailscale-subnet-router   ──┘
│   │   └── proxmox-backup-server     ──> Backup (1 role)
│   ├── host_vars/
│   │   ├── socrates.yml              ──> AI workstation
│   │   ├── plato.yml                 ──> PBS
│   │   └── ...                       ──> Other hosts
│   ├── group_vars/
│   ├── inventory-prod.ini
│   └── *.yml (playbooks)
├── services/
│   ├── ai-stack/                     ──> AI workloads
│   ├── llm-stack/                    ──> AI workloads
│   ├── gitlab-stack/                 ──> Services
│   ├── dns-stack/                    ──> Services
│   └── netbox-stack/                 ──> Services
├── docs/
├── mkdocs.yml
└── README.md
```

---

## Future State: Functional Split

```
GitLab: http://10.203.3.204/homelab/
│
├── infrastructure-core/
│   ├── roles/
│   │   ├── proxmox-base
│   │   ├── user-management
│   │   ├── proxmox-community-scripts
│   │   ├── proxmox-pci-passthrough
│   │   ├── proxmox-cluster
│   │   ├── thunderbolt-ring
│   │   ├── nfs-storage
│   │   ├── proxmox-backup-client
│   │   ├── vm-templates
│   │   ├── lxc-templates
│   │   ├── dotfiles-portable
│   │   └── infra-snapshot
│   ├── host_vars/          (all hosts)
│   ├── group_vars/
│   ├── inventory-prod.ini
│   ├── site.yml
│   ├── cluster-setup.yml
│   ├── cluster-base-config.yml
│   ├── cluster-post-install.yml
│   ├── pve-backup-setup.yml
│   └── README.md
│
├── ai-infrastructure/
│   ├── roles/
│   │   ├── proxmox-nvidia-gpu
│   │   └── nvidia-lxc-ai
│   ├── services/
│   │   ├── ai-stack/
│   │   └── llm-stack/
│   ├── host_vars/
│   │   └── socrates.yml
│   ├── inventory.ini       (subset: socrates)
│   ├── ai-workstation-setup.yml
│   ├── scripts/
│   │   └── socrates-ai     (GPU mode switching)
│   └── README.md
│
├── homelab-services/
│   ├── roles/
│   │   ├── gitlab
│   │   ├── netbox
│   │   ├── netbox-dns-sync
│   │   ├── technitium-dns
│   │   ├── docs-site
│   │   └── tailscale-subnet-router
│   ├── services/
│   │   ├── gitlab-stack/
│   │   ├── dns-stack/
│   │   └── netbox-stack/
│   ├── inventory.ini       (subset: service hosts)
│   ├── deploy-gitlab.yml
│   ├── deploy-netbox.yml
│   ├── deploy-dns.yml
│   └── README.md
│
├── backup-infrastructure/
│   ├── roles/
│   │   └── proxmox-backup-server
│   ├── host_vars/
│   │   └── plato.yml
│   ├── inventory.ini       (subset: plato)
│   ├── pbs-setup.yml
│   ├── scripts/
│   │   ├── backup-verification.sh
│   │   └── disaster-recovery.sh
│   ├── docs/
│   │   ├── backup-procedures.md
│   │   └── recovery-runbooks.md
│   └── README.md
│
└── homelab-docs/ (OPTIONAL)
    ├── docs/
    │   ├── architecture/
    │   ├── guides/
    │   └── reference/
    ├── mkdocs.yml
    └── README.md
```

---

## Repository Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    homelab (GitLab Group)                   │
└─────────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ infrastructure-  │  │ ai-              │  │ homelab-         │
│ core             │  │ infrastructure   │  │ services         │
│                  │  │                  │  │                  │
│ • Base system    │  │ • NVIDIA GPU     │  │ • GitLab         │
│ • Cluster setup  │  │ • AI containers  │  │ • DNS            │
│ • Hardware       │  │ • LLM stacks     │  │ • NetBox         │
│ • Storage        │  │                  │  │ • Tailscale      │
│                  │  │ Depends on:      │  │                  │
│ Primary repo     │  │ infrastructure-  │  │ Depends on:      │
│ Run first        │  │ core (for base)  │  │ infrastructure-  │
│                  │  │                  │  │ core (for LXC)   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                                            │
         │                                            │
         ▼                                            ▼
┌──────────────────┐                        ┌──────────────────┐
│ backup-          │                        │ homelab-docs     │
│ infrastructure   │                        │ (OPTIONAL)       │
│                  │                        │                  │
│ • PBS setup      │                        │ • Architecture   │
│ • Automation     │                        │ • Guides         │
│ • Recovery       │                        │ • Reference      │
│                  │                        │                  │
│ Depends on:      │                        │ Cross-links all  │
│ infrastructure-  │                        │ repositories     │
│ core (for PBS    │                        │                  │
│ client role)     │                        │                  │
└──────────────────┘                        └──────────────────┘
```

---

## Dependency Flow

```
Typical Deployment Order:
═══════════════════════════════════════════════════════════════

1. infrastructure-core
   │
   ├─> Clone & run cluster-setup.yml
   │   • Sets up Proxmox base
   │   • Creates users
   │   • Configures networking
   │   • Enables PCI passthrough
   │
   ✓ All nodes ready

2. ai-infrastructure (if GPU nodes exist)
   │
   ├─> Clone & run ai-workstation-setup.yml
   │   • Installs NVIDIA drivers
   │   • Creates GPU containers
   │   • Deploys AI services
   │
   ✓ AI workloads operational

3. homelab-services
   │
   ├─> Clone & run deploy-*.yml playbooks
   │   • Deploy GitLab
   │   • Deploy DNS
   │   • Deploy NetBox
   │   • Configure integrations
   │
   ✓ Services operational

4. backup-infrastructure
   │
   ├─> Clone & run pbs-setup.yml
   │   • Configure PBS
   │   • Set up backup jobs
   │   • Test recovery
   │
   ✓ Backups automated

5. homelab-docs (optional)
   │
   ├─> Clone & build documentation site
   │
   ✓ Documentation published
```

---

## Host → Repository Mapping

```
Infrastructure Hosts:
═══════════════════════════════════════════════════════════════

zeno (10.203.3.49)              ──> infrastructure-core
  • Media server                    + homelab-services
  • *arr stack, Jellyfin               (for Tailscale, etc.)

rawls (10.203.3.47)             ──> infrastructure-core
  • Infra node                      + homelab-services
  • GitLab, DNS, Authentik             (GitLab, DNS roles)

socrates (10.203.3.42)          ──> infrastructure-core
  • AI workstation                  + ai-infrastructure
  • 2x Tesla P40 GPUs                  (NVIDIA, AI containers)

frege (10.203.3.11)             ──> infrastructure-core
russell (10.203.3.12)               (cluster, thunderbolt)
wittgenstein (10.203.3.13)
  • MS-01 cluster

plato (10.203.3.97)             ──> infrastructure-core
  • Proxmox Backup Server           + backup-infrastructure
                                       (PBS setup, automation)
```

---

## Shared Components Strategy

```
Problem: Multiple repos need common elements
Solution: Progressive consolidation

Phase 1 (Initial Migration):
════════════════════════════════════════════════════════
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ infrastructure- │  │ ai-             │  │ homelab-        │
│ core            │  │ infrastructure  │  │ services        │
│                 │  │                 │  │                 │
│ inventory.ini   │  │ inventory.ini   │  │ inventory.ini   │
│ (copy)          │  │ (copy subset)   │  │ (copy subset)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘

Strategy: Accept duplication for simplicity


Phase 2 (After stabilization):
════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────┐
│         homelab.common (Ansible Collection)             │
│         • Shared filters                                │
│         • Common variables                              │
│         • Utility plugins                               │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ (imported via requirements.yml)
         ┌────────────────┼────────────────┐
         │                │                │
┌────────┴────────┐  ┌────┴────────┐  ┌───┴──────────┐
│ infrastructure- │  │ ai-         │  │ homelab-     │
│ core            │  │ infrastructure│  │ services     │
└─────────────────┘  └─────────────┘  └──────────────┘

Strategy: Centralized shared code


Phase 3 (Future - Dynamic):
════════════════════════════════════════════════════════
┌─────────────────────────────────────────────────────────┐
│              NetBox (Source of Truth)                   │
│              • Dynamic Inventory                        │
│              • Infrastructure documentation             │
│              • IP address management                    │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ (ansible-inventory)
         ┌────────────────┼────────────────┐
         │                │                │
┌────────┴────────┐  ┌────┴────────┐  ┌───┴──────────┐
│ All repos query │  │ NetBox for  │  │ real-time    │
│ current state   │  │ inventory   │  │ inventory    │
└─────────────────┘  └─────────────┘  └──────────────┘

Strategy: Single source of truth
```

---

## Migration Path Visualization

```
Current Monorepo                Split Process              Result
═══════════════                 ═════════════              ══════

homelab-automation/             git filter-repo            homelab/infrastructure-core/
├─ ansible/                     (extract paths)            ├─ roles/ (12 roles)
│  ├─ roles/ (21)          ────────────────────>          ├─ inventory-prod.ini
│  │  ├─ infrastructure (12)                               ├─ site.yml
│  │  ├─ ai (2)            ────────────────────>          └─ *.yml
│  │  ├─ services (6)           ┌───────────┐
│  │  └─ backup (1)             │           │             homelab/ai-infrastructure/
│  ├─ host_vars/        ────────┤           │             ├─ roles/ (2 roles)
│  ├─ group_vars/               │  Split    │────────>    ├─ services/ai-stack/
│  ├─ inventory-prod.ini        │  Repo     │             ├─ services/llm-stack/
│  └─ *.yml                     │           │             └─ *.yml
├─ services/            ────────┤           │
│  ├─ ai-stack/                 │           │             homelab/homelab-services/
│  ├─ llm-stack/                │           │             ├─ roles/ (6 roles)
│  ├─ gitlab-stack/    ─────────┤           │────────>    ├─ services/gitlab-stack/
│  ├─ dns-stack/                │           │             ├─ services/dns-stack/
│  └─ netbox-stack/             │           │             └─ *.yml
├─ docs/                ────────┤           │
├─ mkdocs.yml                   │           │             homelab/backup-infrastructure/
└─ README.md            ────────┘           └────────>    ├─ roles/ (1 role)
                                                           ├─ scripts/
                                                           └─ docs/

                                                           homelab/homelab-docs/
                                                           ├─ docs/
                                                           └─ mkdocs.yml
```

---

## File Count Summary

```
Current Monorepo:
═════════════════════════════════════════════════════════
  21 Ansible roles
  12 Playbook files
  6 Host var files
  5 Service stacks
  ~50 Documentation files
  ────────────────────────────────────────────────────────
  Total: ~100+ files


After Split:
═════════════════════════════════════════════════════════
infrastructure-core:      ~60 files (largest)
ai-infrastructure:        ~20 files
homelab-services:         ~30 files
backup-infrastructure:    ~10 files
homelab-docs:            ~50 files (if split)
────────────────────────────────────────────────────────
Total: ~170 files (includes some duplication)
```

---

## Access Patterns

```
Developer Workflow:
═══════════════════════════════════════════════════════════

Scenario 1: New Proxmox Node Setup
┌─────────────────────────────────────────────────────┐
│ 1. Clone infrastructure-core                        │
│ 2. Update inventory-prod.ini                        │
│ 3. Run: ansible-playbook site.yml --limit newhost  │
│ 4. Commit inventory changes                         │
│ 5. Push to GitLab                                   │
└─────────────────────────────────────────────────────┘

Scenario 2: Deploy New AI Container
┌─────────────────────────────────────────────────────┐
│ 1. Clone ai-infrastructure                          │
│ 2. Update host_vars/socrates.yml                    │
│ 3. Run: ansible-playbook ai-workstation-setup.yml  │
│ 4. Deploy service stack via docker compose          │
│ 5. Commit changes, push to GitLab                   │
└─────────────────────────────────────────────────────┘

Scenario 3: Update Service Configuration
┌─────────────────────────────────────────────────────┐
│ 1. Clone homelab-services                           │
│ 2. Modify role or docker-compose.yml                │
│ 3. Run: ansible-playbook deploy-<service>.yml      │
│ 4. Test service functionality                       │
│ 5. Commit changes, push to GitLab                   │
└─────────────────────────────────────────────────────┘

Scenario 4: Complete Infrastructure Rebuild
┌─────────────────────────────────────────────────────┐
│ 1. Clone infrastructure-core                        │
│ 2. Run cluster-setup.yml                            │
│ 3. Clone ai-infrastructure (if GPU hosts)           │
│ 4. Run ai-workstation-setup.yml                     │
│ 5. Clone homelab-services                           │
│ 6. Run deploy-*.yml for each service                │
│ 7. Clone backup-infrastructure                      │
│ 8. Run pbs-setup.yml                                │
└─────────────────────────────────────────────────────┘
```

---

## Benefits of This Structure

```
┌──────────────────────────────────────────────────────────┐
│ 1. SEPARATION OF CONCERNS                                │
│    ✓ Each repo has single responsibility                 │
│    ✓ Changes isolated by function                        │
│    ✓ Easier to understand & maintain                     │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 2. INDEPENDENT VERSIONING                                │
│    ✓ AI infrastructure can evolve independently          │
│    ✓ Service updates don't affect base infrastructure    │
│    ✓ Clearer release management                          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 3. FOCUSED CI/CD                                         │
│    ✓ Test only what changed                              │
│    ✓ Faster pipeline execution                           │
│    ✓ Deploy specific components independently            │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 4. COLLABORATION                                         │
│    ✓ Grant access to specific repos only                 │
│    ✓ Reduce merge conflicts                              │
│    ✓ Parallel development on different components        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ 5. DISASTER RECOVERY                                     │
│    ✓ Clone only what's needed for recovery               │
│    ✓ Clear dependency chain for rebuild                  │
│    ✓ Backup strategies per repo criticality              │
└──────────────────────────────────────────────────────────┘
```

---

## Next Steps

See `/Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-migration-plan.md` for:
- Detailed migration commands
- Git filter-repo usage
- Testing procedures
- Rollback strategy

**Ready to begin migration when you are!**
