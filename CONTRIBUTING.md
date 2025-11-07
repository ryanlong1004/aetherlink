# Contributing to AetherLink

Thank you for contributing to AetherLink! This guide ensures consistent workflow across all features.

## Development Workflow

We follow a structured GitHub-based workflow for all features and fixes:

### 1. Create a GitHub Issue

Before starting any work, create a detailed issue:

```bash
gh issue create \
  --title "feat: Your feature title" \
  --body "## Problem
Describe the current situation...

## Proposed Solution
Explain what you'll implement...

## Technical Implementation
List files to modify, dependencies, etc...

## Testing Checklist
- [ ] Test case 1
- [ ] Test case 2

## Success Criteria
Define what 'done' looks like..." \
  --label "feature" \
  --label "priority:medium"
```

**Required labels:**

- Type: `feature`, `bug`, `enhancement`, `documentation`
- Priority: `priority:high`, `priority:medium`, `priority:low`
- Scope: `backend`, `frontend`, or both

### 2. Create Feature Branch

Create a branch named after the issue:

```bash
# For issue #5
git checkout -b feature/5-descriptive-name

# For bugs
git checkout -b fix/5-bug-description
```

**Branch naming convention:**

- Features: `feature/[issue-number]-short-description`
- Bugs: `fix/[issue-number]-bug-description`
- Docs: `docs/[issue-number]-what-changed`

### 3. Implement Changes

Work on your feature following these guidelines:

**Code Style:**

- Backend: Follow PEP 8 for Python (use `black` formatter)
- Frontend: Use Vue 3 Composition API with TypeScript
- Keep lines under 80 characters where possible
- Write descriptive variable and function names

**Testing:**

- Test locally before committing
- Ensure both API and frontend run without errors
- Verify existing functionality still works

**Commits:**

- Make atomic commits (one logical change per commit)
- Use conventional commit messages (see below)

### 4. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**

```bash
git commit -m "feat(websocket): Add real-time network updates

- Implement WebSocket manager service
- Add /ws/network endpoint
- Replace polling in Dashboard component
- Add connection status indicator

Closes #1"
```

```bash
git commit -m "fix(api): Properly serialize ChartDataPoint objects

- Use model_dump(mode='json') for Pydantic serialization
- Fixes WebSocket broadcast errors"
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/5-your-feature

# Create pull request
gh pr create \
  --title "feat: Your feature title" \
  --body "## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Testing
- [x] Tested locally
- [x] All existing tests pass
- [x] Added new tests

## Related Issue
Closes #5" \
  --base main
```

**PR Requirements:**

- Link to the issue (use "Closes #X")
- Describe what changed and why
- List testing performed
- Include screenshots for UI changes

### 6. Tag Releases

After merging to main, tag with semantic versioning:

```bash
# Checkout main and pull latest
git checkout main
git pull

# Tag the release
git tag -a v0.3.0 -m "Release v0.3.0: Add device detail pages"

# Push the tag
git push origin v0.3.0
```

**Semantic Versioning:**

- `MAJOR.MINOR.PATCH` (e.g., v1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

## Quick Reference

### Full Workflow Example

```bash
# 1. Create issue
gh issue create --title "feat: Add dark mode" \
  --label "feature" --label "frontend" --label "priority:medium"

# Note the issue number (e.g., #7)

# 2. Create branch
git checkout -b feature/7-dark-mode

# 3. Make changes and commit
git add .
git commit -m "feat(ui): Implement dark/light theme toggle

- Add theme switcher component
- Update Tailwind config
- Add localStorage persistence

Closes #7"

# 4. Push and create PR
git push origin feature/7-dark-mode
gh pr create --title "feat: Add dark mode" --base main

# 5. After merge, tag release
git checkout main
git pull
git tag -a v0.3.0 -m "Release v0.3.0: Dark mode support"
git push origin v0.3.0
```

## Labels

Ensure these labels exist in your repository:

**Type:**

- `feature` - New feature
- `bug` - Bug fix
- `enhancement` - Enhancement to existing feature
- `documentation` - Documentation updates

**Priority:**

- `priority:high` - High priority
- `priority:medium` - Medium priority
- `priority:low` - Low priority

**Scope:**

- `backend` - Backend/API changes
- `frontend` - Frontend/UI changes

**Status:**

- `in-progress` - Currently being worked on
- `needs-review` - Ready for review
- `blocked` - Blocked by dependencies

## Project Structure

```
aetherlink/
├── api-service/          # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Application entry
│   │   ├── models/      # Pydantic models
│   │   ├── routers/     # API endpoints
│   │   └── services/    # Business logic
│   └── requirements.txt
├── components/           # Vue components
├── pages/               # Nuxt pages
├── assets/              # Styles and static assets
├── public/              # Public files
├── CONTRIBUTING.md      # This file
├── README.md           # Project overview
└── package.json        # Frontend dependencies
```

## Getting Help

- Check existing issues and PRs
- Read the [README.md](README.md)
- Review [INTEGRATION.md](INTEGRATION.md) for API integration
- Ask in discussions if stuck

## Code Review

When reviewing PRs:

- Check code follows style guidelines
- Verify tests pass
- Test functionality locally if possible
- Provide constructive feedback
- Approve when ready

---

Thank you for following these guidelines! They help maintain code quality and project consistency.
