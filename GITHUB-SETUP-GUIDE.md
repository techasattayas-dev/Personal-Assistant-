# GitHub Setup Guide - Personal Assistant System

**Purpose**: Connect your entire Personal Assistant system to GitHub for version control, backup, and sync across devices.

**Created**: 2026-03-11

---

## 🎯 Why Use GitHub for This System?

### Benefits:
✅ **Automatic Backup** - All your notes, plans, and research backed up to cloud
✅ **Version History** - See what changed and when, undo mistakes
✅ **Sync Across Devices** - Access from Mac, iPhone, iPad, web
✅ **Collaboration** - Share specific folders with team members
✅ **Free** - GitHub offers free private repositories

---

## 📋 Prerequisites

Before starting, make sure you have:
- [ ] GitHub account (free) - Sign up at https://github.com
- [ ] Git installed on your Mac
- [ ] Terminal access

---

## 🚀 Step-by-Step Setup

### Step 1: Check if Git is Installed

Open Terminal and run:
```bash
git --version
```

**Expected Output**: `git version 2.x.x`

**If not installed**:
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Git
brew install git
```

---

### Step 2: Configure Git (One-Time Setup)

Set your name and email (will appear in commits):

```bash
# Replace with your actual name and email
git config --global user.name "Wut"
git config --global user.email "your-email@example.com"

# Check configuration
git config --global --list
```

---

### Step 3: Initialize Git Repository

Navigate to your Personal Assistant folder:

```bash
cd "/Users/wuud/Desktop/Claude_Personal Assistance"

# Initialize Git repository
git init

