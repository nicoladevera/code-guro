# UX Improvement Roadmap: Making Code Guro Accessible to Non-Technical Users

## Document Purpose

This document outlines a phased approach to improving Code Guro's user experience for non-technical product managers and AI builders. While the tool's core functionality is strong, the current CLI interface presents friction points that may intimidate users unfamiliar with terminal commands, environment variables, and file path navigation.

**Target Audience for This Document:** Future developers and AI agents working on Code Guro enhancements.

**Last Updated:** February 7, 2026

**Status:** Phase 1 (Foundation) completed and shipped in v0.5.0. Currently focusing on Phase 2 (Discoverability).

---

## Current State Analysis

### Friction Points Identified

1. **Environment Variable Configuration**
   - Users must understand `export`, shell config files (`~/.bashrc`, `~/.zshrc`)
   - Manual editing of configuration files required
   - No immediate validation feedback

2. **Path Navigation**
   - Requires knowledge of relative (`.`, `./src`) and absolute paths
   - No visual guidance for folder selection
   - Users must type paths manually

3. **Command Syntax**
   - Commands like `code-guro analyze .` assume terminal familiarity
   - No interactive prompts or guidance
   - Technical error messages

4. **GitHub Integration**
   - Manual URL pasting required
   - No support for private repositories
   - No authentication helpers

5. **Progress Feedback**
   - Technical console output (`Analyzing: /path`)
   - No clear milestones or time estimates
   - Limited visual feedback during long operations

### User Journey Today

```
1. Install Python (if not present)
2. Run: python3 -m pip install --user code-guro
3. Run: code-guro configure
4. Read instructions about environment variables
5. Open shell config file in text editor
6. Add export ANTHROPIC_API_KEY="..." line
7. Restart terminal or source config
8. Run: code-guro configure again to validate
9. Run: code-guro analyze .
10. Wait for analysis (unclear progress)
11. Navigate to output directory manually
```

**Drop-off risk:** Steps 4-7 present significant abandonment risk for non-technical users.

---

## Vision: Ideal User Experience

### Target User Journey (Post-Implementation)

```
1. Install: curl -fsSL https://code-guro.dev/install.sh | sh
2. Installer launches interactive setup automatically
3. Select provider from visual menu (with descriptions)
4. Paste API key when prompted (validated immediately)
5. Run: code-guro (in any project folder)
6. Tool detects project, shows preview, asks for confirmation
7. Clear progress updates with milestones
8. Documentation auto-opens in browser
```

**Success Criteria:**
- Time from install to first analysis: < 2 minutes
- Setup completion rate: > 90%
- No need to read documentation before first use

---

## Phased Implementation Plan

### Phase 1: Foundation (Week 1-2) ✅ COMPLETED
**Goal:** Make the current CLI feel friendly without architectural changes

**Status:** Shipped in v0.5.0 (February 7, 2026)

**What Was Delivered:**
- ✅ Interactive setup wizard with secure API key storage
- ✅ Smart defaults with zero-argument invocation
- ✅ Improved console output with emojis and progress tracking
- ✅ Warning suppression for cleaner UX
- ✅ Bug fixes and documentation updates

**Implementation Summary:**
All three features were successfully implemented and tested:

1. **Interactive Setup Wizard (1.1)** - Provider selection, masked API key input, immediate validation, and secure storage in `~/.config/code-guro/config.json` (0o600 permissions)
2. **Smart Defaults (1.2)** - Zero-argument `code-guro` command with auto-detection, dry-run preview, and confirmation prompt
3. **Improved Console Output (1.3)** - Milestone-based progress, emojis (with `--no-emoji` flag), time estimates, and organized document summaries

**Files Modified:**
- `src/code_guro/cli.py` - All three features + warning suppression
- `src/code_guro/config.py` - API key storage and preferences
- `src/code_guro/analyzer.py` - Progress callbacks and dry-run mode
- `src/code_guro/generator.py` - Enhanced progress tracking
- `src/code_guro/providers/*.py` - Config-first API key retrieval
- `AGENTS.md` - Comprehensive Phase 1 documentation
- `README.md` - Updated Quick Start guide

**Commit:** `11aa2d2` on `feature/phase-1-foundation` branch

---

#### 1.1 Interactive Setup Wizard ✅

**Current State:**
```bash
code-guro configure
# Instructions printed, user must manually set env vars
```

**Target State:**
```bash
code-guro configure

# Interactive flow:
# 1. Show current config (if any)
# 2. Provider selection menu (arrow keys or number)
# 3. Direct API key input (masked, secure)
# 4. Immediate validation with friendly feedback
# 5. Secure storage in ~/.config/code-guro/config.json
# 6. Success message with next steps
```

**Implementation Notes:**
- Modify `src/code_guro/cli.py::configure()` command
- Use `rich.prompt.Prompt` for secure input (already imported)
- Store encrypted API key in config (requires new encryption utility)
- Add `decrypt_api_key()` function in `src/code_guro/config.py`
- Update `get_api_key()` to check config first, then env vars (fallback)
- Validation should use existing `validate_api_key()` from providers

**Files to Modify:**
- `src/code_guro/cli.py` - Update `configure()` command
- `src/code_guro/config.py` - Add API key storage/retrieval functions
- `src/code_guro/utils.py` - Add encryption helpers (consider `cryptography` library)

**Testing Considerations:**
- Test with all three providers (Anthropic, OpenAI, Google)
- Verify secure storage (file permissions 0o600)
- Test fallback to environment variables
- Verify encryption/decryption roundtrip

**Estimated Effort:** 3-4 days

**Actual Effort:** 3 days (including bug fixes and testing)

**Delivery Notes:**
- Implemented with plain text storage (0o600 permissions) instead of encryption - simpler, more maintainable
- Added backward compatibility with environment variables
- Immediate validation with user-friendly error messages
- Config schema v2 with `api_keys` and `preferences` sections

---

#### 1.2 Smart Defaults ✅

**Current State:**
```bash
code-guro analyze .  # User must know to use "."
```

