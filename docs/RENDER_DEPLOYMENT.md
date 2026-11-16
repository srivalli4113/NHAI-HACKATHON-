# Public Demo Deployment (Render)

Use this guide when a reviewer needs a public link for one or two days. It deploys
the React dashboard and FastAPI API as one service, so the public URL works without
Cloudflare Tunnel or the developer laptop running.

## Important Demo Limits

- Use only test faces and test employee details. A free demo host is not an
  approved location for real biometric records.
- The free Render filesystem is temporary. Accounts, registrations, photos, and
  attendance entries can disappear after a service restart or redeploy.
- A free Render service can sleep when unused. Open the link one or two minutes
  before the presentation so it has time to wake up.

## 1. Put the Project on GitHub

The local Git repository and its first commit are already prepared. The GitHub
repository for this project is `srivalli4113/NHAI-HACKATHON-`. Then run:

```bash
cd /Users/srivallikarnataka/Desktop/Hackathon_NHAI
git branch -M main
git remote set-url origin https://github.com/srivalli4113/NHAI-HACKATHON-.git
git push -u origin main
```

## 2. Create the Free Web Service

1. Sign in to Render with the same GitHub account.
2. Select **New +**, then **Web Service**, and choose `NHAI-HACKATHON-`.
3. Give it a unique name such as `nhai-edge-ai-demo-srivalli`.
4. Select the **Docker** runtime and the **Free** instance type.
5. Set **Dockerfile Path** to `docker/Dockerfile.render`.
6. Under **Advanced**, set **Health Check Path** to `/health`.
7. Add these environment variables before clicking **Create Web Service**:

| Key | Value |
| --- | --- |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | An easy demo password you choose privately; do not put it in GitHub |
| `APP_SECRET_KEY` | A new random secret, for example the output of `openssl rand -hex 32` |

The Docker image already sets its temporary database, storage, and model paths.
Do not add `VITE_API_BASE`; the website and API use the same public URL.

## 3. Share the Demo

When Render reports **Live**, copy its `https://...onrender.com` address. That is
the link to send to the reviewer. They can open the link and create an Employee or
Operator account from the sign-up screen.

For a presentation, open the link shortly before the meeting, sign in, and leave
the service page open. Do not redeploy or delete the Render service until the demo
period is over.
