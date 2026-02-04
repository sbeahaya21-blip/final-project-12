# Quick Start Guide - View the Frontend

## Option 1: Simple HTML Frontend (No Node.js Required) ✅

The simple HTML frontend is already available! Just start the backend server:

### In Git Bash or Terminal:

```bash
# Make sure you're in the project root
cd "C:\Users\Admin\Desktop\אוטומציה\final project"

# Start the backend server
python run.py
```

Then open your browser and go to:
- **http://localhost:8000** - Simple HTML frontend
- **http://localhost:8000/docs** - API documentation

The simple HTML frontend has all the features:
- ✅ File upload
- ✅ Invoice parsing
- ✅ Anomaly detection
- ✅ Risk scoring
- ✅ Results display

---

## Option 2: React Frontend (Requires Node.js)

If you want the modern React frontend, you need to install Node.js first.

### Step 1: Install Node.js

1. Download Node.js from: **https://nodejs.org/**
2. Choose the **LTS (Long Term Support)** version
3. Run the installer and follow the instructions
4. **Restart your terminal/Git Bash** after installation

### Step 2: Verify Installation

```bash
node --version
npm --version
```

You should see version numbers (e.g., v18.x.x and 9.x.x)

### Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 4: Run Development Server

```bash
npm run dev
```

The React frontend will be available at: **http://localhost:3000**

### Or Build for Production

```bash
npm run build
```

Then restart the backend server - it will serve the built React app.

---

## Troubleshooting

### If Python server won't start:
```bash
# Install dependencies first
pip install -r requirements.txt

# Then start server
python run.py
```

### If npm command not found:
- Make sure Node.js is installed
- Restart your terminal after installing Node.js
- Check if Node.js is in your PATH

### Quick Test:
```bash
# Test backend
curl http://localhost:8000/health

# Should return: {"status":"healthy","service":"invoice-parser"}
```
