# data-broker-opt-out-bot

An autonomous Telegram bot that submits and tracks opt-out requests to major Brazilian and US data brokers, using a combination of public APIs and headless-browser scraping backed by recorded HTML fixtures. It turns a tedious, multi-week manual process into an automated, privacy-first workflow.

---

## ⚡ 5-Minute Self-Hosted Deployment Guide

This repository includes a production-ready **Docker Compose** self-hosting stack with:
- **Bot Application** (Telegram bot runner & webhook server)
- **PostgreSQL 16** (Persistent data storage)
- **Redis 7** (Distributed locks and queue management)
- **Caddy 2** (Reverse proxy with automatic Let's Encrypt TLS certificates)
- **Watchtower** (Automated container image updates)

### Prerequisites
- A VPS running Linux (Ubuntu 22.04 LTS recommended) with root/sudo access.
- [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose v2](https://docs.docker.com/compose/install/) installed.
- A domain name pointing to your VPS IP address (A / AAAA records) for automatic SSL/TLS via Caddy.
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather).

---

### Step-by-Step Deployment

#### 1. Clone the Repository
```bash
git clone https://github.com/juninmd/data-broker-opt-out-bot.git
cd data-broker-opt-out-bot
```

#### 2. Configure Environment Variables
Copy the example environment file and edit it to set your secrets:
```bash
cp .env.example .env
nano .env
```
Ensure you update the following fields in `.env`:
- `DOMAIN_NAME`: Your domain (e.g. `optout.example.com` or `localhost` for testing).
- `ACME_EMAIL`: Your email address for TLS certificate registration.
- `TELEGRAM_BOT_TOKEN`: The bot token provided by `@BotFather`.
- `POSTGRES_PASSWORD`: A strong random password for PostgreSQL.
- `REDIS_PASSWORD`: A strong random password for Redis locks.

#### 3. Start the Application Stack
Launch all services in detached mode:
```bash
docker compose up -d
```

#### 4. Verify Stack Status
Check that all containers are healthy and running:
```bash
docker compose ps
```

You can test the health endpoint via `curl` or browser:
```bash
curl -f https://yourdomain.com/health
# Expected response: {"status":"ok","service":"data-broker-opt-out-bot"}
```

#### 5. Useful Management Commands
- **View logs in real-time:**
  ```bash
  docker compose logs -f
  ```
- **Restart services:**
  ```bash
  docker compose restart
  ```
- **Stop the stack:**
  ```bash
  docker compose down
  ```

---

## 🛠️ Architecture Overview

```
                          +-------------------+
                          |     Internet      |
                          +---------+---------+
                                    |
                                HTTP/HTTPS (80, 443)
                                    v
                          +-------------------+
                          |      Caddy 2      | (TLS Termination & Reverse Proxy)
                          +---------+---------+
                                    |
                                    v
                          +-------------------+
                          |    Bot Service    | (Python / Telegram Engine)
                          +----+--------+-----+
                               |        |
             +-----------------+        +-----------------+
             v                                            v
  +--------------------+                        +--------------------+
  |   PostgreSQL 16    |                        |      Redis 7       |
  | (Persistent Data)  |                        | (Distributed Lock) |
  +--------------------+                        +--------------------+

  +------------------------------------------------------------------+
  |                   Watchtower (Auto-Updates)                      |
  +------------------------------------------------------------------+
```

---

## 🔐 Security & Operations

- **Non-Root Execution:** All services run under standard container privilege bounds.
- **TLS by Default:** Caddy automatically provisions and renews SSL/TLS certificates via Let's Encrypt.
- **Isolated Networks:** Containers communicate over an internal bridge network (`app-network`); only Caddy exposes public ports `80` and `443`.
