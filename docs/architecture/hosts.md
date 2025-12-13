# Hosts

This page describes each physical server in the homelab.

## Active Hosts

### Socrates - AI Workstation

| | |
|---|---|
| **IP Address** | 10.203.3.42 |
| **Hardware** | Dell PowerEdge R730 |
| **CPUs** | 2x Intel Xeon (many cores) |
| **RAM** | 128GB+ |
| **GPUs** | 2x NVIDIA Tesla P40 (24GB each) |
| **Role** | AI/ML workloads |

**What it does**: Socrates is the powerhouse for AI workloads. The two Tesla P40 GPUs provide 48GB of combined video memory, enough to run large language models locally. This is where Ollama (our local ChatGPT alternative) runs.

**Containers on Socrates**:

- `ai-gpu0` (10.203.3.184) - Ollama + Open WebUI with 1x GPU
- `ai-unified` - Container with access to both GPUs for larger models
- `ai-gpu1` (10.203.3.153) - Karakeep AI bookmarking with 1x GPU

---

### Rawls - Infrastructure Node

| | |
|---|---|
| **IP Address** | 10.203.3.47 |
| **Hardware** | Standard Proxmox server |
| **Role** | Core infrastructure services |

**What it does**: Rawls hosts the "boring but essential" infrastructure - things that other services depend on but you rarely interact with directly.

**Services on Rawls**:

- **GitLab** (10.203.3.204) - Code repository and CI/CD
- **Technitium DNS** (10.203.3.203) - Local DNS server
- **Netbox** (10.203.3.201) - IP address management

---

### Plato - Backup Server

| | |
|---|---|
| **IP Address** | 10.203.3.97 |
| **Software** | Proxmox Backup Server |
| **Role** | Centralized backups |

**What it does**: Plato runs Proxmox Backup Server (PBS), which automatically backs up all virtual machines and containers from other hosts. If anything fails, we can restore from Plato's backups.

**Key feature**: Plato is intentionally separate from the main infrastructure. Even if Socrates or Rawls completely fail, Plato has copies of everything.

---

## Planned Hosts (Not Yet Active)

### MS-01 High-Availability Cluster

Three Minisforum MS-01 mini PCs that will form a high-availability cluster:

| Name | IP Address | Role |
|------|------------|------|
| **Frege** | 10.203.3.11 | Cluster primary |
| **Russell** | 10.203.3.12 | Cluster member |
| **Wittgenstein** | 10.203.3.13 | Cluster member |

**What it will do**: These three nodes will run as a Proxmox cluster with shared storage. If any one node fails, the others automatically take over its workloads. They're connected via high-speed Thunderbolt networking (~25 Gbps) for fast data synchronization.

**Status**: Hardware acquired, awaiting fresh Proxmox installation and cluster setup.

---

## Naming Convention

All hosts are named after philosophers:

- **Socrates** - Greek philosopher, known for questioning everything (fitting for AI that answers questions)
- **Rawls** - John Rawls, political philosopher
- **Plato** - Student of Socrates, preserved knowledge (fitting for backups)
- **Frege**, **Russell**, **Wittgenstein** - Logicians and philosophers of mathematics (fitting for a logical, redundant cluster)
