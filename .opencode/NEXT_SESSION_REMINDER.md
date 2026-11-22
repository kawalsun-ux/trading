# Next Session Reminder

User (last session) asked how to back up OpenCode state against PC loss/damage.
Remind them first thing and offer to implement.

## Backup options discussed
1. Push code + wiki to GitHub (already done for trading repo).
2. Periodic backup of ~/.config/opencode and ~/.local/share/opencode/opencode.db
   to a Windows/cloud folder (e.g. OneDrive).
3. Weekly scheduled rsync script (backup-opencode.sh).
4. Keep secrets/API keys in a password manager, not in repo.
5. Optional private git repo for OpenCode state (excluding DB if sensitive).
6. rag_db is regenerable via `opencode-rag index`.

Offer to create the backup script and/or private-repo workflow.
