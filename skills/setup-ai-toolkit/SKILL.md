# Setup AI Toolkit

> Configure the global `~/.ai-toolkit/` directory, sync the `.env` file, and ensure all directories required by other skills exist — without overwriting any existing configuration.

## When to Use

Use when the user asks to set up the AI toolkit, configure the toolkit path, initialize toolkit settings, or when another skill fails to locate the AI Toolkit project and the user wants to fix that permanently. Also use after importing new skills that may introduce new environment variable or directory dependencies.

## Instructions

### Step 1: Detect the AI Toolkit Project Path

Determine the path to the AI Toolkit project using this priority order:

1. **Workspace marker** — Check if the current workspace root contains a file named `.ai-toolkit`. If it exists, use the current workspace root as the toolkit path.
2. **Global config** — If the marker is not found, check if `~/.ai-toolkit/.env` exists and contains a non-empty `AI_TOOLKIT_PATH` value. If so, use that path.
3. **Ask the user** — If neither method resolves a path, ask: *"What is the absolute path to your ai-toolkit repository?"*

Store the resolved path as `TOOLKIT_PATH`.

### Step 2: Validate the Path

Verify that `TOOLKIT_PATH` actually contains the `.ai-toolkit` marker file. If it does not, warn the user that the path doesn't appear to be a valid AI Toolkit project and ask them to confirm or provide a corrected path.

### Step 3: Create the Global Config Directory

```bash
mkdir -p ~/.ai-toolkit
```

This is safe to run even if the directory already exists.

### Step 4: Scan Skills for Dependencies

Read every `SKILL.md` file under `TOOLKIT_PATH/skills/` (skip `_template`). For each skill, extract two kinds of dependencies:

#### 4a: Environment Variables

Look for environment variable names that a skill expects to find in `~/.ai-toolkit/.env`. Identify them by scanning for:

- Variable names appearing in `source ~/.ai-toolkit/.env` usage contexts
- Variable names listed in prerequisite/configuration sections that reference `~/.ai-toolkit/.env`
- Explicit `KEY=value` patterns shown as required `.env` content
- Variable names referenced after sourcing the `.env` file (e.g., `$VARIABLE_NAME` or `${VARIABLE_NAME}`)

**Do not include** `AI_TOOLKIT_PATH` in this scan — it is handled separately in Step 5.

For each variable found, record:

| Field | Value |
|-------|-------|
| Variable name | e.g. `NEWRELIC_API_KEY` |
| Source skill(s) | e.g. `query-newrelic` |
| Description hint | Any contextual clue about what the value should be (e.g., "query key", "account id") |

#### 4b: Directory Paths

Look for any paths under `~/.ai-toolkit/` that a skill creates or uses — typically via `mkdir -p` commands or file paths referencing `~/.ai-toolkit/` subdirectories. Record:

| Field | Value |
|-------|-------|
| Path | e.g. `~/.ai-toolkit/storage/newrelic` |
| Source skill(s) | e.g. `query-newrelic` |

Ignore references to `~/.ai-toolkit/.env` itself and the `~/.ai-toolkit/` root — only capture **subdirectories**.

### Step 5: Sync the `.env` File (Non-Destructive)

**This step must never delete or overwrite existing values.**

#### If `~/.ai-toolkit/.env` does not exist:

Create it with the following structure:

```
AI_TOOLKIT_PATH=/absolute/path/to/ai-toolkit

# -----------------------------------------------------------
# Environment variables required by AI Toolkit skills.
# Uncomment and fill in values as needed.
# -----------------------------------------------------------

# Used by: query-newrelic
# NEWRELIC_API_KEY=
# NEWRELIC_ACCOUNT_ID=
```

The header always contains the `AI_TOOLKIT_PATH=` line (uncommented, with the real value). Below that, each discovered variable is listed as a **comment** with a `# Used by:` annotation showing which skill(s) need it.

#### If `~/.ai-toolkit/.env` already exists:

1. **Read the existing file** in full.
2. **Update `AI_TOOLKIT_PATH`** — If the line exists, update its value to the current `TOOLKIT_PATH`. If it doesn't exist, add it at the top.
3. **Scan for missing variable stubs** — For each variable discovered in Step 4a, check whether the variable name already appears anywhere in the file (as a live value like `VAR=something` *or* as a commented stub like `# VAR=`). If it already appears, **leave it untouched**. If it does not appear, **append** a new commented stub block at the end of the file:

```
# Used by: <skill-name(s)>
# VAR_NAME=
```

4. **Never remove lines** — Even if a skill has been deleted, leave its env stubs in place. The user may still have values they want to keep.
5. **Update `# Used by:` annotations for existing stubs** — If a variable's commented stub already exists but new skills now also reference it, update the `# Used by:` comment to include the additional skill names. Only do this for lines that are still commented out (i.e., the user hasn't set a real value). If the user has set a real value (`VAR=something`), do not modify that line or its surrounding comments.

### Step 6: Create Required Directories

For each directory path discovered in Step 4b, run:

```bash
mkdir -p <path>
```

This is safe to run even if the directory already exists — it will not modify existing contents.

### Step 7: Confirm

Display a summary of everything that was set up or synced:

```
AI Toolkit configured:

  Project path:  /absolute/path/to/ai-toolkit
  Global config: ~/.ai-toolkit/.env

  Env variables synced:
    AI_TOOLKIT_PATH ............. set
    NEWRELIC_API_KEY ............ stubbed (used by: query-newrelic)
    NEWRELIC_ACCOUNT_ID ......... stubbed (used by: query-newrelic)

  Directories ensured:
    ~/.ai-toolkit/storage/newrelic/  (used by: query-newrelic)
```

Use `set` for variables that have a real value, `stubbed` for commented-out placeholders, and `already set` for variables the user previously configured. For directories, note `created` if it was new or `exists` if it was already present.

## Safety Guarantees

- **Never deletes** any file or directory under `~/.ai-toolkit/`.
- **Never overwrites** user-configured environment variable values.
- **Never removes** lines from `~/.ai-toolkit/.env`, even for skills that no longer exist.
- **Appends only** — new variable stubs are added at the end of the file.
- **Idempotent** — running setup multiple times produces the same result and causes no harm.

## Examples

```
User: "Set up the AI toolkit"
Agent: Detects .ai-toolkit in the current workspace, scans all skills,
       discovers NEWRELIC_API_KEY and NEWRELIC_ACCOUNT_ID from query-newrelic,
       discovers ~/.ai-toolkit/storage/newrelic/ directory dependency.
       Creates ~/.ai-toolkit/.env with AI_TOOLKIT_PATH set and env vars
       stubbed as comments. Creates storage/newrelic/ directory. Confirms.
```

```
User: "Set up the toolkit" (second run, after adding a new skill)
Agent: Reads existing .env, finds AI_TOOLKIT_PATH already set and
       NEWRELIC vars already stubbed. Discovers new env vars from the
       newly added skill. Appends only the new stubs. Creates any new
       directories. Reports what was added vs. what was already present.
```

```
User: "Configure the toolkit path"
Agent: Doesn't find .ai-toolkit locally, checks ~/.ai-toolkit/.env — it exists
       with values from a previous setup. Asks the user for the path, validates
       it, updates AI_TOOLKIT_PATH, appends any new env stubs, ensures
       directories exist, and confirms. All previous .env content is preserved.
```