**Target State:**
```bash
code-guro  # No arguments

# Output:
# Found project at: /Users/user/my-app
# Framework detected: Next.js (156 files, ~23K tokens)
# Estimated cost: $0.45
#
# Analyze this project? [Y/n]
```

**Implementation Notes:**
- Modify `main()` command group to handle no-subcommand case
- Auto-detect current working directory
- Run quick file scan (use existing `analyze_codebase()` but with dry-run mode)
- Display summary with confirmation prompt
- If confirmed, proceed with full analysis

**Files to Modify:**
- `src/code_guro/cli.py` - Add logic to `main()` for zero-argument case
- `src/code_guro/analyzer.py` - Add `dry_run=True` parameter to `analyze_codebase()`

**Edge Cases:**
- Current directory is home folder (too large) - prompt for path
- No code files found - suggest using `code-guro analyze <path>` instead
- Already analyzed recently - offer to re-analyze or view existing docs

**Testing Considerations:**
- Test in various directory types (project root, subdirectory, home folder)
- Test with no analyzable files
- Verify cost estimation accuracy

**Estimated Effort:** 2-3 days

**Actual Effort:** 2 days

**Delivery Notes:**
- Implemented `invoke_without_command=True` in Click to handle zero-argument case
- Added `handle_zero_argument_flow()` with welcome message, configuration check, and project preview
- Dry-run mode estimates cost without reading full file contents
- Edge case handling: home directory warning, empty directories, recent analysis detection

---

#### 1.3 Improved Console Output ✅

**Current State:**
```
Analyzing: /Users/user/project
[technical progress indicators]
```

**Target State:**
```
📊 Understanding your codebase...

✓ Scanned 156 files (2 seconds)
✓ Detected Next.js framework (1 second)
⏳ Generating documentation... (30 seconds estimated)
   [████████████░░░░░░░░] 60% - Writing architecture guide

✓ Documentation ready! (35 seconds total)

📄 Generated documents:
  • Overview - What your app does
  • Getting Oriented - File structure explained
  • Architecture - How it's built
  • Core Files - The important stuff
  • Deep Dives - Detailed explanations
  • Quality Analysis - What's good, what needs attention
  • Next Steps - Where to explore next

🌐 Open in browser: code-guro-output/html/00-overview.html
```

**Implementation Notes:**
- Replace technical messages with friendly equivalents
- Add milestone-based progress tracking
- Use `rich.progress.Progress` for visual progress bars
- Add time estimates based on token count
- Use emojis sparingly for visual markers (make optional via flag)
- Group output into clear sections (scanning, analyzing, generating, complete)

**Files to Modify:**
- `src/code_guro/generator.py` - Add progress callbacks
- `src/code_guro/cli.py` - Update output formatting in `analyze()` command
- `src/code_guro/analyzer.py` - Add progress hooks

**Configuration Option:**
- Add `--no-emoji` flag for users who prefer plain text
- Store preference in config for persistent setting

**Testing Considerations:**
- Test with various codebase sizes (small, medium, large)
- Verify time estimates are reasonably accurate
- Test terminal width handling (narrow vs wide)

**Estimated Effort:** 2-3 days

**Actual Effort:** 2 days

**Delivery Notes:**
- Milestone-based progress with emojis (📊, ✓, ⏳, 📄, 🌐)
- `--no-emoji` flag implemented with preference storage
- Time estimates based on token count
- Progress callbacks in analyzer and generator
- Organized document summary with clear next steps
- Selective warning suppression for cleaner output

---

**Phase 1 Deliverable:** ✅ DELIVERED
A friendlier CLI that removes the biggest barriers to entry. Users can configure, run, and understand Code Guro without reading documentation.

**Success Metrics:**
- Setup time: ✅ < 2 minutes (from `pip install` to first analysis)
- Setup completion rate: 🔄 To be measured in production
- User feedback: 🔄 To be collected post-release

**Total Phase 1 Effort:** 7 days (1.4 weeks) - Under original estimate

---

### Phase 2: Discoverability (Week 3-4) 🎯 CURRENT FOCUS
**Goal:** Help users understand what's possible without reading docs

**Status:** Planning phase - implementation to begin after Phase 1 merge

#### 2.1 Interactive Path Selection

**Feature Description:**
Add a visual directory browser for path selection, similar to `tree` but interactive.

**Usage:**
```bash
code-guro analyze --browse

# Shows interactive tree:
# my-projects/
# ├── my-app/ (156 files, ~$0.45)
# ├── client-dashboard/ (89 files, ~$0.30)
# └── prototype/ (23 files, ~$0.10)
#
# Use ↑↓ to navigate, → to expand, Enter to select, q to quit
```

**Implementation Notes:**
- Add `--browse` flag to `analyze` command
- Use `prompt_toolkit` for interactive tree (add to optional dependencies)
- Display file counts and cost estimates inline
- Support navigation: arrow keys, Enter to select, q to quit
- Show real-time cost estimation as user navigates

**Libraries to Consider:**
- `prompt_toolkit` - Already in optional dependencies for REPL
- `rich.tree` - For rendering tree structure
- Custom implementation using `rich.console` for key input

**Files to Modify:**
- `src/code_guro/cli.py` - Add `--browse` flag to `analyze()` command
- Create `src/code_guro/browser.py` - New module for directory browser
- `src/code_guro/analyzer.py` - Add quick scan function for cost preview

**Edge Cases:**
- Very large directory trees (>1000 folders) - limit depth or paginate
- Symlinks - show as links, prevent infinite loops
- Permission denied folders - show as locked

**Testing Considerations:**
- Test with various directory structures
- Test keyboard navigation (arrow keys, Enter, q)
- Test on different terminal sizes
- Test with symlinks and permission-denied folders

**Estimated Effort:** 4-5 days

---

#### 2.2 Project History

**Feature Description:**
Remember recently analyzed projects for quick re-analysis.

