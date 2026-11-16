# Railway Two-Day Demo Link

Use Railway when you need a public link that stays available for a short review
period without keeping the Mac online. This project has a root `Dockerfile`, so
Railway detects the full FastAPI and React application automatically.

## Before You Start

- The clean source branch is `render-demo` in `srivalli4113/NHAI-HACKATHON-`.
- Sign in at https://railway.app with GitHub and complete its account verification.
- Railway's trial currently includes a one-time $5 grant for up to 30 days. Watch
  the usage shown in its dashboard and remove the service after the evaluation.
- Use test faces and test employee details only. This is a public demonstration,
  not an approved environment for real biometric records.

## Deploy

1. Open Railway and select **New Project** then **Deploy from GitHub Repo**.
2. Choose `srivalli4113/NHAI-HACKATHON-`.
3. Open the new service, choose **Settings**, then set its deployment branch to
   `render-demo`.
4. In **Variables**, add these private values:

| Key | Value |
| --- | --- |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | An easy demo password you choose privately |
| `APP_SECRET_KEY` | The output of `openssl rand -hex 32` |

5. Trigger **Deploy**. Railway builds the root `Dockerfile` automatically.
6. When the deployment shows **Active**, open **Settings** then
   **Networking -> Public Networking -> Generate Domain**.
7. Copy the generated `https://...up.railway.app` address and send that address
   to the reviewer by email.

## During The Two-Day Review

- Do not delete the Railway service until the review finishes.
- Avoid redeploying while a reviewer is testing, because the local demo database
  and uploaded images use temporary storage.
- Open the public URL yourself before emailing it to confirm the sign-in screen
  loads. An Employee can create an account and register; an Operator has the full
  dashboard and attendance workflow.
