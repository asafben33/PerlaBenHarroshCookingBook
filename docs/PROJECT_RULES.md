# PROJECT RULES — Perla Ben-Harrosh z"l Cookbook
> Static site (HTML/JS/CSS on Netlify) + Python CLI scripts for content management.
> Based on SIGMA PROJECT_RULES v2.4 and Claude Code conflict-prevention rules.
> Last updated: 21-04-2026

---

## 0. Language & Style

| Context | Language |
|---------|----------|
| Chat / commit messages / comments to user | Hebrew |
| Code, variable names, git branch names, log keys | English |
| Docstrings | English body, Hebrew purpose line at top |

- No emojis in code or commit messages (terminal rendering issues on Windows).
- All user-facing Python output is Hebrew (UTF-8, RTL-fixed via `recipe_utils`).

## 1. File Reading — Offset / Limit

When reading large files (index.html, data.js, book_data.js), always use
`offset` and `limit` parameters. Never read the entire file into context
unless it is under 500 lines.

## 2. Python Scripts — Dry-Run First

Every script that modifies files (add_recipe, edit_recipe, download_images,
rebuild_book_images, etc.) **must** support `--dry-run`.

- Default mode should be safe (dry-run or read-only).
- `--apply` or absence of `--dry-run` enables writes.
- Dry-run output goes to `*.dryrun` or stdout — never overwrites originals.

## 3. Path Anchoring

All scripts resolve paths from `PROJECT_ROOT`:

```python
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
```

- Never use hardcoded absolute paths (e.g. `C:\Users\...`).
- `recipe_utils.py` exports: `PROJECT_ROOT`, `DEFAULT_DATA_JS`, `DEFAULT_LOG_DIR`.
- Other scripts define their own `PROJECT_ROOT` if they don't import `recipe_utils`.
- `safe-git-pull.py` and `auto-git-sync.py` call `os.chdir(PROJECT_ROOT)` at import time.

## 4. Logging — DD-MM-YYYY_HH.MM

All log files use the Hebrew date format: `DD-MM-YYYY_HH.MM`.

```
logs/add_recipe_21-04-2026_14.30.log
logs/download_images_21-04-2026_14.30.log
```

Log directory is always `PROJECT_ROOT/logs/`.

## 5. Git Workflow

### Branches
- Claude Code works **only** on `claude/*` branches (e.g. `claude/harden-security`).
- **Never push directly to `main`**. Always create a PR.
- Branch naming: `claude/<short-description>` using kebab-case.

### Commits
- Conventional commits: `type(scope): description`
  - Types: `feat`, `fix`, `sec`, `chore`, `docs`, `refactor`, `test`
  - Scope examples: `headers`, `sw`, `scripts`, `index`, `book`
- One logical change per commit.
- Co-author line for Claude contributions.

### Merging
- Squash-merge Claude branches to main via PR.
- Delete branch after merge.
- `safe-git-pull.py --full-auto` handles sync and Claude branch merges.

## 6. Frontend Security

### Content Security Policy (CSP)
- CSP is defined in **two places** — keep them in sync:
  1. `_headers` (Netlify, authoritative — includes `frame-ancestors`)
  2. `<meta http-equiv="Content-Security-Policy">` in `index.html`
- `frame-ancestors` cannot be set via `<meta>` — only in `_headers`.
- Any new external resource (CDN, API) must be added to both.

### HSTS
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- Set in `_headers` only (not in `<meta>`).

### XSS Prevention
- Never insert untrusted data via `innerHTML`. Use `textContent` or `createElement`.
- When `innerHTML` is unavoidable, HTML-escape all dynamic values first.
- External API responses (Web3Forms, YouTube) are untrusted.

### Service Worker
- `sw.js` version must be bumped on every cache-breaking change.
- Only cache GET requests with `response.type === 'basic'` and `status === 200`.
- Never cache POST responses (form submissions).

## 7. Image & Asset Paths

- Recipe images: `images/recipes_images/r-{id}.jpg`
- Book images: `images/book_images/`
- Image alias map: `images/_IMG_ALIAS.js`
- Proxy config: `PROJECT_ROOT/proxy_config.txt`

## 8. data.js Conventions

- Recipe array `R` ends with `\n];\n`.
- Recipe IDs use category prefixes: `s1` (soups), `sa1` (salads), etc.
- Fields use single quotes, no spaces after colons: `id:'s1',cat:'soups'`.
- 19 categories (see `recipe_utils.CATEGORIES`).
- Backup before any modification: `data.js.bak_DD-MM-YYYY_HH.MM.SS`.

## 9. Deployment

- Hosting: Netlify (auto-deploy from `main` branch).
- `_headers` file at site root configures HTTP headers.
- `_redirects` (if present) configures URL redirects.
- `sw.js` must have `Cache-Control: no-cache` (set in `_headers`).
- Images should have `Cache-Control: immutable, max-age=31536000`.

## 10. What NOT to Do

- Do not add FastAPI, database, Redis, or backend server code.
- Do not add Windows services or system-level integrations.
- Do not add scanning/security-testing tools to the repo.
- Do not modify `.git/` internals or force-push to main.
- Do not commit `.env`, credentials, or proxy passwords.
- Do not add Kerberos, LDAP, or enterprise auth code.