**Usage:**
```bash
code-guro list

# Output:
# Recent projects:
#   1. my-app (analyzed 2 days ago, next.js)
#      /Users/user/projects/my-app
#   2. client-dashboard (analyzed 1 week ago, react)
#      /Users/user/projects/client-dashboard
#   3. prototype (analyzed 2 weeks ago, flask)
#      /Users/user/projects/prototype

code-guro analyze --recent 1  # Re-analyze project #1

# OR, when running with no args:
code-guro

# Output:
# What would you like to analyze?
#   1. Current directory (/Users/user/new-project)
#   2. my-app (analyzed 2 days ago)
#   3. client-dashboard (analyzed 1 week ago)
#   4. Browse for a folder
#
# Choice: 2
```

**Implementation Notes:**
- Store history in `~/.config/code-guro/history.json`
- Track: path, timestamp, framework, file count, last cost
- Add `code-guro list` command to view history
- Add `--recent <n>` flag to `analyze` command
- Integrate history into zero-argument `code-guro` flow
- Limit history to last 10 projects (configurable)

**Data Structure:**
```json
{
  "projects": [
    {
      "path": "/Users/user/projects/my-app",
      "name": "my-app",
      "last_analyzed": "2026-02-05T14:30:00Z",
      "framework": "next.js",
      "file_count": 156,
      "estimated_cost": 0.45,
      "output_dir": "/Users/user/projects/my-app/code-guro-output"
    }
  ]
}
```

**Files to Modify:**
- `src/code_guro/config.py` - Add history management functions
- `src/code_guro/cli.py` - Add `list` command, integrate into `main()` and `analyze()`
- `src/code_guro/generator.py` - Update to save project to history on completion

**Edge Cases:**
- Project moved/deleted - validate path exists before offering
- History file corrupted - gracefully handle, recreate if needed
- User privacy - add `--no-history` flag to opt out

**Testing Considerations:**
- Test history persistence across sessions
- Test with moved/deleted projects
- Test history size limit (auto-prune oldest)

**Estimated Effort:** 3-4 days

---

#### 2.3 Onboarding Flow

**Feature Description:**
First-time users see a welcome screen with a quick demo.

**Usage:**
```bash
code-guro  # First run after installation

# Output:
# 👋 Welcome to Code Guro!
#
# Code Guro helps you understand codebases by generating
# beginner-friendly documentation.
#
# Let's try a quick demo with a sample project.
#
# [Press Enter to continue, or type 'skip' to proceed to analysis]

# After Enter:
# Analyzing sample project... (5 seconds)
# ✓ Documentation generated!
#
# 📖 Preview: [opens sample HTML in browser]
#
# Now try it on your own project:
#   cd /path/to/your/project
#   code-guro
```

**Implementation Notes:**
- Detect first run (no config + no history)
- Bundle tiny sample codebase (5-10 files) in package
- Show welcome message with option to skip
- Run quick analysis on sample (pre-cached results optional)
- Open sample docs in browser
- Mark onboarding as complete in config

**Sample Project:**
- Tiny Flask/FastAPI "Hello World" app (5 files)
- Or micro Next.js app (10 files)
- Should analyze in < 10 seconds
- Serves as regression test for output quality

**Files to Modify:**
- `src/code_guro/cli.py` - Add onboarding logic to `main()`
- `src/code_guro/config.py` - Add `mark_onboarding_complete()`
- Create `src/code_guro/samples/` - Bundle sample project
- Add `code-guro demo` command to re-run demo anytime

**Configuration:**
- Add `onboarding_complete: bool` to config.json
- Add `code-guro reset-onboarding` to re-trigger (for testing)

**Testing Considerations:**
- Test first-run detection
- Test skip functionality
- Verify sample analysis completes successfully
- Test browser opening on various platforms

**Estimated Effort:** 2-3 days

---

**Phase 2 Deliverable:**
Self-explanatory tool that teaches itself. Users discover features through interaction, not documentation.

**Success Metrics:**
- Repeat usage: > 50% of users analyze more than one project
- Feature discovery: > 30% use path browser or history within first week
- Onboarding completion: > 80% complete demo

**Total Phase 2 Effort:** 1-2 weeks

---

### Phase 3: Advanced Workflows (Month 2) 🚀
**Goal:** Support more complex use cases gracefully

#### 3.1 GitHub Integration

**Feature Description:**
Seamless authentication for private repositories.

**Usage:**
```bash
code-guro analyze https://github.com/user/private-repo

# Output:
# Repository is private. Authentication required.
#
# Options:
#   1. Use GitHub CLI (gh auth login) - Recommended
#   2. Use personal access token
#   3. Cancel
#
# Choice: 1
#
# Opening GitHub authentication...
# [Opens browser for OAuth flow]
# ✓ Authenticated successfully as @username
#
# Cloning repository...
```

**Implementation Notes:**
- Detect private repo (401/403 response)
- Check for `gh` CLI installation (`which gh`)
- If present, use `gh auth token` for authentication
- If not, guide user through PAT creation
- Cache credentials securely (use system keychain via `keyring` library)
- Add `code-guro auth github` for one-time setup

**Libraries to Add:**
- `keyring` - Secure credential storage (optional dependency)
- Use existing `gitpython` for cloning with auth

**Files to Modify:**
- `src/code_guro/analyzer.py` - Update GitHub cloning logic in `analyze_codebase()`
- Create `src/code_guro/auth.py` - New module for authentication
- `src/code_guro/cli.py` - Add `auth` command group

**Edge Cases:**
- Multiple GitHub accounts - prompt for selection
- Token expiration - detect and re-authenticate
- Enterprise GitHub - support custom domains

**Security Considerations:**
- Never log or print credentials
- Use keyring for secure storage (fall back to config with warning)
- Clear credentials on logout: `code-guro auth github --logout`

**Testing Considerations:**
- Test with public repos (no auth needed)
- Test with private repos (requires auth)
- Test token refresh flow
- Mock GitHub API for CI tests

**Estimated Effort:** 5-7 days

---

#### 3.2 Batch Analysis

**Feature Description:**
Analyze multiple projects in one command.

