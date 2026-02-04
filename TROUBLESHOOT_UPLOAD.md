# Troubleshooting Upload Network Error

## The Problem
You're seeing "Network Error" when trying to upload an invoice. This means the frontend can't connect to the backend API.

## Quick Fix Steps

### Step 1: Check if Backend is Running

Open a new terminal and check:

```bash
# Check if backend is running
curl http://localhost:8000/health
```

If you get an error or no response, the backend is NOT running.

### Step 2: Start the Backend Server

In a terminal, navigate to your project folder and run:

```bash
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!** The server must stay running.

### Step 3: Check Frontend Configuration

The frontend should be running on port 3000 and proxying to port 8000.

If you're running the frontend with `npm run dev`, it should automatically proxy API calls.

### Step 4: Verify Both Servers are Running

You need BOTH servers running:

1. **Backend** (port 8000):
   ```bash
   python run.py
   ```

2. **Frontend** (port 3000):
   ```bash
   cd frontend
   export PATH="/c/Program Files/nodejs:$PATH"  # If needed
   npm run dev
   ```

### Step 5: Check Browser Console

1. Open your browser's Developer Tools (F12)
2. Go to the "Console" tab
3. Look for error messages
4. Go to the "Network" tab
5. Try uploading again
6. Check if the request to `/api/invoices/upload` is failing

## Common Issues & Solutions

### Issue 1: Backend Not Running
**Solution:** Start the backend with `python run.py`

### Issue 2: CORS Error
**Solution:** The backend should handle CORS. Make sure you're using the dev server (`npm run dev`) which has proxy configured.

### Issue 3: Wrong Port
**Solution:** 
- Backend should be on: http://localhost:8000
- Frontend should be on: http://localhost:3000
- Don't use the built version, use `npm run dev` for development

### Issue 4: API URL Mismatch
**Solution:** The frontend uses `/api` which should proxy to `http://localhost:8000/api` when using `npm run dev`.

## Quick Test

1. **Test Backend:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"invoice-parser"}`

2. **Test API:**
   ```bash
   curl http://localhost:8000/api/invoices
   ```
   Should return: `[]` (empty array if no invoices)

3. **Test Frontend:**
   - Open: http://localhost:3000
   - Check browser console (F12) for errors

## Alternative: Use Built Frontend

If dev mode doesn't work, you can build and serve via backend:

1. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Start backend:**
   ```bash
   python run.py
   ```

3. **Access at:**
   - http://localhost:8000 (serves the built frontend)

## Still Not Working?

1. Check firewall settings
2. Make sure no other application is using port 8000
3. Try restarting both servers
4. Check if Python dependencies are installed: `pip install -r requirements.txt`
