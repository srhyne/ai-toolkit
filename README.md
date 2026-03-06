# AI Toolkit

A shared repository of agentic skills that work across AI coding tools. Skills defined here can be synced to **Cursor**, **Claude Code**, **Cline**, **OpenCode**, or any agent that reads markdown instruction files — using the built-in import and export skills.

## How It Works

```
~/.cursor/skills/        ──┐                ┌──  ~/.cursor/skills/
~/.claude/skills/        ──┤   import        │    ~/.claude/skills/
~/.agents/skills/        ──┼──────────►  ai-toolkit/skills/  ──export──►  ~/.agents/skills/
~/.config/opencode/skills/ ┘                 └──  ~/.config/opencode/skills/
```

The toolkit acts as a central hub. **Import** pulls skills from your personal tool directories into the repo. **Export** pushes skills from the repo out to one or more tool directories. This lets you author a skill once and distribute it everywhere.

## Repository Structure

```
ai-toolkit/
├── .ai-toolkit              # Marker file — identifies this repo to import/export skills
├── skills/                  # All shared skills live here
│   ├── _template/           # Copy this folder to create a new skill
│   ├── setup-ai-toolkit/    # Configure ~/.ai-toolkit/ global config and dependencies
│   ├── import-skills/       # Sync skills into this repo from tool directories
│   ├── export-skills/       # Sync skills from this repo out to tool directories
│   ├── git-commit-push/     # Stage, commit, and push in one workflow
│   ├── generate-squash-commit/  # Generate squash commit messages from branch diffs
│   ├── query-runner/        # Run SQL queries against SingleStore/MySQL
│   ├── run-notebook/        # Execute SQL from markdown notebooks with variable substitution
│   ├── query-newrelic/      # Query New Relic Insights API with NRQL
│   ├── log-expert/          # Investigate application errors via New Relic logs
│   ├── do-expert/           # Query DigitalOcean infrastructure via doctl
│   ├── verify-ecosystem/    # Scan codebases and infrastructure to update the ecosystem map
│   ├── conveyour-changelog/ # Generate customer-facing changelogs from backend + frontend git history
│   ├── purpose-expert/      # Generate and query purpose manifests for any codebase
│   └── video-transcript-fetcher/  # Fetch transcripts from YouTube and Vimeo videos
├── agents/                  # Sub-agent definitions (future use)
└── prompts/                 # Standalone prompt templates (future use)
```

## Syncing Skills

### Importing — pull skills into the toolkit

Run this from any workspace where the import-skills skill is available:

```
User: "Import my skills"
```

The agent scans `~/.cursor/skills/`, `~/.claude/skills/`, `~/.agents/skills/`, and `~/.config/opencode/skills/` for skill folders. It deduplicates against what already exists in the repo, presents a list of new skills, and lets you pick which ones to bring in.

This is how you collect skills you've written directly inside a tool's config directory and centralize them in the toolkit.

### Exporting — push skills out to your tools

Run this from any workspace where the export-skills skill is available:

```
User: "Export my skills"
```

The agent lists the skills in this repo, lets you pick which ones to export, then asks where to send them. You can target one or all of:

- `~/.cursor/skills/`
- `~/.claude/skills/`
- `~/.agents/skills/`
- `~/.config/opencode/skills/`

Each destination gets an independent copy of the skill files. After exporting, every tool that reads from those directories will pick up the skills automatically.

### Typical workflow

1. **Author** a new skill in `skills/my-skill/SKILL.md` (or import one you wrote ad-hoc).
2. **Commit and push** to share it with your team via git.
3. **Export** to distribute it to whichever AI tools you use locally.

Teammates pull the repo, run export, and they have the same skills available in their own tools.

## Included Skills

### Toolkit Management

| Skill | Description |
|-------|-------------|
| `setup-ai-toolkit` | Configure the global `~/.ai-toolkit/` directory, sync `.env` variables, and create storage directories required by other skills |
| `import-skills` | Scan personal tool directories, deduplicate, and import new skills into the repo |
| `export-skills` | Pick skills from the repo and copy them to one or more tool directories |

### Git Workflows

| Skill | Description |
|-------|-------------|
| `git-commit-push` | Stage all changes, generate a conventional commit message, and push to remote |
| `generate-squash-commit` | Analyze branch diffs and commit history to produce a squash commit message |

### Database & SQL

| Skill | Description |
|-------|-------------|
| `query-runner` | Run SQL queries against a SingleStore/MySQL database via a self-contained Node.js script |
| `run-notebook` | Execute SQL queries defined in markdown notebook files, handle `{{variable}}` substitution, and save results |

### Observability

| Skill | Description |
|-------|-------------|
| `query-newrelic` | Query New Relic's Insights API with NRQL, store results to disk, and process them with `jq` and Unix tools |
| `log-expert` | Translate log investigation tasks into NRQL queries against New Relic `Log` data (errors, domain-scoped searches, summaries) |

### Infrastructure

| Skill | Description |
|-------|-------------|
| `do-expert` | Query and inspect DigitalOcean infrastructure (droplets, apps, databases, VPCs) via `doctl` |
| `verify-ecosystem` | Scan project codebases and DigitalOcean infrastructure to verify and update the ecosystem map |

### Codebase Intelligence