**Usage:**
```bash
code-guro analyze-all

# Interactive browser:
# Select projects to analyze (Space to toggle, Enter to confirm):
# [x] my-app/
# [x] client-dashboard/
# [ ] old-prototype/
#
# Total estimated cost: $0.75 for 2 projects
# Proceed? [Y/n]

# OR with paths:
code-guro analyze-all ./project1 ./project2 ./project3

# Progress:
# Analyzing 3 projects...
#
# [1/3] my-app ████████████████████ 100% ✓
# [2/3] client-dashboard ████████░░░░░░░░░░ 50% ⏳
# [3/3] old-prototype [pending]
#
# Completed: 2/3 (estimated 30s remaining)
```

**Implementation Notes:**
- Add `analyze-all` command
- Support both interactive selection and path arguments
- Run analyses sequentially or in parallel (configurable)
- Show aggregate progress across all projects
- Generate consolidated index.html linking to all project docs

**Files to Modify:**
- `src/code_guro/cli.py` - Add `analyze_all()` command
- `src/code_guro/generator.py` - Add batch processing logic
- `src/code_guro/browser.py` - Add multi-select mode

**Consolidated Output:**
```
code-guro-output/
├── index.html (links to all projects)
├── my-app/
│   ├── html/...
│   └── markdown/...
├── client-dashboard/
│   ├── html/...
│   └── markdown/...
└── old-prototype/
    ├── html/...
    └── markdown/...
```

**Configuration:**
- Add `--parallel` flag for concurrent analysis
- Add `--max-workers <n>` to limit concurrency
- Add `--output <dir>` to customize output location

**Testing Considerations:**
- Test with 1, 3, 10 projects
- Test sequential vs parallel execution
- Verify consolidated index generates correctly
- Test error handling (one project fails, others continue)

**Estimated Effort:** 5-7 days

---

#### 3.3 Watch Mode

**Feature Description:**
Monitor project for changes and auto-regenerate docs.

**Usage:**
```bash
code-guro watch

# Output:
# 👀 Watching for changes in /Users/user/my-app...
#
# Press Ctrl+C to stop.
#
# [14:23:45] File changed: src/api/users.ts
# [14:23:45] Regenerating documentation... (10s)
# [14:23:55] ✓ Documentation updated
#
# [14:28:12] Files changed: src/api/users.ts, src/db/schema.ts
# [14:28:12] Waiting 5s for more changes...
# [14:28:17] Regenerating documentation... (15s)
# [14:28:32] ✓ Documentation updated
```

**Implementation Notes:**
- Add `watch` command
- Use `watchdog` library for file system events
- Debounce changes (wait 5s after last change before regenerating)
- Only regenerate affected sections (if possible)
- Display live preview URL if serving HTML

**Libraries to Add:**
- `watchdog` - File system monitoring

**Files to Modify:**
- `src/code_guro/cli.py` - Add `watch()` command
- Create `src/code_guro/watcher.py` - New module for watch logic
- `src/code_guro/generator.py` - Add incremental regeneration support

**Configuration:**
- Add `--debounce <seconds>` to adjust wait time
- Add `--ignore <pattern>` to exclude paths from watching
- Add `--serve` to auto-start HTTP server for live preview

**Advanced Feature (Optional):**
Incremental updates - only regenerate affected sections:
- File in `src/auth/` changed → regenerate `04-deep-dive-auth.md` only
- Architecture file changed → regenerate architecture section
- Requires mapping files to output sections

**Testing Considerations:**
- Test with rapid successive changes (debouncing)
- Test with large file changes
- Test with file creation, modification, deletion
- Verify Ctrl+C cleanly exits

**Estimated Effort:** 4-5 days

---

**Phase 3 Deliverable:**
Professional-grade workflows for power users and teams.

**Success Metrics:**
- GitHub analysis adoption: > 20% of analyses use GitHub URLs
- Batch analysis usage: > 10% of users analyze multiple projects
- Watch mode sessions: > 15 minutes average duration

**Total Phase 3 Effort:** 3-4 weeks

---

### Phase 4: Accessibility (Month 3) 🌐
**Goal:** Eliminate terminal requirement for truly non-technical users

#### 4.1 Local Web Interface

**Feature Description:**
Browser-based GUI for all Code Guro functionality.

**Usage:**
```bash
code-guro --gui

# Output:
# Starting Code Guro web interface...
# ✓ Server running at http://localhost:8765
#
# Opening browser...
# [Opens http://localhost:8765 in default browser]
```

**Interface Design:**

**Home Screen:**
- Large "Analyze Project" button
- Recent projects list (clickable to re-analyze)
- Provider configuration status indicator

**Analysis Flow:**
1. **Select Project:**
   - Drag-and-drop folder
   - Browse button (native file picker)
   - Enter GitHub URL
   - Select from recent

2. **Review Preview:**
   - File count, framework detected
   - Estimated cost with breakdown
   - "Analyze" button

3. **Progress View:**
   - Real-time progress bar
   - Current milestone (scanning, analyzing, generating)
   - Elapsed time and estimate

4. **Results View:**
   - Interactive documentation browser (embedded)
   - Download button (zip of markdown/HTML)
   - Share button (if hosting support added later)

**Settings Page:**
- Provider selection (radio buttons with logos)
- API key input (masked)
- Validation status indicator
- Output preferences (HTML only, markdown only, both)

**Technology Stack:**
- **Backend:** FastAPI (lightweight, async)
- **Frontend:** Plain HTML/CSS/JS (no build step) or lightweight framework (Alpine.js, htmx)
- **Styling:** Tailwind CSS (via CDN) or custom minimal CSS

**Implementation Notes:**
- Add `--gui` flag to main CLI
- Create `src/code_guro/web/` package:
  - `server.py` - FastAPI app
  - `static/` - JS/CSS assets
  - `templates/` - HTML templates (Jinja2)
- Server runs on `http://localhost:8765` (random available port)
- Auto-open browser on start (`webbrowser.open()`)
- Graceful shutdown on Ctrl+C

