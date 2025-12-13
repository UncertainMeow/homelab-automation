# Architecture Overview

This page explains how all the pieces of the homelab fit together.

## Network Diagram

```
                            ┌─────────────────┐
                            │    Internet     │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │     Router      │
                            │   10.203.3.1    │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
           ┌────────▼────────┐ ┌─────▼─────┐ ┌───────▼───────┐
           │    Socrates     │ │   Rawls   │ │     Plato     │
           │  AI Workstation │ │   Infra   │ │    Backups    │
           │   10.203.3.42   │ │ 10.203.3.47│ │  10.203.3.97  │
           └────────┬────────┘ └─────┬─────┘ └───────────────┘
                    │                │
        ┌───────────┼───────────┐    │
        │           │           │    │
   ┌────▼───┐ ┌─────▼────┐ ┌────▼───┐│
   │ai-gpu0 │ │ai-unified│ │ai-gpu1 ││    ┌─────────────────────────────┐
   │ Ollama │ │  2x GPU  │ │Karakeep││    │      MS-01 HA Cluster       │
   └────────┘ └──────────┘ └────────┘│    │  (Future - Not Yet Active)  │
                                     │    │                             │
                            ┌────────▼────────┐  │  Frege    10.203.3.11  │
                            │    Services     │  │  Russell  10.203.3.12  │
                            │  GitLab, DNS,   │  │  Wittgen. 10.203.3.13  │
                            │  Netbox, etc.   │  └─────────────────────────┘
                            └─────────────────┘
```

## The Three Layers

### 1. Physical Hosts (Proxmox Servers)

These are the actual physical servers. Each runs **Proxmox VE**, which is software that allows one server to run many virtual machines and containers.

| Host | Hardware | Primary Role |
|------|----------|--------------|
| **Socrates** | Dell R730, 2x Tesla P40 GPUs | AI/ML workloads |
| **Rawls** | Proxmox node | Infrastructure services |
| **Plato** | Proxmox Backup Server | Backup storage |

### 2. Containers (LXC)

Inside each Proxmox host, we run **containers**. These are lightweight isolated environments - like mini-servers inside the server. They share the host's operating system kernel but are otherwise independent.

Containers are used for services that need direct hardware access (like GPUs) or high performance.

### 3. Docker Services

Inside some containers, we run **Docker**, which provides another layer of isolation for applications. Docker is great for running pre-packaged applications that someone else has built.

## Why This Structure?

**Efficiency**: One powerful server can run dozens of services instead of needing separate hardware for each.

**Isolation**: If one service crashes or gets compromised, it can't affect the others.

**Flexibility**: Services can be moved between hosts, backed up, or restored independently.

**Hardware Access**: Containers can directly use GPUs and other hardware, which virtual machines handle less efficiently.

## Network Addressing

All devices are on the `10.203.3.x` network:

- `.1` - Router/Gateway
- `.11-.13` - MS-01 cluster nodes
- `.42` - Socrates (main AI host)
- `.47` - Rawls (infrastructure)
- `.97` - Plato (backups)
- `.184`, `.201-.204` - Various containers

## Automation

Everything is managed through **Ansible playbooks** stored in this repository. When we need to:

- Add a new service → Write a role, run the playbook
- Update configurations → Edit the files, run the playbook
- Rebuild after failure → Run the playbook on fresh install

This "Infrastructure as Code" approach means the documentation and the actual configuration are always in sync.
