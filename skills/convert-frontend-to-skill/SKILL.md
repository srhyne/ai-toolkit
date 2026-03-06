---
name: convert-frontend-to-skill
description: Analyze a frontend codebase to discover backend API resources and generate a new skill that can interact with those APIs directly. Use when the user wants to convert frontend code into an API skill, generate a backend API skill from frontend code, create a skill from a frontend codebase, or understand what backend resources a frontend app uses.
---

# Convert Frontend to Skill

Analyze a frontend codebase to discover every backend API it talks to, then generate a new skill that teaches an agent how to interact with those APIs directly — no frontend required.

## When to Use

- User says "convert frontend to skill", "generate skill from frontend"
- User wants to create a skill that interacts with a backend API a frontend already consumes
- User wants to catalog backend resources used by a frontend app

---

## Phase 1: Identify the Frontend and Name the Skill

### Step 1.1: Get the frontend path

If the user hasn't provided a path, ask:

> "What's the path to the frontend codebase you'd like me to analyze?"

Validate the path exists and contains frontend indicators (`package.json`, `src/`, `index.html`, etc.). If not obvious, ask for confirmation.

### Step 1.2: Derive and confirm the skill name

Infer the application name from (in priority order):

1. `package.json` → `name` field
2. Directory name
3. README title
4. Git remote URL

Suggest `<app-name>-expert` as the skill name. Ask the user to confirm:

> "This looks like **<app-name>**. I'd suggest naming the generated skill `<app-name>-expert`. Sound good, or would you prefer a different name?"

Store as `SKILL_NAME`.

---

## Phase 2: Analyze the Codebase

### Step 2.1: Find environment and config files

Search for files defining API base URLs:

```bash
find <path> -maxdepth 3 -name ".env*" -not -path "*/node_modules/*" -not -path "*/.git/*"
find <path> -maxdepth 4 \( -name "config.*" -o -name "*.config.*" -o -name "constants.*" -o -name "api.*" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*"
```

Read these files. Extract:

- **Base URLs** — `API_URL`, `BASE_URL`, `BACKEND_HOST`, `VITE_API_URL`, `NEXT_PUBLIC_API_URL`, `REACT_APP_API_URL`, etc.
- **API key references** — variable names that hold keys or tokens
- **Environment-specific overrides** — `.env.production`, `.env.local`, etc.

### Step 2.2: Discover API call patterns

Search for HTTP client usage:

```bash
rg -l "(fetch\(|axios\.|\.get\(|\.post\(|\.put\(|\.delete\(|\.patch\(|http\.|api\.|useFetch|useQuery|useMutation)" \
  <path>/src --type js --type ts --type vue -g '!node_modules' -g '!dist' -g '!*.test.*' -g '!*.spec.*'
```

Also find API client/service modules (these are goldmines — centralized API definitions):

```bash
rg -l "(createApi|defineApi|apiClient|httpClient|baseURL|baseUrl)" \
  <path>/src --type js --type ts -g '!node_modules'
```

Read centralized API modules first — they usually have the most organized endpoint definitions.

### Step 2.3: Build the API inventory

For each file with API calls, extract:

| Field | What to capture |
|---|---|
| **Host** | The base URL being called (resolve env vars to their values) |
| **Method** | GET, POST, PUT, DELETE, PATCH |
| **Path** | The URL path (e.g., `/contacts/:id`) |
| **Params** | Query parameters, URL parameters |
| **Body** | Request body shape — field names and types |
| **Response** | Expected response shape (from usage in the code) |
| **Context** | What frontend feature uses this endpoint |

Group endpoints by **host**, then by **base route** (first path segment, e.g., `/contacts`).

### Step 2.4: Identify the authentication scheme

```bash
rg -n "(Authorization|Bearer|withCredentials|credentials.*include|x-api-key|api[._-]key|cookie|csrf|xsrf|token)" \
  <path>/src --type js --type ts -g '!node_modules' -i
```

```bash
rg -l "(login|signIn|sign-in|authenticate|auth)" \
  <path>/src --type js --type ts -g '!node_modules' -i
```

Classify what you find:

| Pattern | Auth Type | Skill Implications |
|---|---|---|
| `Authorization: Bearer <token>` | Bearer token | Store token in env |
| `withCredentials: true` / `credentials: 'include'` | Cookie-based session | Need login flow + cookie jar |
| `x-api-key` or similar header | API key | Store key in env |
| Basic auth header | Basic auth | Store username + password in env |
| CSRF/XSRF token handling | CSRF protection | May need to fetch token before writes |