**API Endpoints:**
- `GET /` - Home page
- `GET /api/recent` - Recent projects list
- `POST /api/analyze` - Start analysis (returns job ID)
- `GET /api/status/<job_id>` - Check analysis progress
- `GET /api/results/<job_id>` - Get results (redirect to docs)
- `POST /api/config` - Update provider config
- `GET /api/config` - Get current config

**Files to Create:**
- `src/code_guro/web/__init__.py`
- `src/code_guro/web/server.py` - FastAPI app
- `src/code_guro/web/static/app.js` - Frontend logic
- `src/code_guro/web/static/styles.css` - Styles
- `src/code_guro/web/templates/index.html` - Main page
- `src/code_guro/cli.py` - Add `--gui` flag to `main()`

**Libraries to Add:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `jinja2` - Template engine (FastAPI dependency)
- `python-multipart` - File upload support

**Security Considerations:**
- Localhost only (no external binding)
- CORS restricted to localhost
- No authentication needed (single-user local app)
- Warn if accessed from non-localhost IP

**Testing Considerations:**
- Test server start/stop
- Test all API endpoints
- Test drag-and-drop file upload
- Test on different browsers (Chrome, Firefox, Safari)
- Test with concurrent analyses (queue jobs)

**Estimated Effort:** 2-3 weeks

---

#### 4.2 VS Code Extension (Optional)

**Feature Description:**
Integrate Code Guro directly into VS Code.

**Usage:**
1. Right-click folder in Explorer → "Analyze with Code Guro"
2. Status bar shows progress
3. Documentation opens in sidebar panel

**Features:**
- Context menu integration (right-click folder/file)
- Status bar indicator (analysis in progress)
- Sidebar webview for documentation viewing
- Command palette commands:
  - "Code Guro: Analyze Current Workspace"
  - "Code Guro: Configure Provider"
  - "Code Guro: Open Documentation"
- Settings integration (provider selection in VS Code settings)

**Technology Stack:**
- VS Code Extension API (TypeScript)
- Communicate with Code Guro CLI via `child_process`
- Webview for documentation display

**Implementation Notes:**
- Create separate repo: `code-guro-vscode`
- Extension calls `code-guro analyze` as subprocess
- Parse output to show progress in VS Code UI
- Render HTML docs in webview panel

**Files to Create (new repo):**
- `package.json` - Extension manifest
- `src/extension.ts` - Main extension code
- `src/commands.ts` - Command handlers
- `src/webview.ts` - Documentation viewer
- `README.md` - Extension documentation

**Publishing:**
- Publish to VS Code Marketplace
- Link from main Code Guro README

**Testing Considerations:**
- Test on VS Code and Cursor (both support extensions)
- Test with various workspace sizes
- Test progress reporting
- Test error handling

**Estimated Effort:** 2-3 weeks

---

#### 4.3 Desktop App (Future)

**Feature Description:**
Standalone Electron app for non-developers.

**Usage:**
- Download installer for macOS/Windows/Linux
- Double-click to install like any app
- Icon in menu bar / system tray
- Click "Analyze..." to select folder

**Features:**
- Native file picker (no terminal needed)
- Menu bar app for quick access
- Auto-updates (Electron auto-updater)
- Onboarding wizard on first launch
- Offline mode (queue analyses for when internet returns)

**Technology Stack:**
- Electron (Chromium + Node.js)
- Same FastAPI backend from web interface
- React or Vue for frontend (more polished than plain HTML)

**Implementation Notes:**
- Create separate repo: `code-guro-desktop`
- Bundle Python runtime + Code Guro package
- Use PyInstaller or Nuitka to package Python CLI
- Electron app communicates with bundled Python via IPC

**Challenges:**
- App size (bundling Python + dependencies = ~50-100MB)
- Auto-updates for Python components
- Platform-specific packaging (macOS app signing, Windows installer)

**Publishing:**
- Distribute via GitHub Releases
- Consider Mac App Store / Microsoft Store (requires signing certs)

**Estimated Effort:** 1-2 months

---

**Phase 4 Deliverable:**
Tool accessible to anyone, regardless of technical skill level.

**Success Metrics:**
- Web UI adoption: > 40% of new users start with `--gui`
- Non-developer users: Can successfully complete analysis without terminal knowledge
- Desktop app downloads: Tracks adoption beyond technical users

**Total Phase 4 Effort:** 1-2 months (3-4 months with desktop app)

---

### Phase 5: Intelligence (Month 4+) 🧠
**Goal:** Tool adapts to user preferences and improves over time

#### 5.1 Smart Suggestions

**Feature Description:**
Context-aware suggestions based on project structure and user behavior.

**Examples:**

**Monorepo Detection:**
```bash
code-guro analyze .

# Output:
# 🔍 This looks like a monorepo with 3 packages:
#   - packages/frontend (Next.js)
#   - packages/backend (Express)
#   - packages/shared (TypeScript library)
#
# Analyze all packages together? [Y/n]
# Or select specific packages: [1,2,3 or 'all']
```

**Pattern Recognition:**
```bash
# User previously analyzed /src only
code-guro analyze .

# Output:
# Last time you analyzed only the 'src/' folder.
# Do the same this time? [Y/n]
```

**Framework-Specific Suggestions:**
```bash
# Detects test files
code-guro analyze .

# Output:
# Found 45 test files (20% of codebase).
# Exclude tests from documentation? [Y/n]
```

**Implementation Notes:**
- Store analysis preferences in history (per project or global)
- Add heuristics for common patterns:
  - Monorepo: multiple `package.json` or `pyproject.toml` files
  - Test files: `test_*.py`, `*.test.ts`, `__tests__/` folders
  - Documentation: `docs/`, `*.md` files
- Use LLM for advanced pattern recognition (optional, costs tokens)

**Files to Modify:**
- `src/code_guro/analyzer.py` - Add pattern detection logic
- `src/code_guro/cli.py` - Add suggestion prompts
- `src/code_guro/config.py` - Store user preferences

**Configuration:**
- Add `smart_suggestions: bool` to config (default: true)
- Add `--no-suggestions` flag to disable per-run

**Testing Considerations:**
- Test monorepo detection with real examples (Nx, Turborepo)
- Test preference learning (requires multiple runs)
- Verify suggestions are helpful (not annoying)

