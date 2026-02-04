# Fix Node.js PATH in Git Bash

## Quick Fix (Temporary - Current Session Only)

Run this in your Git Bash:

```bash
export PATH="/c/Program Files/nodejs:$PATH"
node --version
npm --version
```

If that works, you can now run:
```bash
cd frontend
npm install
npm run dev
```

---

## Permanent Fix (Recommended)

### Option 1: Use the Start Script

I've created a script that fixes the PATH automatically:

```bash
bash start_frontend.sh
```

This will:
1. Fix the PATH for Node.js
2. Install dependencies (if needed)
3. Start the React dev server

---

### Option 2: Add to Git Bash Profile (Permanent)

1. Open Git Bash
2. Edit your `.bashrc` file:
   ```bash
   notepad ~/.bashrc
   ```
   (Or use any text editor)

3. Add this line at the end:
   ```bash
   export PATH="/c/Program Files/nodejs:$PATH"
   ```

4. Save and close
5. Restart Git Bash or run:
   ```bash
   source ~/.bashrc
   ```

Now `node` and `npm` will work in all new Git Bash sessions!

---

### Option 3: Reinstall Node.js with PATH Option

1. Download Node.js installer again: https://nodejs.org/
2. Run the installer
3. **IMPORTANT**: Make sure "Add to PATH" option is checked
4. Complete installation
5. Restart Git Bash

---

## Quick Test

After fixing PATH, test it:

```bash
node --version
npm --version
```

You should see version numbers like:
- `v18.x.x` or `v20.x.x`
- `9.x.x` or `10.x.x`

---

## Then Start Frontend

Once Node.js is working:

```bash
cd frontend
npm install    # Only needed first time
npm run dev    # Start development server
```

Open http://localhost:3000 in your browser!
