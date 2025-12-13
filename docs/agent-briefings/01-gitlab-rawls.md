# Agent Briefing: GitLab on Rawls

## Mission

Deploy a self-hosted GitLab instance on Rawls (10.203.3.47) that serves as the central Git repository and CI/CD platform for this homelab infrastructure.

## Business Outcomes (Success Criteria)

- [ ] Self-hosted Git server accessible at `gitlab.lab.local` or via IP
- [ ] CI/CD pipelines functional for Ansible playbook testing
- [ ] All homelab repos mirrored from GitHub (homelab-automation, dotfiles, etc.)
- [ ] Terraform state storage available (optional but nice)
- [ ] Survives internet outages - fully local operation
- [ ] Ansible-driven deployment (idempotent, reproducible)

## Network Topology

```
Host: Rawls (Proxmox node)
IP: 10.203.3.47

GitLab should run as:
- Option A: LXC container on Rawls (preferred, lighter weight)
- Option B: VM on Rawls
- Option C: Docker on Rawls directly (if simpler)

Prior art used LXC at 10.203.3.204 - evaluate if that's still the right approach.
```

## Reference Materials

### Prior Work (descartes-stack)
Location: `/Users/kellen/_Noetica/myt/_code/descartes-stack-master/`

Relevant files:
- Check `ansible/playbooks/` for GitLab deployment patterns
- Check `configs/` for GitLab configuration
- The prior setup used LXC container on Rawls

### Existing Infrastructure Patterns
Location: `/Users/kellen/_Noetica/myt/_code/homelab-automation/`

- `ansible/site.yml` - Main playbook structure
- `ansible/host_vars/socrates.yml` - Example host config
- `ansible/roles/` - Existing role patterns to follow
- `services/llm-stack/` - Docker compose patterns

### Key Standards
- Primary user: `kellen` with full sudo, SSH-key only
- Automation user: `ansible` with passwordless sudo
- SSH keys documented in `CLAUDE.md`

## Constraints

1. **Ansible-driven**: Create role(s) in `ansible/roles/gitlab/` or similar
2. **Idempotent**: Running the playbook twice should be safe
3. **Follow existing patterns**: Match the structure of other roles
4. **Feature branch**: Work in `feature/gitlab-rawls` branch
5. **No hardcoded secrets**: Use variables, 1Password integration, or ansible-vault

## What NOT To Do

1. **Don't copy the Tailscale/Caddy reverse proxy setup** from descartes-stack - it caused issues
2. **Don't over-engineer** - start simple, get it working first
3. **Don't install on the Proxmox host directly** - use LXC/VM/Docker
4. **Don't skip testing** - verify GitLab is accessible before marking complete

## Suggested Approach

1. Create `ansible/host_vars/rawls.yml` with GitLab configuration
2. Create GitLab role with tasks for:
   - Container/VM creation (if using LXC)
   - GitLab Omnibus installation
   - Initial configuration
   - Runner setup (optional)
3. Test deployment
4. Document access URLs and initial credentials

## Deliverables

1. `ansible/roles/gitlab/` - Role for GitLab deployment
2. `ansible/host_vars/rawls.yml` - Rawls-specific configuration
3. Updated `ansible/site.yml` to include GitLab role
4. `services/gitlab-stack/` - If using Docker approach
5. Documentation in `docs/gitlab-setup.md`

## Questions to Research

- GitLab Omnibus vs GitLab Docker - which is better for homelab?
- Memory requirements - Rawls specs?
- GitLab Runner - same host or separate?
- Backup strategy for GitLab data?

## Communication

When complete, report back with:
1. What approach you chose and why
2. How to access GitLab
3. Initial admin credentials location
4. Any issues encountered
5. Suggested next steps