**Estimated Effort:** 1-2 weeks

---

#### 5.2 Custom Profiles

**Feature Description:**
Save and share analysis preferences for consistent team workflows.

**Usage:**
```bash
# Create profile
code-guro profile create --name "team-docs"

# Configure profile
# - Exclude tests: yes
# - Output format: HTML only
# - Max depth: 2 (core files + one level of deep dives)
# - Custom prompt additions: "Focus on API endpoints"

# Save profile
code-guro profile save team-docs

# Use profile
code-guro analyze . --profile team-docs

# Export for team sharing
code-guro profile export team-docs > code-guro.config.json

# Team member imports
code-guro profile import code-guro.config.json
```

**Profile Configuration:**
```json
{
  "name": "team-docs",
  "description": "Standard documentation for API services",
  "exclude_patterns": ["**/test/**", "**/*.test.*"],
  "output_format": "html",
  "max_depth": 2,
  "custom_prompts": {
    "architecture": "Focus on API design patterns and authentication flow"
  },
  "cost_limit": 2.00,
  "auto_open_browser": true
}
```

**Files to Create:**
- `src/code_guro/profiles.py` - Profile management
- `src/code_guro/cli.py` - Add `profile` command group

**Commands:**
- `code-guro profile create` - Interactive profile creation
- `code-guro profile list` - Show all profiles
- `code-guro profile edit <name>` - Modify existing profile
- `code-guro profile delete <name>` - Remove profile
- `code-guro profile export <name>` - Export to JSON
- `code-guro profile import <file>` - Import from JSON

**Storage:**
- Profiles stored in `~/.config/code-guro/profiles/`
- Each profile is a JSON file: `team-docs.json`

**Testing Considerations:**
- Test profile creation, modification, deletion
- Test import/export roundtrip
- Verify profiles work across different projects
- Test with shared config in version control

**Estimated Effort:** 1-2 weeks

---

#### 5.3 AI-Powered Help

**Feature Description:**
Use LLM for contextual help and suggestions.

**Usage:**
```bash
code-guro help "how do I analyze just the src folder"

# Output:
# To analyze a specific folder, use:
#   code-guro analyze ./src
#
# This will analyze only files within the 'src' directory.
# Estimated cost: $0.20 (45 files detected)
#
# Related commands:
#   code-guro explain ./src - Deep dive into src folder
#   code-guro analyze . --exclude "**/test/**" - Exclude test files

code-guro suggest

# Output (based on current directory):
# Based on your project, you might want to:
#
# 1. Analyze the API layer separately:
#    code-guro explain ./src/api
#
# 2. Exclude test files to reduce cost:
#    code-guro analyze . --exclude "**/test/**"
#
# 3. Generate documentation for the frontend only:
#    code-guro analyze ./frontend
```

**Implementation Notes:**
- Add `help` command that takes natural language query
- Use selected LLM provider for query understanding
- Include current directory context in prompt
- Parse help query + file tree to generate specific suggestions
- Cache common queries to reduce API costs

**Files to Modify:**
- `src/code_guro/cli.py` - Add `help()` and `suggest()` commands
- Create `src/code_guro/ai_help.py` - LLM-powered help logic

**Cost Management:**
- Use cheaper model for help queries (e.g., Gemini Flash)
- Limit context sent (no full file contents)
- Cache responses for common queries

**Testing Considerations:**
- Test with various help queries
- Verify suggestions are relevant and accurate
- Test cost impact (should be < $0.01 per query)

**Estimated Effort:** 1 week

---

**Phase 5 Deliverable:**
A tool that learns from user behavior and provides intelligent assistance.

**Success Metrics:**
- Smart suggestions acceptance rate: > 60%
- Profile adoption: > 20% of users create custom profiles
- AI help usage: > 10% of users try help commands

**Total Phase 5 Effort:** 1-1.5 months

---

## Implementation Priorities

### Recommended Order

1. **Start with Phase 1** (1-2 weeks)
   - Highest user impact for lowest effort
   - Removes critical barriers to adoption
   - Gathers user feedback before bigger investments

2. **Validate with users before Phase 2**
   - Get feedback on improved UX
   - Identify which Phase 2 features are most desired
   - Adjust Phase 2 scope based on data

3. **Phase 2 → Phase 3** (1-2 months total)
   - Progressive enhancement of CLI experience
   - Each feature is independently valuable

4. **Evaluate GUI need before Phase 4**
   - Check if Phases 1-3 are sufficient for target users
   - GUI is large investment - validate demand first
   - Consider starting with web UI before desktop app

5. **Phase 5 is ongoing enhancement**
   - Add intelligence features based on user patterns
   - Can be implemented in parallel with earlier phases

---

## Success Metrics by Phase

### Phase 1 (Foundation)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Setup time (install to first analysis) | < 2 minutes | Instrumentation in CLI |
| Setup completion rate | > 90% | Track `code-guro configure` success |
| Time to re-configure | < 30 seconds | Track reconfigure flow |
| User satisfaction (setup) | > 4.5/5 | Post-setup survey prompt |

### Phase 2 (Discoverability)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Multi-project usage | > 50% | Track unique paths analyzed per user |
| Path browser adoption | > 30% | Track `--browse` flag usage |
| History feature usage | > 40% | Track recent project selections |
| Onboarding completion | > 80% | Track demo completions |

### Phase 3 (Advanced)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| GitHub URL analyses | > 20% | Track GitHub URL patterns |
| Batch analysis usage | > 10% | Track `analyze-all` command |
| Watch mode sessions | > 15 min avg | Track session duration |
| Private repo success rate | > 85% | Track auth flow completions |

### Phase 4 (Accessibility)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Web UI adoption | > 40% new users | Track `--gui` flag usage |
| Non-developer users | Qualitative | User interviews, feedback |
| Desktop app downloads | Growth tracking | GitHub Releases metrics |
| VS Code extension installs | > 1000 in 3 months | Marketplace analytics |

