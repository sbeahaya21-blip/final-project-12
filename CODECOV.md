# Viewing API test coverage on Codecov

## Quick: see coverage for this repo

1. **Connect the repo to Codecov (one-time)**  
   - Open: **https://codecov.io**  
   - Sign in with **GitHub**  
   - Click **“Add new repository”**  
   - Select **`sbeahaya21-blip/final-project-12`** and add it  

2. **Open the coverage dashboard**  
   - **https://codecov.io/gh/sbeahaya21-blip/final-project-12**  
   - After the next CI run, you’ll see the coverage report, graphs, and file list here.

3. **Trigger a new report**  
   - Push a commit to `main` (or open a PR).  
   - When the “CI Pipeline” workflow finishes, coverage is uploaded to Codecov and the dashboard updates.

**If the repo is private:**  
- On the repo’s Codecov page, copy the **Repository Token**.  
- In GitHub: **Settings → Secrets and variables → Actions** → New secret: name `CODECOV_TOKEN`, value = that token.  
- Push again so CI re-runs and uploads coverage.

---

## 1. Connect your repo to Codecov

1. Go to [codecov.io](https://codecov.io) and sign in with **GitHub**.
2. Click **Add new repository** and select **final-project-12**.
3. (Optional) For **private** repos, copy the **Repository Token** from the repo’s Codecov page, then in GitHub:
   - Repo → **Settings** → **Secrets and variables** → **Actions**
   - Add a secret named `CODECOV_TOKEN` with that token.

## 2. Run CI

On every push or PR to `main` or `develop`, the workflow:

- Runs API tests: `pytest tests/api/`
- Generates coverage for the `app/` package
- Uploads `coverage.xml` to Codecov

## 3. Where to see coverage

- **This repo’s dashboard:** [codecov.io/gh/sbeahaya21-blip/final-project-12](https://codecov.io/gh/sbeahaya21-blip/final-project-12)
- **PR comments:** Codecov posts a comment on pull requests with coverage diff and links.
- **Badge:** On the repo’s Codecov page you can copy a markdown badge to add to your README.

## 4. Local coverage (no Codecov)

```bash
pip install -r requirements.txt
pytest tests/api/ --cov=app --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` in a browser to see the same style of report locally.
