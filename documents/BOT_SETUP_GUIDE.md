# 🤖 CodeSlim GitHub Auto-Fix Bot — Setup & Deployment Guide

This guide walks you through setting up and running the autonomous **CodeSlim GitHub PR Bot** for your repositories.

---

## 🛠️ Step-by-Step Setup Instructions

### 🔑 Step 1: Create a GitHub Token (PAT)
1. Log in to GitHub and navigate to:
   👉 **Settings** $\rightarrow$ **Developer settings** $\rightarrow$ **Personal access tokens** $\rightarrow$ **Tokens (classic)** (or Fine-grained tokens).
2. Click **Generate new token**.
3. Set token permissions:
   - `repo` (Full control of repositories, write access to PR comments & code commits).
4. Copy the generated token string (e.g., `ghp_abcdef1234567890...`).

---

### 🔒 Step 2: Set Environment Variables

#### **On Windows (PowerShell):**
```powershell
$env:CODESLIM_GITHUB_TOKEN="ghp_your_real_token_here"
$env:CODESLIM_GITHUB_WEBHOOK_SECRET="your_custom_secret_key"
```

#### **On Linux / macOS (Bash / Zsh):**
```bash
export CODESLIM_GITHUB_TOKEN="ghp_your_real_token_here"
export CODESLIM_GITHUB_WEBHOOK_SECRET="your_custom_secret_key"
```

#### **Or via `.env` file (Root Directory):**
Create a `.env` file in the root folder of CodeSlim:
```env
CODESLIM_GITHUB_TOKEN=ghp_your_real_token_here
CODESLIM_GITHUB_WEBHOOK_SECRET=your_custom_secret_key
```

---

### 🌐 Step 3: Configure GitHub Repository Webhook
1. Go to your target GitHub repository $\rightarrow$ **Settings** $\rightarrow$ **Webhooks** $\rightarrow$ Click **Add webhook**.
2. Fill in the form:
   - **Payload URL**: `http://<your-server-ip-or-ngrok-domain>:8000/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: `<your_custom_secret_key>` (must match `CODESLIM_GITHUB_WEBHOOK_SECRET`)
   - **SSL verification**: Enable (if using HTTPS domain)
3. Select **Let me select individual events** $\rightarrow$ Check **Pull requests**.
4. Click **Add webhook**.

> 💡 **Local Testing Tip**: If running locally on your computer, use **ngrok** to expose port 8000:
> ```bash
> ngrok http 8000
> ```
> Use the generated `https://xxxx.ngrok-free.app/webhook/github` URL as your Webhook Payload URL!

---

### 🚀 Step 4: Start the CodeSlim Bot Server

To start the bot server with interactive log updates:

```powershell
python -m codeslim.cli bot serve --host 0.0.0.0 --port 8000 --auto-commit
```

#### **CLI Options:**
- `--host`: Server IP to bind (default `0.0.0.0`).
- `--port`: HTTP port (default `8000`).
- `--auto-commit`: (Optional) Automatically pushes Tier-1 dead code removal commits back to the PR branch.

---

## 🧪 Testing the Webhook Bot

1. Open a new Pull Request in your repository containing modified `.py` files.
2. CodeSlim Bot will automatically:
   - Receive the webhook in `< 100ms`.
   - Validate HMAC signature.
   - Run cyclomatic complexity & dead code static analysis.
   - Post an interactive **Markdown Audit Report** directly inside the PR thread!
   - (If `--auto-commit` enabled) Push a clean auto-fix commit removing dead imports.