### Phase 5 (Intelligence)
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Suggestion acceptance | > 60% | Track Y/n responses |
| Profile usage | > 20% | Track custom profile creation |
| AI help queries | > 10% | Track `help` command usage |
| Repeat users (weekly) | > 30% | Track unique users per week |

---

## Technical Architecture Considerations

### Backward Compatibility

All phases must maintain backward compatibility with existing functionality:

- **Phase 1-3:** Pure CLI enhancements, no breaking changes
- **Phase 4:** Web UI is optional (`--gui` flag), doesn't affect CLI
- **Phase 5:** Smart features are opt-out (`--no-suggestions`)

### Configuration Management

As features grow, config structure evolves:

**Current config.json:**
```json
{
  "provider": "anthropic",
  "api_key_env_var": "ANTHROPIC_API_KEY"
}
```

**Phase 1 config.json:**
```json
{
  "provider": "anthropic",
  "api_key_encrypted": "...",  // New: encrypted API key storage
  "onboarding_complete": false  // New: first-run tracking
}
```

**Phase 2 config.json:**
```json
{
  "provider": "anthropic",
  "api_key_encrypted": "...",
  "onboarding_complete": true,
  "history": {  // New: project history
    "projects": [...]
  },
  "preferences": {  // New: user preferences
    "emoji_enabled": true,
    "auto_open_browser": true
  }
}
```

**Migration Strategy:**
- Add version field: `"config_version": 1`
- Write migration functions for each version bump
- Gracefully handle missing fields (use defaults)

### Dependencies Growth

| Phase | New Dependencies | Size Impact | Reasoning |
|-------|-----------------|-------------|-----------|
| 1 | `cryptography` | +5MB | API key encryption |
| 2 | None (optional: `prompt_toolkit` already present) | +0MB | Re-use existing libs |
| 3 | `keyring`, `watchdog` | +2MB | Secure storage, file watching |
| 4 | `fastapi`, `uvicorn`, `jinja2` | +10MB | Web server |
| 5 | None | +0MB | Uses existing LLM providers |

**Total growth:** ~17MB (acceptable for CLI tool)

**Mitigation:**
- Mark heavy dependencies as optional: `pip install code-guro[web]`
- Phase 4 web dependencies only needed for `--gui` users

---

## Testing Strategy

### Phase 1 Testing

**Unit Tests:**
- API key encryption/decryption roundtrip
- Config migration from old to new format
- Provider validation with all three providers

**Integration Tests:**
- End-to-end setup flow (mock API calls)
- Zero-argument `code-guro` with various directory structures
- Progress output formatting with different terminal widths

**Manual Testing:**
- Fresh install on macOS, Linux, Windows
- Test with non-technical user (observe friction points)
- Verify emoji rendering on different terminals

### Phase 2 Testing

**Unit Tests:**
- History management (add, prune, validate paths)
- Path browser navigation logic
- Onboarding flow state management

**Integration Tests:**
- Interactive path selection with mock directory tree
- Project history persistence across restarts
- Onboarding skip and complete flows

**Manual Testing:**
- Test path browser on large directory (1000+ folders)
- Verify history survives config changes
- Test onboarding on first-time user machine

### Phase 3 Testing

**Unit Tests:**
- GitHub auth token management
- Batch analysis job scheduling
- File watcher debouncing logic

**Integration Tests:**
- GitHub cloning with authentication (mock GitHub API)
- Batch analysis with 3+ projects (parallel and sequential)
- Watch mode with rapid file changes

**Manual Testing:**
- Test with real GitHub private repo
- Test batch analysis on 10 projects (performance check)
- Run watch mode for 1 hour (stability test)

### Phase 4 Testing

**Unit Tests:**
- Web API endpoint responses
- File upload handling
- WebSocket progress updates (if implemented)

**Integration Tests:**
- Full analysis flow via web UI (Selenium/Playwright)
- Concurrent analyses (multiple users on localhost)
- Browser compatibility (Chrome, Firefox, Safari)

**Manual Testing:**
- Test drag-and-drop on different OS
- Test web UI on tablet (responsive design)
- Verify localhost-only binding (security)

### Phase 5 Testing

**Unit Tests:**
- Pattern detection (monorepo, test files)
- Profile management (CRUD operations)
- AI help query parsing

**Integration Tests:**
- Smart suggestions with various project structures
- Profile import/export roundtrip
- AI help with different provider configurations

**Manual Testing:**
- Verify suggestions are helpful (not annoying)
- Test profile sharing across team members
- Validate AI help accuracy

---

## Risk Mitigation

### Risk: User confusion with too many features

**Mitigation:**
- Progressive disclosure: Start simple, reveal features gradually
- Contextual help: Show relevant tips based on current action
- Documentation: Clear examples for each feature
- Defaults: Sensible defaults that "just work"

### Risk: Increased complexity makes maintenance harder

**Mitigation:**
- Modular design: Each phase in separate modules
- Comprehensive testing: Maintain >80% code coverage
- Documentation: Update AGENTS.md with architectural decisions
- Code reviews: Require review for complex features

### Risk: API cost inflation from new features (AI help, etc.)

**Mitigation:**
- Use cheaper models for non-critical features (Gemini Flash for help)
- Cache common queries aggressively
- Add cost warnings before expensive operations
- Make AI features opt-in, not opt-out

### Risk: GUI increases support burden

**Mitigation:**
- Start with web UI (easier to update than desktop app)
- Clear error messages with troubleshooting links
- Telemetry (opt-in) to identify common issues
- Thorough testing on different platforms

### Risk: Feature creep beyond target user needs

**Mitigation:**
- Validate each phase with user feedback before next phase
- Track feature usage metrics (opt-in telemetry)
- Be willing to remove unused features
- Focus on core value: understanding codebases

---

## Resources & References

### Design Inspiration

**Interactive CLI Tools:**
- `create-react-app` - Excellent onboarding and progress feedback
- `vercel` CLI - Smart defaults and friendly output
- `gh` (GitHub CLI) - Great authentication flow
- `npm create vite` - Interactive project setup

