#!/bin/bash

# Fix GitHub submodule issue for final project
# Run this script in Git Bash from the C:\Users\Admin directory

echo "========================================"
echo "Fixing GitHub Submodule Issue"
echo "========================================"
echo ""

# Navigate to home directory
cd /c/Users/Admin

echo "Step 1: Removing submodule reference..."
git rm --cached "Desktop/אוטומציה/final project" 2>/dev/null || echo "Warning: Could not remove submodule reference (may not exist)"

echo ""
echo "Step 2: Removing .git folder from final project..."
if [ -d "Desktop/אוטומציה/final project/.git" ]; then
    echo "Found .git folder, removing it..."
    rm -rf "Desktop/אוטומציה/final project/.git"
    echo ".git folder removed successfully"
else
    echo "No .git folder found (may have been removed already)"
fi

echo ""
echo "Step 3: Adding final project files as regular files..."
git add "Desktop/אוטומציה/final project/" || {
    echo "Error: Failed to add files. Please check the path."
    exit 1
}

echo ""
echo "Step 4: Checking what will be committed..."
git status --short | grep -i "final project" | head -20

echo ""
echo "Step 5: Committing changes..."
git commit -m "Fix: Convert final project from submodule to regular files" || {
    echo "Warning: Commit failed or no changes to commit"
}

echo ""
echo "Step 6: Pushing to GitHub..."
git push origin main || {
    echo "Error: Failed to push. You may need to pull first or check your credentials."
    exit 1
}

echo ""
echo "========================================"
echo "Done! The final project folder should now"
echo "be visible with all its files on GitHub."
echo "========================================"
