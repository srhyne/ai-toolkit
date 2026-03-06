---
name: generate-squash-commit
description: Generate a comprehensive squash commit message by analyzing git diffs and commit history between branches. Use when the user asks to create a squash commit, squash commit message, summarize branch changes, or prepare for a merge/squash.
---

# Generate Squash Commit

Generate a well-crafted squash commit message by analyzing the diff and commit history between two branches.

## Default Behavior

- **Source branch**: Current branch (HEAD)
- **Target branch**: `master`

The user may override either branch explicitly.

## Workflow

### Step 1: Determine Branches

```bash
# Get current branch name
git rev-parse --abbrev-ref HEAD

# Verify target branch exists (default: master)
git rev-parse --verify master 2>/dev/null || git rev-parse --verify main 2>/dev/null
```

If neither `master` nor `main` exists, ask the user for the target branch.

### Step 2: Gather Information

Run these commands in parallel to gather context:

```bash
# Get commit log between branches (target..source)
git log --oneline master..HEAD

# Get detailed commit messages
git log --format="%B---COMMIT_SEPARATOR---" master..HEAD

# Get the full diff
git diff master...HEAD

# Get summary of changes (files changed, insertions, deletions)
git diff --stat master...HEAD
```

Replace `master` with the user-specified target branch if provided.

### Step 3: Analyze Changes

Review the gathered information to understand:
1. **What changed**: Files modified, added, deleted
2. **Why it changed**: Extract intent from commit messages
3. **Impact**: Scope and significance of the changes

### Step 4: Generate Squash Commit Message

Output a commit message following this format:

```
<type>(<scope>): <concise summary>

<body - detailed explanation of what and why>

<optional footer - breaking changes, related issues, etc.>
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependencies, configs

#### Guidelines for the Message

1. **Summary line**: 50 chars or less, imperative mood ("Add feature" not "Added feature")
2. **Body**: Wrap at 72 chars, explain what and why (not how)
3. **Consolidate**: Merge related commits into cohesive descriptions
4. **Omit noise**: Skip merge commits, WIP commits, typo fixes unless significant
5. **Preserve intent**: Capture the overall purpose, not individual steps

## Output Format

Output ONLY the commit message to stdout. Do not write to any file. Format it as a code block the user can copy:

```
feat(auth): implement OAuth2 authentication flow

Add complete OAuth2 authentication with support for Google and GitHub
providers. This replaces the legacy session-based auth system.

Changes include:
- OAuth2 client configuration for multiple providers
- Token refresh handling with automatic retry
- User profile sync from OAuth providers
- Migration script for existing user sessions

Breaking change: Session-based auth endpoints are removed.
Relates to: #142, #156
```

## Example Usage

**User says**: "Create a squash commit for my branch"

**Agent executes**:
1. Determine current branch and verify master exists
2. Run git log and git diff commands
3. Analyze the changes
4. Output the squash commit message to stdout

**User says**: "Squash commit comparing feature/api-v2 to develop"

**Agent executes**:
1. Use `feature/api-v2` as source, `develop` as target
2. Run: `git log develop..feature/api-v2` and `git diff develop...feature/api-v2`
3. Analyze and output

## Tips for Quality Messages

- If there are many small commits, group by theme (e.g., "refactoring", "new endpoints", "tests")
- If commits have inconsistent messages, focus on the code diff to understand intent
- Include metrics when meaningful (e.g., "Reduce bundle size by 15%")
- Call out breaking changes prominently
- Reference issues/tickets if mentioned in commit history