**Web-Based Tools:**
- Railway.app - Simple project deployment UI
- Netlify - Drag-and-drop simplicity
- CodeSandbox - In-browser code editing

**Desktop Apps:**
- Postman - API testing with GUI
- Sourcetree - Git client for non-technical users
- TablePlus - Database GUI

### Technical Resources

**Libraries:**
- `rich` - Already used, expand usage for progress bars
- `prompt_toolkit` - Already in optional deps, use for interactive features
- `click` - Already used, supports command groups well
- `fastapi` - Modern Python web framework
- `watchdog` - Cross-platform file system monitoring

**Documentation:**
- [Rich documentation](https://rich.readthedocs.io/)
- [Click documentation](https://click.palletsprojects.com/)
- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [VS Code Extension API](https://code.visualstudio.com/api)

---

## Appendix: Quick Reference

### Command Evolution

| Feature | Current | Phase 1 | Phase 2 | Phase 3 |
|---------|---------|---------|---------|---------|
| Configure | `code-guro configure` | Interactive setup | + History | + `auth` command |
| Analyze | `code-guro analyze <path>` | `code-guro` (smart default) | + `--browse` | + `analyze-all` |
| Explain | `code-guro explain <path>` | (unchanged) | (unchanged) | + watch mode |
| Help | `--help` | (unchanged) | + onboarding | + AI help |

### Config File Evolution

```json
// v1 (current)
{
  "provider": "anthropic"
}

// v2 (Phase 1)
{
  "config_version": 2,
  "provider": "anthropic",
  "api_key_encrypted": "...",
  "onboarding_complete": false
}

// v3 (Phase 2)
{
  "config_version": 3,
  "provider": "anthropic",
  "api_key_encrypted": "...",
  "onboarding_complete": true,
  "history": {
    "projects": [...]
  },
  "preferences": {
    "emoji_enabled": true,
    "auto_open_browser": true
  }
}

// v4 (Phase 3+)
{
  "config_version": 4,
  "provider": "anthropic",
  "api_key_encrypted": "...",
  "onboarding_complete": true,
  "history": {...},
  "preferences": {...},
  "github_auth": {
    "token_encrypted": "..."
  },
  "profiles": {
    "active": "default",
    "available": ["default", "team-docs"]
  }
}
```

---

## Next Steps for Implementer

### Phase 1 Retrospective (Completed):

✅ **What Went Well:**
- Implementation took 7 days vs. estimated 10-14 days
- All three features delivered successfully
- No major architectural issues encountered
- Security handled appropriately with 0o600 permissions
- Backward compatibility maintained throughout

📝 **Lessons Learned:**
- Plain text storage with secure permissions was simpler than encryption
- Warning suppression significantly improved UX without code complexity
- Progress callbacks pattern worked well for decoupling concerns
- Dry-run mode proved valuable for fast previews

🔄 **Adjustments Made:**
- Skipped encryption in favor of secure file permissions (simpler, equally secure for single-user systems)
- Added selective warning suppression for cleaner output
- Implemented comprehensive edge case handling in smart defaults

---

### To Start Phase 2:

**Priority Order (Recommended):**

1. **Start with 2.3 (In-App Help):** Low risk, high value
   - Add `code-guro help` command with contextual guidance
   - Implement `--examples` flag for common scenarios
   - Quick wins that build confidence

2. **Then tackle 2.2 (Better Error Messages):** Medium complexity
   - Audit all error messages and make them actionable
   - Add `ERROR_MESSAGES` dictionary with hints
   - Important for reducing user frustration

3. **Then implement 2.4 (Output Browser):** Medium-high complexity
   - Auto-open HTML in browser after generation
   - Add `--no-open` flag for control
   - Improves discoverability of generated docs

4. **Finally add 2.1 (Interactive Path Selection):** Highest complexity
   - Optional feature, nice-to-have
   - Requires `prompt_toolkit` integration
   - Consider deferring to Phase 3 if time-constrained

**Setup Steps:**

1. **Merge Phase 1 to main:**
   - Create PR from `feature/phase-1-foundation`
   - Run full test suite
   - Update CHANGELOG.md with v0.5.0 release notes

2. **Create Phase 2 branch:**
   - `git checkout -b feature/phase-2-discoverability`
   - Start with smallest feature (2.3 in-app help)

3. **Review Phase 2 requirements:**
   - Read sections 2.1-2.4 in this document
   - Identify dependencies and integration points
   - Plan implementation order

**Questions to Consider:**

1. **Browser Auto-Open:** Default on or off?
   - Recommendation: Default ON with `--no-open` flag (better discoverability)

2. **Interactive Path Browser:** Worth the complexity?
   - Recommendation: Phase 3 feature - focus on higher-impact items first

3. **Help System:** Integrated or separate docs?
   - Recommendation: Both - integrated for common tasks, link to full docs for advanced

4. **Error Message Tone:** Technical or conversational?
   - Recommendation: Conversational with technical details in "Show more" section

---

### Config File Evolution (Updated)

```json
// v1 (pre-Phase 1)
{
  "provider": "anthropic"
}

// v2 (Phase 1 - CURRENT)
{
  "config_version": 2,
  "provider": "anthropic",
  "api_keys": {
    "anthropic": "sk-ant-...",
    "openai": null,
    "google": null
  },
  "preferences": {
    "emoji_enabled": true
  }
}

// v3 (Phase 2 - PLANNED)
{
  "config_version": 3,
  "provider": "anthropic",
  "api_keys": {...},
  "preferences": {
    "emoji_enabled": true,
    "auto_open_browser": true,
    "output_format": "html"
  },
  "history": {
    "last_analyzed": "/path/to/project",
    "recent_projects": [...]
  }
}

// v4 (Phase 3+ - FUTURE)
{
  "config_version": 4,
  "provider": "anthropic",
  "api_keys": {...},
  "preferences": {...},
  "history": {...},
  "github_auth": {
    "token": "ghp_..."
  }
}
```

---

**Document Version:** 1.1
**Last Updated:** February 7, 2026 (Phase 1 completion)
**Next Review:** After Phase 2 completion