# Check status
git status
```

---

### Step 4: Create .gitignore File

**Important**: Some files should NOT be uploaded to GitHub (sensitive data, large files, temporary files).

The `.gitignore` file is already created for you. Review it:

**File**: `/Users/wuud/Desktop/Claude_Personal Assistance/.gitignore`

**Contents**:
```
# Sensitive Files - NEVER commit these
config/integrations.json
**/*credentials*.json
**/*password*.txt
**/*api-key*.txt
.env
*.key

# Sync Logs (can be large)
Integrations/*/sync-log.md
Integrations/*/change-log.md

# Temporary Files
*.tmp
*.temp
.DS_Store
Thumbs.db

# Large Media Files (optional - uncomment if you have many)
# *.mp4
# *.mov
# *.zip
# *.pdf

# System Files
.Spotlight-V100
.Trashes
```

**To customize**, edit this file and add patterns for files you don't want to sync.

---

### Step 5: Create GitHub Repository

#### Option A: Via GitHub Website (Recommended for Beginners)

1. Go to https://github.com
2. Click **"+"** (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `personal-assistant` (or your choice)
   - **Description**: "My Personal Assistant System - PARA + Zettelkasten"
   - **Privacy**: ⚠️ **Select "Private"** (recommended for personal data)
   - **DO NOT** initialize with README (we already have one)
4. Click **"Create repository"**
5. **Copy the repository URL** (looks like: `https://github.com/yourusername/personal-assistant.git`)

#### Option B: Via GitHub CLI (Advanced)

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Create private repository
gh repo create personal-assistant --private --source=. --remote=origin
```

---

### Step 6: Connect Local Repository to GitHub

Using the URL from Step 5:

```bash
cd "/Users/wuud/Desktop/Claude_Personal Assistance"

# Add remote repository (replace URL with yours)
git remote add origin https://github.com/yourusername/personal-assistant.git

# Verify remote is added
git remote -v
```

**Expected Output**:
```
origin  https://github.com/yourusername/personal-assistant.git (fetch)
origin  https://github.com/yourusername/personal-assistant.git (push)
```

---

### Step 7: First Commit - Upload Everything

```bash
cd "/Users/wuud/Desktop/Claude_Personal Assistance"

# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status

# Create first commit
git commit -m "Initial commit: Personal Assistant System setup

- PARA structure (Projects, Areas, Resources, Archive)
- Zettelkasten knowledge base
- Vacation planning system
- News intelligence framework
- Myanmar compliance research
- FOODEX Japan 2026 trip planning"

# Push to GitHub
git push -u origin main
```

**Note**: If you get an error about branch name, use:
```bash
git branch -M main
git push -u origin main
```

---

### Step 8: Verify Upload

1. Go to your GitHub repository: `https://github.com/yourusername/personal-assistant`
2. You should see all your folders and files
3. Check that sensitive files (credentials, API keys) are NOT visible

---

## 📅 Daily Workflow - How to Sync Changes

### After Making Changes (New notes, updated files, etc.)

**Quick Method** (3 commands):
```bash
cd "/Users/wuud/Desktop/Claude_Personal Assistance"

# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Update: [brief description of what changed]"

# Push to GitHub
git push
```

### **Example Daily Commits**:

**After adding Japan trip notes**:
```bash
git add .
git commit -m "Add: FOODEX Japan 2026 visual dining guide"
git push
```

**After research session**:
```bash
git add .
git commit -m "Research: Myanmar seed law compliance analysis"
git push
```

**After daily planning**:
```bash
git add .
git commit -m "Update: Daily log March 11 and weekly review"
git push
```

---

## 🔄 Syncing Across Multiple Devices

### On Another Computer/Device:

**First Time Setup**:
```bash
# Clone repository to new location
git clone https://github.com/yourusername/personal-assistant.git

cd personal-assistant
```

**Daily Usage**:
```bash
cd personal-assistant

# Get latest changes from GitHub
git pull

# Make your changes...

# Push changes back
git add .
git commit -m "Update: [description]"
git push
```

---

## 📝 Useful Git Commands

### Check Status
```bash
# See what files changed
git status

# See detailed changes
git diff
```

### View History
```bash
# See commit history
git log --oneline

# See last 10 commits
git log --oneline -10

# See changes in specific file
git log --oneline -- "path/to/file.md"
```

### Undo Changes
```bash
# Discard changes in file (before commit)
git checkout -- filename.md

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

### View Old Versions
```bash
# See file as it was in previous commit
git show HEAD~1:path/to/file.md

# Restore file from previous commit
git checkout HEAD~1 -- path/to/file.md
```

---

## 🔐 Security Best Practices

### What to NEVER Commit:

❌ **API Keys & Credentials**
- Gmail API credentials
- Notion API tokens
- Google Calendar OAuth tokens
- Any file with "password", "secret", "key" in name

❌ **Personal Financial Data**
- Bank account numbers
- Credit card details
- Tax information

❌ **Sensitive Business Data**
- Confidential contracts
- Proprietary formulas
- Employee personal information

✅ **Safe to Commit**:
- Notes, plans, research
- Templates and configurations (without credentials)
- Trip planning documents
- Knowledge base articles
- Meeting notes (non-confidential)

### If You Accidentally Commit Sensitive Data:

⚠️ **IMMEDIATE ACTION REQUIRED**:

```bash
# Remove file from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file.txt" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to GitHub
git push origin --force --all

# Change the exposed credential immediately!
```

**Better**: Delete repository and create new one if sensitive data was exposed.

---

## 📱 GitHub Mobile App

### Access on iPhone/iPad:

1. Download **"GitHub"** app from App Store
2. Sign in with your account
3. Browse repositories, view files, see commit history
4. **Cannot edit** files directly (read-only on mobile)

**For editing on mobile**: Use GitHub web interface or apps like Working Copy (iOS Git client)

---

## 🤝 Sharing with Team Members

### To Share Specific Folders Only:

**Option 1: Share Entire Repository**
```bash
# On GitHub website:
Repository → Settings → Collaborators → Add people
```

**Option 2: Create Separate Repository for Shared Content**
```bash
# Create new repo for shared items only
# Copy specific folders there
# Invite collaborators to that repo
```

**Recommended Structure for Sharing**:
- **Personal Repository** (private): All your personal notes
- **Team Repository** (private): Only work-related shared documents

---

## 📊 GitHub Desktop App (Alternative to Command Line)

**Easier than Terminal** - Visual interface for Git

### Install:
1. Download from: https://desktop.github.com
2. Install and sign in with GitHub account
3. Add existing repository: `/Users/wuud/Desktop/Claude_Personal Assistance`

### Usage:
1. **See changes**: Visual diff of what changed
2. **Commit**: Write message and click "Commit to main"
3. **Push**: Click "Push origin" to sync to GitHub
4. **Pull**: Click "Fetch origin" to get updates

**Recommended for beginners** - No need to remember commands!

---

## 🔄 Automated Sync (Advanced)

### Option 1: Cron Job (Mac Automation)

Auto-commit every day at 8 PM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 20 * * * cd "/Users/wuud/Desktop/Claude_Personal Assistance" && git add . && git commit -m "Auto-sync: $(date '+\%Y-\%m-\%d')" && git push
```

### Option 2: Folder Action (AppleScript)

Auto-commit when files change - requires more setup.

### Option 3: Use VS Code

If you use VS Code editor:
1. Open folder in VS Code
2. Source Control panel shows changes automatically
3. Click "+" to stage, write message, click "✓" to commit
4. Click "..." → "Push" to sync

---

## 🆘 Common Issues & Solutions

### Issue 1: "Permission denied (publickey)"

**Solution**: Set up SSH key or use HTTPS with Personal Access Token

**Quick Fix (HTTPS)**:
```bash
# Use HTTPS URL instead of SSH
git remote set-url origin https://github.com/yourusername/personal-assistant.git
```

**GitHub now requires Personal Access Token**:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo` (full control)
4. Copy token
5. Use token as password when pushing

### Issue 2: "fatal: refusing to merge unrelated histories"

**Solution**:
```bash
git pull origin main --allow-unrelated-histories
```

### Issue 3: Merge Conflicts

**What it means**: Same file edited in two places

**Solution**:
```bash
# See conflicted files
git status

# Open file, look for markers:
<<<<<<< HEAD
Your changes
=======
Changes from GitHub
>>>>>>> origin/main

# Edit file to resolve conflict
# Then:
git add .
git commit -m "Resolve merge conflict"
git push
```

### Issue 4: Large Files

GitHub has 100MB file size limit.

**Solution**:
```bash
# Add to .gitignore
echo "*.mp4" >> .gitignore
echo "*.zip" >> .gitignore

# Or use Git LFS for large files
git lfs install
git lfs track "*.mp4"
```

---

## 📚 Recommended Learning Resources

### Beginner:
- **GitHub Guides**: https://guides.github.com
- **GitHub Desktop Tutorial**: Built into app
- **Git Basics**: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics

### Intermediate:
- **Branching**: Learn to create feature branches
- **Pull Requests**: Collaborate with others
- **GitHub Actions**: Automate workflows

---

## ✅ Quick Setup Checklist

Use this checklist to set up GitHub for your system:

### Initial Setup (One Time):
- [ ] Create GitHub account
- [ ] Install Git on Mac
- [ ] Configure Git (name + email)
- [ ] Review .gitignore file
- [ ] Create private GitHub repository
- [ ] Initialize local Git repository
- [ ] Connect local to GitHub
- [ ] Make first commit and push
- [ ] Verify files on GitHub website

### Daily Workflow:
- [ ] Make changes to files (notes, plans, research)
- [ ] `git add .`
- [ ] `git commit -m "Update: [description]"`
- [ ] `git push`

### Weekly:
- [ ] Review commit history
- [ ] Check .gitignore is working
- [ ] Verify no sensitive data committed

---

## 🎯 Next Steps After Setup

Once GitHub is set up, you can:

1. **Access from anywhere**: Clone to work computer, home computer
2. **Mobile viewing**: Use GitHub app to read notes on phone
3. **Backup strategy**: Your data is now backed up automatically
4. **Version control**: Roll back to any previous version
5. **Collaboration**: Share specific folders with team members
6. **Automation**: Set up auto-sync with cron jobs

---

## 📞 Need Help?

### Resources:
- **GitHub Support**: https://support.github.com
- **Git Documentation**: https://git-scm.com/doc
- **Ask me**: I can help with specific Git commands or issues

### Common Commands Quick Reference:

```bash
# Daily workflow
git add .
git commit -m "message"
git push

# Get updates
git pull

# Check status
git status

# View history
git log --oneline

# Undo changes
git checkout -- filename.md
```

---

**Setup Status**: ⏳ Ready to Configure

**Next Action**: Follow Step 1 to check Git installation

**Estimated Setup Time**: 15-20 minutes for first-time setup

**Difficulty**: ⭐⭐☆☆☆ (Beginner-friendly with this guide)

---

**Last Updated**: 2026-03-11
**System**: Personal Assistant - PARA + Zettelkasten
**Privacy**: Recommended to use **private repository**
