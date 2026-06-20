# VibeGraph Demo Repository

This intentionally small FastAPI + React project demonstrates the complete
VibeGraph workflow around an authentication change.

## Install and test

```bash
uv sync --project demo/backend
pnpm install
pnpm demo:check
```

## Run the sample application

Backend:

```bash
uv run --project demo/backend uvicorn --app-dir demo/backend app.main:app --reload --port 9100
```

Frontend:

```bash
pnpm --filter @vibegraph/demo-frontend dev
```

Use `builder@vibegraph.dev` and `ship-fast`.

## Five-minute VibeGraph scenario

1. Run VibeGraph against the demo:

   ```bash
   node cli/dist/index.js demo --port 8732 --no-open
   ```

2. Search for `auth_routes.py` and inspect its neighborhood.
3. Break the imported symbol:

   ```bash
   pnpm demo:break
   ```

4. Observe the missing-symbol warning for `validate_session`.
5. Generate context for:

   ```text
   Fix login error handling in auth_routes.py
   ```

6. Confirm the context includes:

   ```text
   backend/app/routes/auth_routes.py
   backend/app/services/session_service.py
   backend/app/models/errors.py
   backend/tests/test_auth_flow.py
   ```

7. Generate the README draft.
8. Restore the demo:

   ```bash
   pnpm demo:restore
   ```
