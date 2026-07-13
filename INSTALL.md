# INSTALL — instructions for Claude Code

A user has dropped this `keel/` folder into a Claude Code session and asked to install it as a skill.
Do exactly this:

1. **Copy the folder into the user's personal skills directory** (create parents if needed):
   ```bash
   mkdir -p ~/.claude/skills
   cp -R <path-to-this-folder> ~/.claude/skills/keel
   ```
   - If `~/.claude/skills/keel` already exists, STOP and ask the user before overwriting.
   - After copying, remove any dev cruft so the one-time intro fires fresh:
     `rm -f ~/.claude/skills/keel/.introduced ~/.claude/skills/keel/.DS_Store`,
     `rm -rf ~/.claude/skills/keel/.git`.

2. **Fire the one-time introduction and relay it to the user:**
   ```bash
   python3 ~/.claude/skills/keel/scripts/docs.py intro
   ```
   Present what it prints — it is the user's first orientation to keel. It writes a marker and
   self-suppresses on every later run, so it appears **only once per install**.

3. **Confirm** keel is installed and tell the user they can start by describing what they want to build.

keel is self-contained: one skill folder, standard Python 3, nothing to `pip install`.
(If the user installs manually instead of via these steps, the same intro still fires automatically the
first time keel runs `rehydrate`.)
