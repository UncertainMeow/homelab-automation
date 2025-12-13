# Project Rules

## Long-Running Task Monitoring

**CRITICAL**: When running background tasks (ansible playbooks, builds, deployments):

1. **Set expectations upfront** - Proxmox config playbooks should complete in 10-15 minutes. Anything over 20 minutes is suspect.
2. **Active monitoring** - Check progress every 2-3 minutes, not just wait blindly
3. **Recognize stuck tasks** - If the same task shows in output for more than 5 minutes, investigate immediately
4. **Fail fast** - At 15 minutes, proactively check if the process is hung rather than waiting
5. **Never wait 45 minutes** - This is a hard ceiling. If a task approaches 20 minutes, stop and investigate.

When monitoring ansible playbooks:
- Container operations: 1-2 min each
- Package installs (apt): 2-5 min max
- Driver installs: 5-10 min max
- Full playbook: 15-20 min max

If any of these are exceeded, **stop waiting and investigate**.

## SSH Keys

Standard SSH keys for this infrastructure:
- cogito: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN7jefck23Q1wCFLAS3shg6uVpiOXKdVRPiPqRQc2gNz cogito`
- ergo-sum: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEIBPoFy/oe9j6lvXyVgnaPRb72EznbsuJQUDhQYxu2l ergo-sum`

## User Management

- Primary user: `kellen` with full sudo, SSH-key only authentication
- Automation user: `ansible` with passwordless sudo for automation
