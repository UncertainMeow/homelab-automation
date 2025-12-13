# Services

This page lists all services available on the homelab network.

## AI Services

### Ollama + Open WebUI

| | |
|---|---|
| **URL** | [http://10.203.3.184:8080](http://10.203.3.184:8080) |
| **Host** | Socrates → ai-gpu0 container |
| **What it is** | A ChatGPT-like interface for local AI models |

**How to use**: Open the URL in your browser. You can chat with various AI models without any data leaving the network.

**Available models**:

- `llama3.1:8b` - General purpose chat, good balance of speed and quality
- `mistral:7b` - Fast general chat
- `llava:7b` - Can understand images (upload a photo and ask questions about it)

---

### Karakeep

| | |
|---|---|
| **URL** | [http://10.203.3.153:3000](http://10.203.3.153:3000) |
| **Host** | Socrates → ai-gpu1 container |
| **What it is** | AI-powered bookmarking and knowledge management |

**How to use**: Save web pages and documents. Karakeep uses AI to automatically summarize, tag, and make them searchable.

---

## Infrastructure Services

### GitLab

| | |
|---|---|
| **URL** | [http://10.203.3.204](http://10.203.3.204) |
| **Host** | Rawls → gitlab container |
| **What it is** | Self-hosted GitHub alternative |

**How to use**: Create accounts, store code repositories, run CI/CD pipelines. Works like GitHub but runs entirely on our network.

---

### Technitium DNS

| | |
|---|---|
| **URL** | [http://10.203.3.203:5380](http://10.203.3.203:5380) (admin) |
| **Host** | Rawls → dns container |
| **What it is** | Local DNS server |

**What it does**: Translates hostnames to IP addresses on the local network. Instead of typing `10.203.3.184`, you can use `ollama.hq.doofus.co`.

**Note**: Your device needs to use this DNS server (configured via router or manually) for local hostnames to work.

---

### Netbox

| | |
|---|---|
| **URL** | [http://10.203.3.201:8080](http://10.203.3.201:8080) |
| **Host** | Rawls → netbox container |
| **What it is** | IP Address Management (IPAM) and documentation |

**What it does**: Tracks which IP addresses are assigned to what, documents network infrastructure, and syncs with DNS so records stay accurate.

---

### Documentation Site (This Site)

| | |
|---|---|
| **URL** | [http://10.203.3.205:8000](http://10.203.3.205:8000) |
| **Host** | Rawls → docs container |
| **What it is** | This documentation website |

**What it does**: Serves the homelab documentation you're reading right now. Auto-updates from the git repository every 15 minutes.

---

## Management Interfaces

### Proxmox Web UI

Each Proxmox host has a web management interface:

| Host | URL |
|------|-----|
| Socrates | [https://10.203.3.42:8006](https://10.203.3.42:8006) |
| Rawls | [https://10.203.3.47:8006](https://10.203.3.47:8006) |

**What it does**: View and manage virtual machines and containers, monitor resource usage, access container consoles.

!!! warning "HTTPS Certificate Warning"
    Your browser will show a security warning because these use self-signed certificates. This is normal for local management interfaces - click through to proceed.

---

### Proxmox Backup Server

| | |
|---|---|
| **URL** | [https://10.203.3.97:8007](https://10.203.3.97:8007) |
| **Host** | Plato |
| **What it is** | Backup management interface |

**What it does**: View backup status, restore files or entire machines, manage retention policies.

---

## Service Status

To check if services are running, you can:

1. **Try the URL** - If the page loads, it's working
2. **Check Proxmox** - Log into the host's Proxmox UI and check container status
3. **SSH to host** - Run `pct list` to see container states

---

## Adding New Services

All services are defined in Ansible and deployed automatically. To add a new service:

1. Check the [Setup Guides](../guides/dns-netbox.md) for existing patterns
2. Create or modify the appropriate Ansible role
3. Run the playbook to deploy

See the [Reference](../reference/roles.md) section for technical details.