| Skill | Description |
|-------|-------------|
| `purpose-expert` | Generate and query scoped purpose manifests for any codebase — scan specific directories, build searchable indexes of documented subsystem purposes |

### Product & Releases

| Skill | Description |
|-------|-------------|
| `conveyour-changelog` | Generate customer-facing changelogs from ConveYour backend (PHP/Laravel) and frontend (Vue/cy-ui2) git history, with feature flag detection and Notion task linking |

### Media

| Skill | Description |
|-------|-------------|
| `video-transcript-fetcher` | Fetch transcripts from YouTube or Vimeo videos via an API and save them as markdown files |

## Global Config (`~/.ai-toolkit/`)

Several skills store credentials, results, and working files in a shared global directory at `~/.ai-toolkit/`. Run the `setup-ai-toolkit` skill to initialize it:

```
User: "Set up the AI toolkit"
```

This will:

1. Create `~/.ai-toolkit/` if it doesn't exist.
2. Write (or update) `~/.ai-toolkit/.env` with `AI_TOOLKIT_PATH` pointing to this repo, plus commented stubs for every credential the skills need.
3. Create subdirectories like `storage/newrelic/`, `storage/transcripts/`, `storage/notebook-results/`, and `storage/purpose-manifests/`.

You only need to run setup once — or again after importing new skills that introduce new environment variables.

### Required environment variables by skill

| Variable | Used by |
|----------|---------|
| `SINGLESTORE_HOST`, `SINGLESTORE_PORT`, `SINGLESTORE_USER`, `SINGLESTORE_PASSWORD`, `SINGLESTORE_DB_NAME` | `query-runner`, `run-notebook` |
| `NEWRELIC_API_KEY`, `NEWRELIC_ACCOUNT_ID` | `query-newrelic`, `log-expert` |
| `CY_TRANSCRIPTS_API_KEY` | `video-transcript-fetcher` |
| `PROJECT_PATHS` | `verify-ecosystem`, `conveyour-changelog` |

## Adding a New Skill

1. Copy the template:
   ```bash
   cp -r skills/_template skills/my-new-skill
   ```
2. Edit `skills/my-new-skill/SKILL.md` — follow the structure in the template.
3. Commit, push, and optionally run **export** to distribute it to your local tools.

### Skill file format

Every skill folder contains at minimum a `SKILL.md` with:

- **When to Use** — triggers that tell the agent when to activate the skill.
- **Instructions** — step-by-step workflow the agent follows.
- **Examples** — sample user prompts and expected behavior.

See `skills/_template/SKILL.md` for the full structure.

## The `.ai-toolkit` Marker

The `.ai-toolkit` file at the repo root identifies this directory as the AI Toolkit project. The import and export skills use it to locate the toolkit when running from any workspace — if the marker isn't found, the agent will ask for the path instead.

## Conventions

- **One folder per skill** — keep everything self-contained.
- **Kebab-case folder names** — e.g., `git-commit-push`, `do-expert`.
- **`SKILL.md` as the entry point** — use this exact filename.
- **Tool-agnostic language** — write instructions any LLM-based coding agent can follow; avoid syntax specific to one tool.
- **Include examples** — show sample user prompts and expected agent behavior.

## Examples

Note: I'm just calling out the skill with /, these are not commands but another way to reference a skill. 

### Pulling Logs from New Relic

- `/log-expert Get the last 10 ConveYour errors, then look through my current workspace to explain where and why the errors occurred` - [screnshot](https://share.zight.com/eDuOk5XX)
- `/log-expert Pull the last 15 logs for context.org_domain sunrun`
- `/log-expert Can you get me the last 10 errors for domain dthvivinttraining`


### Faster git & merge operations

- `/branch-reviewer my current branch to master` to get a quick exec summary of changes, optionally do a deep dive on the branch
- `/git-commit-push` that's it. I use it a ton to get tight commits and push to my merge branch quickly.
- `/generate-squash-commit` Does something similar to branch reviewer, but it's just more focused on just generating a squash commit. I use often when merging in GitLab. 

### Infrastructure

- `/do-expert help me understand the topology for all droplets starting with "v" or "ny-v".` - incredible response, [see image](https://share.zight.com/WnuvzyEr)
- `/do-expert help me understand the state of all of my apps.` - [see image](https://share.zight.com/o0udyR8O)

### ConveYour Admin
An interface for working with the admin RPC API. 

- `/conveyour-admin help me understand the state of this contact 697952853d612b01b9743889 and help me better understand what has run on this contact in terms of trigger logs. Help me visually understand how they got to the state that they're in through their campaigns and triggers.`

    - [creates entire write-up](https://share.zight.com/kpu2BJNv)
    - [creates visuals mapping process](https://share.zight.com/QwuZxL9W)

### ConveYour Changelog
Generate customer-facing release notes from git history.

- `/conveyour-changelog Generate a changelog for the last 30 days` — scans backend + frontend master branches, correlates changes, detects feature flags, and produces a polished changelog for product marketing / CS
- `/conveyour-changelog What improvements have we shipped since January 1st?`

### ConveYour Data Expert
A skill trained on ConveYour's Singlestore data!

- `/conveyour-data-expert  What organization has the most running active triggers within a single campaign? I've use the active triggers view for this.` 

    - [ creates nice data summary ](https://share.zight.com/04uj9EL2)