#!/bin/bash
# Helper script to start a new feature following the workflow

set -e

echo "🚀 AetherLink Feature Workflow Helper"
echo "===================================="
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "   Install: https://cli.github.com/"
    exit 1
fi

# Get feature title
read -p "Feature title: " title
if [ -z "$title" ]; then
    echo "❌ Title is required"
    exit 1
fi

# Get description
echo "Feature description (press Ctrl+D when done):"
description=$(cat)

# Get labels
echo ""
echo "Select priority:"
echo "  1) priority:high"
echo "  2) priority:medium"
echo "  3) priority:low"
read -p "Choice (1-3): " priority_choice

case $priority_choice in
    1) priority="priority:high" ;;
    2) priority="priority:medium" ;;
    3) priority="priority:low" ;;
    *) priority="priority:medium" ;;
esac

echo ""
echo "Select scope:"
echo "  1) backend"
echo "  2) frontend"
echo "  3) both"
read -p "Choice (1-3): " scope_choice

case $scope_choice in
    1) scope_labels="backend" ;;
    2) scope_labels="frontend" ;;
    3) scope_labels="backend,frontend" ;;
    *) scope_labels="" ;;
esac

# Create issue
echo ""
echo "📝 Creating GitHub issue..."
issue_url=$(gh issue create \
    --title "feat: $title" \
    --body "$description" \
    --label "feature,$priority,$scope_labels" \
    2>&1)

# Extract issue number
issue_number=$(echo "$issue_url" | grep -oP 'issues/\K[0-9]+')

if [ -z "$issue_number" ]; then
    echo "❌ Failed to create issue"
    exit 1
fi

echo "✅ Created issue #$issue_number"
echo "   $issue_url"

# Create branch name from title
branch_name=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')
branch="feature/${issue_number}-${branch_name}"

echo ""
echo "🌿 Creating branch: $branch"
git checkout -b "$branch"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Make your changes"
echo "  2. Commit: git commit -m 'feat: $title'"
echo "  3. Push: git push origin $branch"
echo "  4. Create PR: gh pr create --title 'feat: $title' --base main"
echo "  5. After merge, tag: git tag -a v0.X.0 -m 'Release v0.X.0'"
