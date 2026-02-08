# Run GitHub UI Tests Against Your Local Machine (ngrok)

This lets **GitHub Actions** run the real UI test (the one that talks to ERPNext) by sending traffic to your computer through **ngrok**.

## 1. On your computer

### Install ngrok

- Download from [ngrok.com](https://ngrok.com) or `choco install ngrok` / `scoop install ngrok`.
- Sign up and get your auth token; then: `ngrok config add-authtoken YOUR_TOKEN`.

### Start your stack

1. **Backend:** `python run.py` (port 8000)
2. **Frontend:** `cd frontend && npm run dev` (port 3000)
3. **ERPNext** (e.g. port 8080)
4. **.env** with `ERPNEXT_BASE_URL`, `ERPNEXT_API_KEY`, `ERPNEXT_API_SECRET` set.

### Expose the app with ngrok

Expose the **frontend** (so the test opens your real app; the frontend will call your backend on localhost from your machine):

```bash
ngrok http 3000
```

You’ll see something like:

```
Forwarding   https://abc123def.ngrok-free.app -> http://localhost:3000
```

Copy that **https** URL (e.g. `https://abc123def.ngrok-free.app`). It changes each time you restart ngrok unless you use a fixed domain (paid).

---

## 2. In GitHub

### Add the secret

1. Repo → **Settings** → **Secrets and variables** → **Actions**.
2. **New repository secret**:
   - Name: `LIVE_TEST_BASE_URL`
   - Value: your ngrok URL **with no trailing slash**, e.g. `https://abc123def.ngrok-free.app`

Update this secret whenever you get a new ngrok URL (after restarting ngrok).

### Run the workflow

1. Go to the **Actions** tab.
2. Choose the workflow **"Live UI test (ngrok)"**.
3. Click **Run workflow** (and run it).
4. The job will:
   - Run on GitHub’s runner
   - Open a browser (headless) and go to `LIVE_TEST_BASE_URL`
   - Run the user journey test (upload → submit to ERPNext)
   - Your local backend and ERPNext handle the requests via ngrok.

---

## 3. Important notes

- **Keep ngrok and your stack running** for the whole time the workflow is running (a few minutes).
- **URL changes:** If you restart ngrok, the URL changes; update the `LIVE_TEST_BASE_URL` secret.
- **Paid ngrok:** A fixed domain avoids updating the secret every time.
- **Security:** Anyone with the ngrok URL can reach your app while ngrok is running. Use a temporary session and stop ngrok when you’re done.

---

## 4. If the workflow is skipped

The job runs only if the secret `LIVE_TEST_BASE_URL` is set. If you see “Skipped” or no job, add or fix that secret.
