# Export Skills

> Scan the local project's skills folder, let the user pick which skills to export, then copy them to one or more personal skill directories.

## When to Use

Use when the user asks to export skills, push skills to their home directory, distribute skills to other tools, or sync local skills outward to their system.

## Instructions

### Step 1: Locate the AI Toolkit Project

This skill needs access to the AI Toolkit project's `skills/` directory. Resolve the path using this priority order:

1. **Workspace marker** — Check if the current workspace root contains a file named `.ai-toolkit`. If it exists, use the current workspace root as the toolkit path.
2. **Global config** — If the marker is not found, check if `~/.ai-toolkit/.env` exists and contains a non-empty `AI_TOOLKIT_PATH` value. If so, use that path.
3. **Ask the user** — If neither method resolves a path, ask: *"I can't detect the AI Toolkit project. What is the path to your ai-toolkit repository?"* Suggest running the **Setup AI Toolkit** skill to avoid this prompt in the future.

Store the resolved path as `TOOLKIT_ROOT` for the remaining steps.

### Step 2: Scan Local Skills

Read the contents of `TOOLKIT_ROOT/skills/`. Collect every immediate subdirectory that contains a `SKILL.md` file. Record the **folder name** and **full path** for each.

Skip `_template` and `export-skills` itself.

### Step 3: Present the Skill List

If no skills are found, tell the user there are no skills to export and stop.

Otherwise, display a numbered list:

```
Skills available to export:

  1. git-commit-push
  2. generate-squash-commit
  3. import-skills
```

### Step 4: Prompt — Which Skills to Export

Use the `AskQuestion` tool to ask which skills to export. Provide each numbered skill as a selectable option with `allow_multiple: true`. Include an **"All"** option as the first choice for convenience.

If the AskQuestion tool is unavailable, ask conversationally: *"Which skills would you like to export? Enter the number(s), separated by commas, or type 'all'."*

### Step 5: Present Export Locations

Display the available export locations as a numbered list:

```
Export locations:

  1. ~/.cursor/skills
  2. ~/.claude/skills
  3. ~/.agents/skills
  4. ~/.config/opencode/skills
```

### Step 6: Prompt — Which Locations to Export To

Use the `AskQuestion` tool to ask where to export. Provide each location as a selectable option with `allow_multiple: true`. Include an **"All"** option as the first choice for convenience.

If the AskQuestion tool is unavailable, ask conversationally: *"Which locations should I export to? Enter the number(s), separated by commas, or type 'all'."*

### Step 7: Copy Skills to Selected Locations

For each selected skill and each selected location:

1. Ensure the destination directory exists (create it if needed, including parent directories).
2. Read every file in the source skill folder (`SKILL.md` and any supporting files).
3. Create the matching subdirectory at the destination (e.g. `~/.cursor/skills/git-commit-push/`).
4. Write each file into the destination directory, preserving the original content exactly.

**Important:** This is a direct copy, not a symlink. Each destination gets its own independent copy of the skill files.

### Step 8: Confirm Results

After copying, confirm what was exported:

```
Exported 2 skill(s) to 3 location(s):

  Skills:
    - git-commit-push
    - import-skills

  Locations:
    - ~/.cursor/skills
    - ~/.claude/skills
    - ~/.config/opencode/skills
```

If any destination had an existing skill folder with the same name, note that it was overwritten.

## Examples

```
User: "Export my skills"
Agent: Scans skills/ folder, finds 3 skills. Presents them as a numbered
       list, asks which to export. Then presents the 4 export locations,
       asks which to target. Copies the selected skills to the selected
       locations.
```

```
User: "Push all skills to my cursor and claude directories"
Agent: Same workflow — selects all skills and the ~/.cursor/skills and
       ~/.claude/skills locations based on the user's request.
```

```
User: "Sync skills out to all my tools"
Agent: Exports all skills to all 4 locations.
```
