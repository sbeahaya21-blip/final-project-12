# Start React Frontend - Quick Guide

## Important: Restart Your Terminal First! 🔄

After installing Node.js, you **must restart your terminal/Git Bash** for it to recognize the `node` and `npm` commands.

---

## Step 1: Restart Terminal

1. **Close** your current Git Bash/PowerShell window
2. **Open a new** Git Bash/PowerShell window
3. Navigate to the project:
   ```bash
   cd "C:\Users\Admin\Desktop\אוטומציה\final project"
   ```

## Step 2: Verify Node.js

```bash
node --version
npm --version
```

You should see version numbers. If not, Node.js might not be installed correctly.

## Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

This will take a minute or two to download all packages.

## Step 4: Start Development Server

```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

## Step 5: Open in Browser

Open your browser and go to:
**http://localhost:3000**

---

## Alternative: Quick Setup Script

If you're in Git Bash, you can use:

```bash
bash setup_frontend_now.sh
```

This will do steps 3-4 automatically.

---

## Troubleshooting

### "node: command not found"
- **Restart your terminal** after installing Node.js
- Check if Node.js is installed: Look for "Node.js" in Start Menu
- Reinstall Node.js if needed

### "npm: command not found"
- Same as above - restart terminal
- npm comes with Node.js, so if node works, npm should too

### Port 3000 already in use
- Stop any other process using port 3000
- Or the dev server will automatically use another port

### Installation errors
- Make sure you have internet connection
- Try: `npm cache clean --force` then `npm install` again

---

## What You'll See

Once running, you'll have:
- **Modern React UI** at http://localhost:3000
- **Full navigation** between pages
- **Invoice list view**
- **Detailed invoice view**
- **Real-time analysis**

The React frontend is much more polished than the simple HTML version!
