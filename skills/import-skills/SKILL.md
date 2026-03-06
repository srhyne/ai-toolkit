# Import Skills

> Scan personal skill directories, list discovered skills, deduplicate against the local project, and let the user pick which ones to import.

## When to Use

Use when the user asks to import skills, sync skills, pull in skills from their home directory, or browse available skills across their system.

## Instructions

### Step 1: Locate the AI Toolkit Project

This skill needs access to the AI Toolkit project's `skills/` directory. Resolve the path using this priority order:

1. **Workspace marker** — Check if the current workspace root contains a file named `.ai-toolkit`. If it exists, use the current workspace root as the toolkit path.
2. **Global config** — If the marker is not found, check if `~/.ai-toolkit/.env` exists and contains a non-empty `AI_TOOLKIT_PATH` value. If so, use that path.
3. **Ask the user** — If neither method resolves a path, ask: *"I can't detect the AI Toolkit project. What is the path to your ai-toolkit repository?"* Suggest running the **Setup AI Toolkit** skill to avoid this prompt in the future.

Store the resolved path as `TOOLKIT_ROOT` for the remaining steps.

### Step 2: Scan for Skills

Search these directories for skill folders (each containing a `SKILL.md`):

- `~/.cursor/skills/`
- `~/.claude/skills/`
- `~/.agents/skills/`
- `~/.config/opencode/skills/`

For each directory that exists, collect every immediate subdirectory that contains a `SKILL.md` file. Record:

- **Skill name** — the folder name (e.g. `git-commit-push`)
- **Source** — which root directory it came from (e.g. `~/.cursor/skills/`)
- **Full path** — the absolute path to the skill folder

Skip directories that don't exist or are empty.

### Step 3: Scan Local Skills

Read the contents of `TOOLKIT_ROOT/skills/`. Collect the folder name of every existing local skill, ignoring `_template`.

### Step 4: Deduplicate

Compare the discovered skills from Step 2 against the local skills from Step 3 by **folder name**. Remove any skill from the discovered list that already exists locally.

### Step 5: Present the Report

If no new skills are found after deduplication, tell the user everything is already imported and stop.

Otherwise, display a numbered list using this format:

```
Available skills to import:

  1. skill-name-a  (from ~/.cursor/skills/)
  2. skill-name-b  (from ~/.claude/skills/)
  3. skill-name-c  (from ~/.config/opencode/skills/)
```

### Step 6: Prompt the User

Use the `AskQuestion` tool to ask which skills to import. Provide each numbered skill as a selectable option with `allow_multiple: true`. Include an "All" option as the first choice for convenience.

If the AskQuestion tool is unavailable, ask conversationally: *"Which skills would you like to import? Enter the number(s), separated by commas, or type 'all'."*

### Step 7: Copy Skills into the Project

For each selected skill:

1. Read every file in the source skill folder (SKILL.md and any supporting files).
2. Create the matching directory under `TOOLKIT_ROOT/skills/`.
3. Write each file into the new local directory, preserving the original content exactly.

After copying, confirm what was imported:

```
Imported 2 skill(s):

  - skill-name-a  (from ~/.cursor/skills/)
  - skill-name-b  (from ~/.claude/skills/)
```

## Examples

```
User: "Import my skills"
Agent: Scans ~/.cursor/skills/, ~/.claude/skills/, ~/.agents/skills/,
       and ~/.config/opencode/skills/. Finds 4 skills, 1 already exists
       locally. Presents the 3 new ones as a numbered list, asks the user
       to pick, then copies the selected skills into skills/.
```

```
User: "Sync skills from my home directory"
Agent: Same workflow as above.
```
