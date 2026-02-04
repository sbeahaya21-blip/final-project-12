# Viewing API test coverage on Codecov

## 1. Connect your repo to Codecov

1. Go to [codecov.io](https://codecov.io) and sign in with **GitHub**.
2. Click **Add new repository** and select this repository.
3. (Optional) For **private** repos, copy the **Repository Token** from the repo’s Codecov page, then in GitHub:
   - Repo → **Settings** → **Secrets and variables** → **Actions**
   - Add a secret named `CODECOV_TOKEN` with that token.

## 2. Run CI

On every push or PR to `main` or `develop`, the workflow:

- Runs API tests: `pytest tests/api/`
- Generates coverage for the `app/` package
- Uploads `coverage.xml` to Codecov

## 3. Where to see coverage

- **Codecov dashboard**: [codecov.io/gh/YOUR_USERNAME/YOUR_REPO](https://codecov.io) → choose your repo.
- **PR comments**: Codecov posts a comment on pull requests with coverage diff and links.
- **Badge**: On the repo’s Codecov page you can copy a markdown badge to add to your README.

## 4. Local coverage (no Codecov)

```bash
pip install -r requirements.txt
pytest tests/api/ --cov=app --cov-report=html --cov-report=term-missing
```

Open `htmlcov/index.html` in a browser to see the same style of report locally.
