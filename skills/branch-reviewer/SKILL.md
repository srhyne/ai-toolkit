---
name: branch-reviewer
description: Review the current branch against a target branch (master/main) with an executive summary, technical analysis, security profile, test coverage check, and deployment risk assessment. Use when the user asks to review a branch, analyze branch changes, compare branches, or prepare for a merge review.
---

# Branch Reviewer

Perform a comprehensive review of the current working branch against a target branch. The review is delivered in two phases so the user gets a quick executive summary before the deeper analysis begins.

## Phase 1: Executive Summary (deliver immediately)

### Step 1: Determine Branches

```bash
# Get current branch
git rev-parse --abbrev-ref HEAD

# Determine target branch
git rev-parse --verify master 2>/dev/null && echo "TARGET=master" \
  || (git rev-parse --verify main 2>/dev/null && echo "TARGET=main")
```

**Branch resolution order:**
1. If the user specified a target branch, use it.
2. If `master` exists, use `master`.
3. If `main` exists, use `main`.
4. Otherwise, ask the user which branch to compare against.

### Step 2: Gather Diff Context

Run these commands in parallel (replace `$TARGET` with the resolved target branch):

```bash
# One-line commit log
git log --oneline $TARGET..HEAD

# Detailed commit messages
git log --format="%h %s%n%b---COMMIT_SEPARATOR---" $TARGET..HEAD

# Full diff
git diff $TARGET...HEAD

# Stat summary
git diff --stat $TARGET...HEAD

# List of changed files
git diff --name-only $TARGET...HEAD
```

### Step 3: Read Surrounding Context

For each file that was materially changed (not just whitespace or import ordering):
- Read the full file so you understand the surrounding code and how the change fits in.
- Check for related documentation files (README, CHANGELOG, docs/, wiki/, or inline doc comments) near the changed files and read those too.

### Step 4: Produce the Executive Summary

Output a concise, high-level summary in this format and **stop here** to let the user read it before continuing:

```markdown
# Branch Review: `<source-branch>` → `<target-branch>`

## Executive Summary

**What changed:** <1-2 sentence plain-language description>

### Highlights
- <Bullet per meaningful change — focus on user-facing value and why it matters>
- ...

### Change Stats
- **Files changed:** N
- **Commits:** N
- **Insertions / Deletions:** +N / -N
```

After outputting the Executive Summary, **ask the user if they'd like to continue to the deep analysis.** This keeps the experience fast — the user can copy the summary immediately and optionally proceed.

---

## Phase 2: Deep Analysis (only after user confirms)

When the user opts to continue, perform the following analyses and output them together.

### 2A — Technical Analysis

Examine the diff deeply:

- **Architecture impact**: Does this introduce new patterns, services, or dependencies?
- **Code quality**: Complexity, duplication, naming, error handling.
- **Performance**: Any new queries, loops, or allocations that could degrade performance at scale?
- **Edge cases**: Inputs or states that the new code may not handle.

Format:

```markdown
## Technical Analysis

### Architecture
<findings or "No architectural changes.">

### Code Quality
<findings>

### Performance Considerations
<findings or "No concerns.">

### Edge Cases & Error Handling
<findings>
```

### 2B — Security Profile

Flag anything that touches:

| Area | What to look for |
|------|-----------------|
| **PII** | New personal data being logged, stored, returned in APIs, or shared with third parties |
| **Authentication** | Changes to login, token handling, session management, OAuth flows |
| **Authorization** | Permission checks, role gates, access control changes |
| **Billing** | Payment processing, subscription logic, pricing calculations |
| **Secrets** | API keys, credentials, tokens in code or config |
| **Input validation** | New user inputs that lack sanitization or validation |

Format:

```markdown
## Security Profile

| Area | Status | Notes |
|------|--------|-------|
| PII | ✅ Clear / ⚠️ Flag | <details> |
| Authentication | ✅ / ⚠️ | <details> |
| Authorization | ✅ / ⚠️ | <details> |
| Billing | ✅ / ⚠️ | <details> |
| Secrets | ✅ / ⚠️ | <details> |
| Input Validation | ✅ / ⚠️ | <details> |
```

If nothing is flagged, output: **"No security concerns identified."**

### 2C — Test Coverage

- Check whether the branch includes new or updated tests for the changed code.
- Look for test files that correspond to the changed source files.
- Identify any new public functions, endpoints, or business logic that lack test coverage.

Format:

```markdown
## Test Coverage

### Tests Added/Modified
- <list of test files changed, or "None">

### Untested Changes
- <list of changed functions/endpoints with no corresponding tests, or "All changes appear covered.">
```

### 2D — Deployment & Rollback Risk

Think forward to what happens when this branch is merged and deployed:

1. **User-facing changes**: Will end users need to change how they use the product? New UI flows, removed features, changed behavior?
2. **API compatibility**: Are there breaking changes to endpoints (removed fields, changed response shapes, new required parameters)?
3. **Frontend impact**: Will a frontend deployment need to happen simultaneously? Will the frontend break if it deploys before or after this backend change?
4. **Data mutations**: Does this branch run migrations, backfills, or write data in a new format that cannot be easily undone?
5. **Rollback safety**: If you revert to the previous commit after deploying, will the system recover cleanly? Or will there be orphaned data, broken references, or schema mismatches?

Format:

```markdown
## Deployment & Rollback Risk

| Risk Area | Level | Details |
|-----------|-------|---------|
| User-Facing Changes | 🟢 None / 🟡 Minor / 🔴 Breaking | <details> |
| API Compatibility | 🟢 / 🟡 / 🔴 | <details> |
| Frontend Coordination | 🟢 / 🟡 / 🔴 | <details> |
| Data Mutations | 🟢 / 🟡 / 🔴 | <details> |
| Rollback Safety | 🟢 Safe / 🟡 Caution / 🔴 Dangerous | <details> |

### Recommendations
- <any pre-deploy or post-deploy steps to mitigate risk>
```

---

## Output Flow Summary

```
1. Determine branches
2. Gather diffs + read surrounding code & docs
3. Output Executive Summary → STOP, ask user
4. (User confirms) → Output Technical Analysis, Security Profile, Test Coverage, Deployment Risk
```

## Example Usage

**User says**: "Review my branch"

**Agent executes Phase 1**: Detects branch `feature/new-billing` vs `master`, gathers diff, outputs executive summary, and pauses.

**User says**: "Continue" or "Give me the deep analysis"

**Agent executes Phase 2**: Outputs technical analysis, security profile, test coverage, and deployment risk.

**User says**: "Review this branch against develop"

**Agent**: Uses `develop` as the target branch instead of master/main.
