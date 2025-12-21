# GitLab Access Information

**Status**: Active - Password retrieved 2025-12-13
**GitLab URL**: http://10.203.3.204

---

## Login Credentials

**Username**: `root`
**Password**: Retrieved via gitlab-rake (see Reset Root Password section below)

**IMPORTANT**: Change this password after first login via Web UI:
1. Log in at http://10.203.3.204
2. Click profile icon (top right) → Preferences → Password
3. Set a new secure password

---

## SSH Access

### Container Access

```bash
# From your workstation to Proxmox host (rawls)
ssh kellen@10.203.3.47

# From rawls into GitLab container
sudo pct enter 204

# Or execute commands directly
sudo pct exec 204 -- gitlab-ctl status
```

### Git SSH Access

**GitLab SSH Port**: 22 (default within container)
**Container IP**: 10.203.3.204

```bash
# Clone repository via SSH (after adding your SSH key)
git clone git@10.203.3.204:homelab/infrastructure-core.git

# Add as remote to existing repository
git remote add gitlab git@10.203.3.204:homelab/infrastructure-core.git
```

### Add Your SSH Key

1. Log in to GitLab at http://10.203.3.204
2. Click profile icon → Preferences → SSH Keys
3. Add your public key (cogito or ergo-sum)

**Your SSH Keys** (from CLAUDE.md):
- **cogito**: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN7jefck23Q1wCFLAS3shg6uVpiOXKdVRPiPqRQc2gNz cogito`
- **ergo-sum**: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEIBPoFy/oe9j6lvXyVgnaPRb72EznbsuJQUDhQYxu2l ergo-sum`

---

## Container Information

**Proxmox Host**: rawls (10.203.3.47)
**Container VMID**: 204
**Hostname**: gitlab
**IP Address**: 10.203.3.204

---

## GitLab Management Commands

```bash
# Check service status
sudo pct exec 204 -- gitlab-ctl status

# View logs
sudo pct exec 204 -- gitlab-ctl tail

# Reconfigure after config changes
sudo pct exec 204 -- gitlab-ctl reconfigure

# Create backup
sudo pct exec 204 -- gitlab-backup create

# Stop all services
sudo pct exec 204 -- gitlab-ctl stop

# Start all services
sudo pct exec 204 -- gitlab-ctl start

# Check GitLab health
sudo pct exec 204 -- gitlab-rake gitlab:check SANITIZE=true
```

---

## Reset Root Password (If Needed)

If the above password doesn't work:

```bash
# SSH to rawls
ssh kellen@10.203.3.47

# Reset root password
sudo pct exec 204 -- gitlab-rake "gitlab:password:reset[root]"

# Follow the interactive prompts to set a new password
```

---

## Next Steps

1. **Log in** to GitLab at http://10.203.3.204 with root credentials
2. **Change password** immediately
3. **Create group**: `homelab`
4. **Create repositories**:
   - homelab/infrastructure-core
   - homelab/ai-infrastructure
   - homelab/homelab-services
   - homelab/backup-infrastructure
   - homelab/homelab-docs (optional)
5. **Add SSH key** for git operations
6. **Proceed with migration** per /Users/kellen/_Noetica/myt/_code/homelab-automation/docs/gitlab-migration-plan.md

---

## Troubleshooting

### Can't Access Web UI

```bash
# Check container is running
ssh kellen@10.203.3.47 "sudo pct status 204"

# Check GitLab services
ssh kellen@10.203.3.47 "sudo pct exec 204 -- gitlab-ctl status"

# Check for errors
ssh kellen@10.203.3.47 "sudo pct exec 204 -- gitlab-ctl tail"
```

### Git Clone/Push Fails

1. Verify SSH key is added to GitLab profile
2. Test SSH connection: `ssh -T git@10.203.3.204`
3. Check GitLab SSH service: `sudo pct exec 204 -- gitlab-ctl status sshd`

### Service Won't Start

```bash
# Reconfigure GitLab
ssh kellen@10.203.3.47 "sudo pct exec 204 -- gitlab-ctl reconfigure"

# Restart all services
ssh kellen@10.203.3.47 "sudo pct exec 204 -- gitlab-ctl restart"

# Check disk space
ssh kellen@10.203.3.47 "sudo pct exec 204 -- df -h"
```

---

**Documentation**: See gitlab-migration-plan.md for complete migration strategy