If cookie-based auth is detected, also find the login endpoint (the POST that establishes the session).

### Step 2.5: Identify non-REST connections

```bash
rg -n "(WebSocket|socket\.io|ws://|wss://|ably|pusher|pubnub|EventSource|server-sent)" \
  <path>/src --type js --type ts -g '!node_modules' -i
```

Document these separately — include the connection URL, event names, and message formats.

---

## Phase 3: Present Findings and Get User Selections

### Step 3.1: Present discovered hosts

Show all discovered backend hosts:

```
## Discovered Backend Hosts

| # | Host | Source | Routes Found |
|---|------|--------|--------------|
| 1 | https://api.example.com | .env (API_URL) | 24 |
| 2 | wss://ws.example.com | config.ts | 2 (WebSocket) |
```

Ask using AskQuestion (multi-select) or conversationally:

> **"Which hosts should the generated skill cover?"**

### Step 3.2: Present base routes for selected hosts

For each selected host, show base routes with helpful context about what each one does in the frontend:

```
## Routes for https://api.example.com

| # | Base Route | Methods | What it does |
|---|-----------|---------|--------------|
| 1 | /contacts | GET POST PUT DELETE | Contact management — list, create, edit, delete |
| 2 | /campaigns | GET POST PUT | Campaign CRUD — used in the campaign builder |
| 3 | /auth | POST | Login/logout |
| 4 | /reports | GET | Read-only reporting dashboards |
```

Provide a brief note about each route's role so the user can make an informed decision. Not every frontend API call needs to be in the skill — some are presentation-only or admin-only.

Ask using AskQuestion (multi-select) or conversationally:

> **"Which base routes should the skill cover? Pick the ones most useful for an agent to call directly."**

---

## Phase 4: Handle Authentication and Secrets

### Step 4.1: Explain auth in plain terms

Tell the user what was discovered, without jargon:

> "The frontend uses **[auth type]** to talk to the API. Here's what that means for your new skill..."

| Auth Type | Plain Explanation |
|---|---|
| Bearer token | "You'll need an API token. The skill will send it with every request." |
| Cookie-based | "The API uses browser-style login sessions. The skill will log in first, save the session cookie, and reuse it." |
| API key | "You'll need an API key. The skill will include it as a header on every request." |

### Step 4.2: Store credentials

Ensure the storage location exists:

```bash
mkdir -p ~/.ai-toolkit
touch ~/.ai-toolkit/.env
```

Use the skill name (uppercased, underscores replacing hyphens) as a prefix for all env vars. Example: skill `dashboard-expert` → `DASHBOARD_EXPERT_API_HOST`.

For each required credential, check if it's already set:

```bash
source ~/.ai-toolkit/.env 2>/dev/null
echo "${VAR_NAME:-__UNSET__}"
```

If not set, ask the user for the value in plain terms:

> "I need to save the API base URL. This is the address the frontend talks to — something like `https://api.example.com`. What's the value?"

Write to env:

```bash
echo '<VAR_NAME>=<value>' >> ~/.ai-toolkit/.env
```

Required env vars to set (adapt names to `SKILL_NAME` prefix):

| Variable | When needed |
|---|---|
| `<PREFIX>_HOST` | Always — the API base URL |
| `<PREFIX>_TOKEN` | Bearer token auth |
| `<PREFIX>_API_KEY` | API key auth |
| `<PREFIX>_USERNAME` | Cookie/basic auth |
| `<PREFIX>_PASSWORD` | Cookie/basic auth |

### Step 4.3: Cookie-based auth setup

If the API uses cookies, the generated skill needs:

1. A storage directory for the cookie jar:
   ```bash
   mkdir -p ~/.ai-toolkit/storage/<skill-name>
   ```

2. A login command in the generated skill:
   ```bash
   curl -s -c ~/.ai-toolkit/storage/<skill-name>/cookies.txt \
     -X POST "${HOST}/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "${USERNAME}", "password": "${PASSWORD}"}'
   ```

3. Subsequent requests use `-b` to send cookies:
   ```bash
   curl -s -b ~/.ai-toolkit/storage/<skill-name>/cookies.txt \
     "${HOST}/api/resource"
   ```

4. A re-login instruction if a request returns 401.

---

## Phase 5: Generate the Skill

### Step 5.1: Determine skill location

Ask the user:

> "Where should the skill be saved?"

Offer options:
- **Project skill** — `skills/<skill-name>/` in the current workspace (shared via repo)
- **Personal skill** — `~/.cursor/skills/<skill-name>/` (available across all projects)

