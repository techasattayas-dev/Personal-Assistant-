#!/bin/bash

# Personal Assistant - GitHub Update Script
# Usage: Just say "update git" to Claude, or run ./update-git.sh manually

echo "🔄 Starting GitHub sync..."
echo ""

# Navigate to Personal Assistant directory
cd "/Users/wuud/Desktop/Claude_Personal Assistance"

# Check for changes
if [[ -z $(git status -s) ]]; then
    echo "✅ No changes to sync - everything is up to date!"
    exit 0
fi

# Show what changed
echo "📝 Files changed:"
git status -s
echo ""

# Add all changes
echo "📦 Staging changes..."
git add .

# Create commit with timestamp
COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M') - Auto-sync"
echo "💾 Creating commit: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo "☁️  Pushing to GitHub..."
git push

# Check if push was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! All changes synced to GitHub"
    echo "🕐 Synced at: $(date '+%Y-%m-%d %H:%M:%S')"
else
    echo ""
    echo "❌ ERROR: Push failed. Check your internet connection or GitHub credentials."
    exit 1
fi
