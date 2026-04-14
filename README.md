# AniList Discord Bot — Setup Guide

This bot watches your friends' AniList accounts and posts their anime
watch activity straight into your Discord server.

---

## Step 1 — Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** → give it a name (e.g. "AniList Tracker")
3. Click **Bot** in the left sidebar → click **Add Bot** → confirm
4. Under the **Token** section, click **Reset Token** then **Copy**
   - SAVE THIS — you'll need it later as DISCORD_TOKEN
5. Scroll down to **Privileged Gateway Intents** — no extras needed, leave them off
6. Click **OAuth2 → URL Generator** in the sidebar
7. Check the **bot** scope, then check **Send Messages** and **Embed Links** permissions
8. Copy the generated URL at the bottom → open it in your browser → invite the bot to your server

---

## Step 2 — Get Your Discord Channel ID

1. In Discord, go to **Settings → Advanced** and turn on **Developer Mode**
2. Right-click the channel you want posts in → **Copy Channel ID**
   - SAVE THIS — you'll need it as CHANNEL_ID

---

## Step 3 — Find Your Friends' AniList Usernames

Just check their AniList profile URLs:
  https://anilist.co/user/USERNAME/

Collect all usernames you want to track (e.g. alex,sarah,mike).

---

## Step 4 — Deploy to Railway

Railway is a free cloud host that will keep your bot running 24/7.

1. Create a free account at https://railway.app (sign in with GitHub)
2. Create a free GitHub account at https://github.com if you don't have one
3. In GitHub, create a new repository called "anilist-bot" (click + → New repository)
4. Upload all three bot files to the repo:
   - bot.py
   - requirements.txt
   - Procfile
   (Use the "Add file → Upload files" button on GitHub)

5. In Railway, click **New Project → Deploy from GitHub repo**
6. Select your "anilist-bot" repository
7. Once it appears, click your project → go to the **Variables** tab
8. Add these environment variables one by one:

   | Variable        | Value                                      |
   |-----------------|-------------------------------------------|
   | DISCORD_TOKEN   | (the token from Step 1)                   |
   | CHANNEL_ID      | (the channel ID from Step 2)              |
   | ANILIST_USERS   | alex,sarah,mike  ← your friends' usernames|
   | CHECK_INTERVAL  | 600  ← checks every 10 minutes            |

9. Railway will automatically redeploy. Click **Deployments** to see logs.
   You should see: "Logged in as YourBot#1234 — watching [...]"

---

## Troubleshooting

- **Bot is online but not posting** — make sure it was invited with "Send Messages"
  and "Embed Links" permissions, and that CHANNEL_ID is correct.
- **"Could not find channel" error** — double-check the CHANNEL_ID value.
- **No activity showing up** — AniList accounts must be public. Have your friends
  check Settings → Account → List Activity is set to public.
- **Want to add more friends later?** — just edit ANILIST_USERS in Railway's
  Variables tab and redeploy.

---

## What the Bot Posts

Every time a friend marks an episode as watched on AniList, the bot posts
an embed like:

  ┌─────────────────────────────────────────┐
  │ 👤 alex watched some anime              │
  │                                         │
  │ Frieren: Beyond Journey's End           │
  │ 📺 Episode 5 of 28                      │
  └─────────────────────────────────────────┘

Completed shows get a ✅ green embed instead.
