# GitHub Setup Guide - Using Personal Access Token

## Problem: Didn't receive GitHub authorization code

If you didn't receive the code for device authorization, use a **Personal Access Token** instead.

## Step 1: Create a Personal Access Token

1. **Go to GitHub:**
   - Open: https://github.com/settings/tokens
   - Or: GitHub → Your Profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click **"Generate new token"** → **"Generate new token (classic)"**
   - Give it a name: `Invoice Parser Project`
   - Set expiration: Choose your preference (90 days, 1 year, or no expiration)
   - Select scopes:
     - ✅ **repo** (Full control of private repositories)
     - ✅ **workflow** (if you want to use GitHub Actions)

3. **Generate and Copy:**
   - Click **"Generate token"**
   - **⚠️ IMPORTANT:** Copy the token immediately! You won't see it again.
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 2: Initialize Git Repository (if not done)

```bash
# Navigate to your project
cd "C:\Users\Admin\Desktop\אוטומציה\final project"

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Invoice Parser and Anomaly Detection System"
```

## Step 3: Create GitHub Repository

1. **Go to GitHub:**
   - Visit: https://github.com/new
   - Or: Click "+" → "New repository"

2. **Repository Settings:**
   - Name: `invoice-parser-anomaly-detection` (or your preferred name)
   - Description: "Invoice Parser and AI Invoice Anomaly & Fraud Detection System"
   - Visibility: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have files)

3. **Click "Create repository"**

## Step 4: Push to GitHub Using Token

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push using token as password
git push -u origin main
```

**When prompted:**
- **Username:** `sbeahaya21-blip` (or your GitHub username)
- **Password:** Paste your **Personal Access Token** (not your GitHub password!)

## Step 5: Verify

Check your GitHub repository - all files should be there!

## Alternative: Use GitHub CLI

If you prefer, install GitHub CLI:

```bash
# Install GitHub CLI (if not installed)
# Download from: https://cli.github.com/

# Login
gh auth login

# Create and push repository
gh repo create invoice-parser-anomaly-detection --public --source=. --remote=origin --push
```

## Troubleshooting

### If push fails:
- Make sure you're using the **token** as password, not your GitHub password
- Check that the token has `repo` scope
- Verify the repository URL is correct

### If you get "remote already exists":
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

## Security Note

⚠️ **Never commit these files:**
- `.env` files with secrets
- `ERPnext-API KEY.txt` (if it contains API keys)
- Any files with passwords or API keys

Consider adding them to `.gitignore`:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "ERPnext-API KEY.txt" >> .gitignore
```
