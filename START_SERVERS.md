# How to Start Both Servers

## The Problem
You're getting "Network Error" because the backend server is not running.

## Solution: Start Both Servers

You need **TWO terminals** - one for backend, one for frontend.

---

## Terminal 1: Start Backend Server

1. **Open a terminal** (Git Bash, PowerShell, or Command Prompt)

2. **Navigate to project folder:**
   ```bash
   cd "C:\Users\Admin\Desktop\אוטומציה\final project"
   ```

3. **Start the backend:**
   ```bash
   python run.py
   ```

4. **You should see:**
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

5. **Keep this terminal open!** The server must stay running.

---

## Terminal 2: Start Frontend Server

1. **Open a NEW terminal** (keep the backend terminal running!)

2. **Navigate to frontend folder:**
   ```bash
   cd "C:\Users\Admin\Desktop\אוטומציה\final project\frontend"
   ```

3. **Fix PATH (if needed):**
   ```bash
   export PATH="/c/Program Files/nodejs:$PATH"
   ```

4. **Start the frontend:**
   ```bash
   npm run dev
   ```

5. **You should see:**
   ```
   VITE v5.x.x  ready in xxx ms

   ➜  Local:   http://localhost:3000/
   ➜  Network: use --host to expose
   ```

6. **Keep this terminal open too!**

---

## Now Test the Upload

1. **Open your browser:**
   - Go to: http://localhost:3000

2. **Upload a PDF:**
   - Drag and drop a PDF from `sample_invoices\pdf\` folder
   - Or click "Choose File"

3. **It should work now!** ✅

---

## Quick Check: Are Both Running?

### Check Backend (port 8000):
Open browser and go to: http://localhost:8000/health
- Should show: `{"status":"healthy","service":"invoice-parser"}`

### Check Frontend (port 3000):
Open browser and go to: http://localhost:3000
- Should show the upload page

### Check API:
Open browser and go to: http://localhost:8000/docs
- Should show the API documentation

---

## Troubleshooting

### "Port 8000 already in use"
- Another process is using port 8000
- Stop it or change the port in `run.py`

### "Port 3000 already in use"
- Another process is using port 3000
- Vite will automatically use another port (check the terminal output)

### "python: command not found"
- Python is not in PATH
- Try: `py run.py` instead

### "npm: command not found"
- Node.js is not in PATH
- Run: `export PATH="/c/Program Files/nodejs:$PATH"` first

---

## Summary

✅ **Backend running** on http://localhost:8000  
✅ **Frontend running** on http://localhost:3000  
✅ **Both terminals open**  
✅ **Upload should work!**
