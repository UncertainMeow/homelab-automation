# Runbooks

This page contains operational procedures for common tasks.

## Daily Operations

### Check Service Status

```bash
# SSH to Proxmox host
ssh kellen@10.203.3.42

# List all containers
pct list

# Check specific container
pct status 201
```

### Access Container Console

```bash
# From Proxmox host
pct enter 201  # ai-gpu0
pct enter 202  # ai-gpu1
```

### Restart a Service

```bash
# Enter the container
pct enter 201

# Restart Docker service (if using Docker inside)
systemctl restart docker

# Or restart specific container
docker restart ollama
```

---

## Backup Operations

### Manual Backup

```bash
# From any Proxmox node with PBS configured
vzdump 201 --storage pbs --mode snapshot
```

### Check Backup Status

Access PBS web UI at [https://10.203.3.97:8007](https://10.203.3.97:8007)

### Restore from Backup

```bash
# List available backups
pvesm list pbs

# Restore (will prompt for options)
qmrestore <backup-file> <new-vmid>
```

---

## Network Troubleshooting

### DNS Not Resolving

1. Check if DNS container is running:
   ```bash
   ssh kellen@10.203.3.47
   pct status 203
   ```

2. Test DNS directly:
   ```bash
   dig @10.203.3.203 ollama.hq.doofus.co
   ```

3. Check Technitium logs:
   ```bash
   pct enter 203
   docker logs technitium-dns
   ```

### Can't Reach a Service

1. Verify container is running
2. Check container has correct IP (`pct exec <vmid> ip addr`)
3. Check service is listening (`pct exec <vmid> ss -tlnp`)
4. Check firewall isn't blocking (unlikely on trusted network)

---

## GPU Troubleshooting

### GPU Not Visible in Container

```bash
# On Socrates host
nvidia-smi  # Should show GPUs

# Check container config
cat /etc/pve/lxc/201.conf | grep -i nvidia

# Inside container
nvidia-smi  # Should also show GPUs
```

### Ollama Not Using GPU

```bash
# Inside ai-gpu0 container
pct enter 201

# Check Ollama sees GPU
ollama run llama3.1:8b
# First response will show if GPU is being used

# Check CUDA
nvidia-smi
```

---

## Disaster Recovery

### Host Won't Boot

1. Check physical hardware (power, drives, network)
2. Boot from Proxmox USB installer in rescue mode
3. If hardware OK, restore from PBS backup

### Complete Rebuild

```bash
# After fresh Proxmox install
cd homelab-automation/ansible

# Bootstrap users first
ansible-playbook -i inventory-prod.ini site.yml \
  --limit <hostname> \
  -e ansible_user=root \
  --tags users

# Then run full playbook
ansible-playbook -i inventory-prod.ini site.yml --limit <hostname>
```

### Restore Specific Container

1. Access PBS web UI
2. Select the backup
3. Click Restore
4. Choose target node and VMID

---

## Adding to This Document

When you solve a new problem, add it here so future-you (or the AI assistant) knows how to handle it.
