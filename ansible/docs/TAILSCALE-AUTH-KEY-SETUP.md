# Tailscale Auth Key Setup Guide

Complete guide to setting up automated Tailscale authentication for your emergency beacon.

## Why Auth Keys?

**Problem**: Default Tailscale setup requires clicking a URL to authorize devices. In an emergency where you can't access your Proxmox host locally, this creates a chicken-and-egg problem.

**Solution**: Reusable auth keys allow automated authentication, so your beacon "just works" even when you can't access the host.

---

## Step 1: Generate Auth Key

### Via Web UI (Recommended)

1. Go to [Tailscale Admin Console](https://login.tailscale.com/admin/settings/keys)
2. Click **"Generate auth key"**
3. Configure settings:
   - **Reusable**: ✅ Yes (same key for multiple beacons)
   - **Ephemeral**: ❌ No (beacon should persist)
   - **Preauthorized**: ✅ Yes (no manual approval)
   - **Tags**: `tag:beacon` (for ACL policies)
   - **Expiry**: 90 days (rotate quarterly)
4. Click **"Generate key"**
5. Copy the key: `tskey-auth-xxxxxxxxxxxxx-yyyyyyyyyyyyyy`

### Via CLI (Alternative)

```bash
tailscale up --authkey=$(tailscale gen-authkey \
  --reusable \
  --preauthorized \
  --tags=tag:beacon \
  --expiry=90d)
```

---

## Step 2: Store Securely in Ansible Vault

### Create Encrypted Vault File

```bash
cd /path/to/homelab-automation/ansible

# Copy the template
cp group_vars/vault.yml.example group_vars/vault.yml

# Edit and add your key
vim group_vars/vault.yml

# Add:
tailscale_auth_key: "tskey-auth-xxxxxxxxxxxxx-yyyyyyyyyyyyyy"

# Encrypt the file
ansible-vault encrypt group_vars/vault.yml
# Enter a strong password when prompted
```

### Store Vault Password Securely

**Option 1: Password file** (local development only)
```bash
echo "your-vault-password" > ~/.ansible-vault-pass
chmod 600 ~/.ansible-vault-pass

# Add to ansible.cfg
vault_password_file = ~/.ansible-vault-pass
```

**Option 2: Environment variable**
```bash
export ANSIBLE_VAULT_PASSWORD="your-vault-password"
```

**Option 3: Password prompt** (most secure)
```bash
# Ansible will prompt for password
ansible-playbook site.yml --ask-vault-pass
```

---

## Step 3: Configure Tailscale ACLs

Apply least-privilege policies to your beacons.

### Edit ACLs

Go to [Tailscale ACL Editor](https://login.tailscale.com/admin/acls)

### Add Tag Owner

```json
{
  "tagOwners": {
    "tag:beacon": ["autogroup:admin"]
  }
}
```

### Add ACL Rules

```json
{
  "acls": [
    {
      "action": "accept",
      "src": ["autogroup:admin"],
      "dst": ["tag:beacon:*"]
    },
    {
      "action": "accept",
      "src": ["tag:beacon"],
      "dst": ["autogroup:admin:*"]
    }
  ]
}
```

**What this does:**
- Admins can access beacons
- Beacons can access admin-owned devices (your homelab)
- Beacons cannot access other Tailscale devices

---

## Step 4: Test the Setup

### Run the Playbook

```bash
cd ansible/

# Deploy to one node first
ansible-playbook -i inventory.ini site.yml \
  --tags tailscale-router \
  --limit test-node \
  --ask-vault-pass
```

### Verify Beacon

```bash
# From your Proxmox host
pct list | grep beacon

# Check Tailscale status
pct exec 200 -- tailscale status

# Should show connected with routes advertised
```

### Enable Subnet Routes

1. Go to [Tailscale Machines](https://login.tailscale.com/admin/machines)
2. Find your beacon: `tailscale-beacon`
3. Click the **three dots** → **Edit route settings**
4. Enable subnet routes: `10.203.0.0/16`
5. Save

### Test Emergency Access

```bash
# From anywhere on your Tailscale network
ssh root@tailscale-beacon

# From beacon, access Proxmox
ssh root@10.203.3.42

# Success! Emergency access works!
```

---

## Security Best Practices

### 1. Key Rotation

**Rotate auth keys quarterly:**

```bash
# Generate new key (Tailscale admin console)
# Update vault
vim group_vars/vault.yml
ansible-vault encrypt group_vars/vault.yml

# Redeploy beacons
ansible-playbook site.yml --tags tailscale-router --ask-vault-pass

# Revoke old key (Tailscale admin console)
```

### 2. Limit Key Scope

- Use **tags** to apply specific ACL policies
- Set **expiry** (90 days recommended)
- Mark as **preauthorized** only for beacons
- Don't use same key for production services

### 3. Protect Vault File

```bash
# Never commit unencrypted vault
git add group_vars/vault.yml  # Only if encrypted!

# Verify encryption
file group_vars/vault.yml
# Should output: "ASCII text" (encrypted) not "YAML"

# Add to .gitignore (just in case)
echo "group_vars/vault.yml.decrypted" >> .gitignore
```

### 4. Audit Access

Regularly check Tailscale logs:
1. [Tailscale Admin](https://login.tailscale.com/admin/machines)
2. Click beacon machine
3. Review **Activity** tab
4. Look for unexpected connections

---

## Troubleshooting

### Beacon won't authenticate

**Check auth key:**
```bash
# Decrypt vault and verify key
ansible-vault view group_vars/vault.yml

# Test key manually
pct exec 200 -- tailscale up --authkey=tskey-auth-xxxxxxxxxxxxx
```

**Common issues:**
- Key expired (check admin console)
- Key not reusable (regenerate with --reusable)
- Typo in key (copy-paste carefully)

### Routes not working

**Enable on Tailscale side:**
1. Admin console → Machines
2. Find beacon
3. Edit route settings
4. ✅ Enable subnet routes

**Check container config:**
```bash
# Verify IP forwarding
pct exec 200 -- sysctl net.ipv4.ip_forward
# Should be: net.ipv4.ip_forward = 1

# Verify routes advertised
pct exec 200 -- tailscale status
# Should show: "advertising routes: 10.203.0.0/16"
```

### Can't decrypt vault

```bash
# Wrong password
ansible-vault view group_vars/vault.yml
# Enter correct password

# Reset if forgotten (requires re-entering all secrets)
ansible-vault decrypt group_vars/vault.yml
# Enter old password

ansible-vault encrypt group_vars/vault.yml
# Enter new password
```

---

## Alternative: Manual Authentication

If you prefer not to use auth keys:

```yaml
# group_vars/proxmox.yml
tailscale_auth_method: "manual"
```

**Process:**
1. Playbook creates beacon
2. Playbook outputs authorization URL
3. You click URL and approve
4. Enable subnet routes manually

**Trade-off**: More secure (no stored keys) but requires manual step during deployment.

---

## Key Rotation Schedule

| Task | Frequency | Action |
|------|-----------|--------|
| **Rotate auth keys** | Quarterly (90 days) | Generate new, update vault, redeploy |
| **Audit beacon access** | Monthly | Check Tailscale activity logs |
| **Review ACLs** | Quarterly | Verify least-privilege policies |
| **Test emergency access** | Monthly | Verify beacon works from external network |

---

## Next Steps

1. ✅ Generate reusable auth key
2. ✅ Store in encrypted vault
3. ✅ Configure ACLs
4. ✅ Deploy beacon
5. ✅ Test emergency access
6. 📅 Set calendar reminder for quarterly rotation

Your emergency beacon is now a fully automated, secure backdoor to your homelab! 🚨
