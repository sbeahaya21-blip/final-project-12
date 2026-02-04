# How to Check if Backend is Running

## Quick Check Methods

### Method 1: Open in Browser
Open this URL in your browser:
```
http://localhost:8000/health
```

**If backend is running:** You'll see:
```json
{"status":"healthy","service":"invoice-parser"}
```

**If backend is NOT running:** You'll get a connection error or "This site can't be reached"

---

### Method 2: Check API Documentation
Open this URL:
```
http://localhost:8000/docs
```

**If backend is running:** You'll see the Swagger API documentation page

**If backend is NOT running:** You'll get a connection error

---

### Method 3: Command Line (PowerShell)
```powershell
Test-NetConnection -ComputerName localhost -Port 8000
```

If it says "TcpTestSucceeded : True", the backend is running.

---

## Start the Backend

If the backend is NOT running, start it:

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

## Verify It's Working

After starting, test it:

1. **Health check:** http://localhost:8000/health
2. **API docs:** http://localhost:8000/docs
3. **List invoices:** http://localhost:8000/api/invoices

---

## Important Notes

- ✅ **Backend must be running** for the frontend to work
- ✅ **Keep the terminal open** - closing it stops the server
- ✅ **Backend runs on port 8000**
- ✅ **Frontend runs on port 3000** (different terminal)

---

## Quick Test

Open your browser and go to:
- http://localhost:8000/health

If you see `{"status":"healthy"}`, the backend is running! ✅