Default to project skills in the ai-toolkit if running from that workspace.

### Step 5.2: Create the skill

```bash
mkdir -p <skill-location>/<skill-name>
```

### Step 5.3: Write the SKILL.md

Use the template structure in [generated-skill-template.md](generated-skill-template.md) as the base. Fill in:

1. **Frontmatter** — name and description (third person, includes trigger terms)
2. **Context preamble** — explain what the skill is for, that it was generated from frontend analysis, and what API it covers
3. **Prerequisites** — list all env vars with their purpose
4. **Credential loading** — `source ~/.ai-toolkit/.env` and verification
5. **Storage directory** — `~/.ai-toolkit/storage/<skill-name>/`
6. **Auth handling** — complete instructions appropriate to the auth type
7. **Available Resources** — table of all selected routes with methods and descriptions
8. **Endpoint documentation** — for each route:
   - HTTP method and full path pattern
   - Path parameters, query parameters, request body schema (with types)
   - Example `curl` command using env var references
   - Example response shape (derived from frontend usage)
9. **Workflow examples** — common multi-step operations (derived from how the frontend chains API calls)
10. **Presentation guidelines** — how to format output for the user

### Step 5.4: Size management

If the generated SKILL.md would exceed 500 lines, split:

- Keep the overview, auth, resource table, and workflows in `SKILL.md`
- Move detailed endpoint docs to `api-reference.md`
- Link from SKILL.md: `For detailed endpoint schemas, see [api-reference.md](api-reference.md).`

### Step 5.5: Add the context preamble

Include this near the top of the generated skill so future agents understand their role:

```markdown
> **How this skill was created:** Generated by `convert-frontend-to-skill` from
> the frontend codebase at `<path>`. The endpoints, request/response shapes, and
> auth patterns were extracted from the frontend source code. Your job is to use
> these API endpoints to help the user query, create, update, and manage data
> directly — no frontend needed.
```

---

## Phase 6: Verify and Report

### Step 6.1: Validate the generated skill

- [ ] SKILL.md exists with valid YAML frontmatter
- [ ] Description is specific, third person, includes trigger terms
- [ ] Under 500 lines (or has reference files)
- [ ] All env vars are set in `~/.ai-toolkit/.env`
- [ ] Storage directory exists (if cookie-based auth)

### Step 6.2: Test connectivity

Make a simple API call to verify credentials work:

```bash
source ~/.ai-toolkit/.env
curl -s -o /dev/null -w "%{http_code}" <auth-headers> "${HOST}/<simple-endpoint>"
```

If it returns 200, credentials are good. If 401/403, help the user troubleshoot.

### Step 6.3: Summary report

```
## Skill Generated Successfully

**Skill:** <skill-name>
**Location:** <path>
**API host(s):** <hosts>
**Routes covered:** <count> base routes, <total> endpoints
**Auth type:** <type>
**Env vars configured:** <list>

### Try it out
Ask the agent:
- "<example query that would trigger the skill>"
- "<another example>"
```

---

## Important Notes

- **Don't assume the user knows about env vars.** Walk them through every credential step in plain language.
- **Frontends lie.** Some API endpoints in the code may be deprecated or commented out. Prioritize endpoints that are actively used (imported, called in components).
- **TypeScript interfaces are gold.** If the frontend has type definitions for API responses, use those as the response schema in the generated skill.
- **Centralized API modules first.** Look for files like `api.ts`, `services/`, `client.ts`, `http.ts` before scanning individual components.
- **Test the skill.** Always attempt at least one API call before declaring success.
- **WebSocket endpoints** need different handling than REST — document the connection URL, event names, and message format rather than curl commands.

---

## Examples

```
User: "Convert my frontend to a skill"
Agent: Asks for frontend path. Scans the codebase. Finds 3 backend hosts
       and 18 base routes. Presents hosts for selection. User picks 1 host.
       Presents routes — user picks 8 of 12. Discovers Bearer token auth.
       Asks for the API token, stores it in ~/.ai-toolkit/.env. Generates
       the skill with full endpoint docs. Tests a GET call. Reports success.
```

```
User: "Generate a skill from ~/Sites/my-dashboard/frontend"
Agent: Reads package.json → app name is "acme-dashboard". Suggests skill
       name "acme-dashboard-expert". Scans for API calls. Finds cookie-based
       auth with a /login endpoint. Helps user store credentials. Generates
       skill with cookie jar login flow. Tests login + one endpoint.
```
