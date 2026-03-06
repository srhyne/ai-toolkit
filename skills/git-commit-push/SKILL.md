---
name: git-commit-push
description: Stage all local changes, generate a commit message with description, commit, and push to remote. Use when the user asks to commit and push, deploy changes, ship code, or wants a quick commit workflow.
---

# Git Commit & Push

Stage all changes, generate a descriptive commit message, commit, and push to remote in one workflow.

## Default Behavior

- **Remote**: `lab` (unless user specifies otherwise)
- **Branch**: Current branch (HEAD)

## Workflow

### Step 1: Stage All Changes

```bash
# Stage all tracked and untracked files
git add -A
```

### Step 2: Review Staged Changes

Run these commands to understand what's being committed:

```bash
# Show staged files
git diff --cached --stat

# Show detailed diff of staged changes
git diff --cached
```

### Step 3: Generate Commit Message

Analyze the staged diff and create a commit message with:

1. **Short summary** (50 chars max): Imperative mood, concise
2. **Description** ("ditty"): A brief, friendly summary of what changed

#### Commit Message Format

```
<type>(<scope>): <short summary>

<ditty - a brief friendly description of the changes>
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix  
- `refactor`: Code restructuring
- `style`: Formatting changes
- `docs`: Documentation
- `test`: Test updates
- `chore`: Maintenance, deps, configs

#### Guidelines

- Summary: Imperative mood ("Add feature" not "Added feature")
- Ditty: Conversational, explains what changed and why in 1-3 sentences
- Keep it light but informative

### Step 4: Commit the Changes

Use a HEREDOC to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <short summary>

<ditty>
EOF
)"
```

### Step 5: Push to Remote

```bash
# Get current branch name
git rev-parse --abbrev-ref HEAD

# Push to lab remote (or user-specified remote)
git push lab HEAD
```

If push fails due to no upstream, set it:

```bash
git push -u lab HEAD
```

## Output

After completing, report:
1. Files staged and committed
2. The commit message used
3. Push result (branch and remote)

## Example Usage

**User says**: "commit and push my changes"

**Agent executes**:
1. `git add -A`
2. `git diff --cached --stat` and `git diff --cached`
3. Analyzes diff, generates message
4. Commits with generated message
5. Pushes to `lab` remote

**Example commit message**:
```
feat(recruiting): add outreach contact filtering

Added ability to filter outreach contacts by status and last contact date.
This makes it easier to find contacts who need follow-up.
```

**User says**: "ship this to origin"

**Agent executes**:
- Same workflow but pushes to `origin` instead of `lab`

## Handling Edge Cases

- **No changes to commit**: Report "Nothing to commit, working tree clean"
- **Push rejected**: Report the error and suggest `git pull` if needed
- **Detached HEAD**: Warn user and ask for branch name
- **Remote doesn't exist**: List available remotes and ask user to choose
