# Agent Briefing: MS-01 Proxmox Cluster

## Mission

Build a 3-node high-availability Proxmox cluster using three MS-01 mini PCs, connected via Thunderbolt/USB4 for high-speed inter-node communication.

## Business Outcomes (Success Criteria)

- [ ] 3-node Proxmox VE cluster operational
- [ ] High-speed Thunderbolt ring network between nodes
- [ ] Ceph or other shared storage configured
- [ ] VMs can live-migrate between nodes
- [ ] Cluster survives single node failure
- [ ] Independent of Socrates - can run workloads standalone
- [ ] Ansible-driven deployment (idempotent, reproducible)

## Network Topology

```
Cluster Nodes:
- Frege: 10.203.3.11 (MS-01)
- Russell: 10.203.3.12 (MS-01)
- Wittgenstein: 10.203.3.13 (MS-01)

Networks:
1. Management Network: 10.203.3.x (standard LAN)
2. Cluster Network: Thunderbolt ring (high-speed, dedicated)
   - Frege ←→ Russell ←→ Wittgenstein ←→ Frege (ring topology)

Starting State: Bare metal - fresh Proxmox installs needed
```

## Reference Materials

### Existing Thunderbolt Role
Location: `/Users/kellen/_Noetica/myt/_code/homelab-automation/ansible/roles/thunderbolt-ring/`

This role was already created for MS-01 cluster networking - review and use it.

### Existing Infrastructure Patterns
Location: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`

- `ansible/site.yml` - Main playbook structure
- `ansible/host_vars/socrates.yml` - Example host config (GPU-focused but good pattern)
- `ansible/roles/proxmox-base/` - Base Proxmox configuration
- `ansible/roles/user-management/` - User setup
- `CLAUDE.md` - SSH keys and user standards

### Key Standards
- Primary user: `kellen` with full sudo, SSH-key only
- Automation user: `ansible` with passwordless sudo
- SSH keys documented in `CLAUDE.md`

## Constraints

1. **Fresh installs**: All three nodes need Proxmox VE installed
2. **Ansible-driven**: Create/update roles as needed
3. **Feature branch**: Work in `feature/ms01-cluster` branch
4. **Thunderbolt networking**: Use existing `thunderbolt-ring` role
5. **Cluster quorum**: Need all 3 nodes for proper HA

## What NOT To Do

1. **Don't create cluster with only 1-2 nodes** - quorum requires 3
2. **Don't skip the Thunderbolt network** - standard LAN isn't fast enough for Ceph
3. **Don't mix Proxmox versions** - all nodes should run same version
4. **Don't rush Ceph setup** - get cluster working first, then add storage
5. **Don't ignore network bonding/failover** - management network should be reliable

## Suggested Approach

### Phase 1: Proxmox Installation
1. Install Proxmox VE on all three MS-01 nodes
2. Basic network configuration (management network)
3. SSH key setup for kellen and ansible users
4. Run base playbooks (proxmox-base, user-management)

### Phase 2: Cluster Formation
1. Create cluster on Frege (first node)
2. Join Russell and Wittgenstein
3. Verify cluster health in web UI
4. Test node communication

### Phase 3: Thunderbolt Network
1. Connect Thunderbolt cables in ring topology
2. Run thunderbolt-ring role
3. Configure cluster network to use Thunderbolt
4. Verify high-speed connectivity

### Phase 4: Shared Storage (Ceph)
1. Identify available disks on each node
2. Deploy Ceph monitors
3. Deploy Ceph OSDs
4. Create Ceph pool for VMs
5. Test VM creation on shared storage

### Phase 5: HA Configuration
1. Enable HA in cluster
2. Create HA group
3. Test VM failover
4. Document recovery procedures

## Deliverables

1. `ansible/host_vars/frege.yml` - Frege configuration
2. `ansible/host_vars/russell.yml` - Russell configuration
3. `ansible/host_vars/wittgenstein.yml` - Wittgenstein configuration
4. `ansible/roles/proxmox-cluster/` - Cluster formation role
5. `ansible/roles/ceph-cluster/` - Ceph deployment role (if not using existing)
6. Updated inventory with cluster nodes
7. Documentation in `docs/cluster-setup.md`

## Hardware Questions to Answer

- MS-01 specs? (CPU, RAM, disk count/size)
- Thunderbolt 3 or Thunderbolt 4/USB4?
- How many disks per node for Ceph?
- NVMe or SATA?

## Cluster Naming

Following the philosopher theme:
- **Frege** - Gottlob Frege (logic, philosophy of language)
- **Russell** - Bertrand Russell (logic, analytic philosophy)
- **Wittgenstein** - Ludwig Wittgenstein (language, logic)

All three worked on foundations of logic and language - fitting for a cluster that needs clear communication!

## Communication

When complete, report back with:
1. Cluster status (all nodes joined?)
2. Thunderbolt network bandwidth (test results)
3. Ceph pool status and capacity
4. How to access cluster management
5. HA test results (did failover work?)
6. Any issues encountered
7. Recommended next steps
