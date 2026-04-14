import discord
import asyncio
import aiohttp
import json
import os
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────
DISCORD_TOKEN   = os.environ["DISCORD_TOKEN"]
CHANNEL_ID      = int(os.environ["CHANNEL_ID"])
ANILIST_USERS   = os.environ["ANILIST_USERS"].split(",")   # comma-separated usernames
CHECK_INTERVAL  = int(os.environ.get("CHECK_INTERVAL", "600"))  # seconds (default 10 min)

SEEN_FILE = "seen_activities.json"

# ── AniList GraphQL query ─────────────────────────────────────────────────────
ACTIVITY_QUERY = """
query ($username: String) {
  Page(perPage: 10) {
    activities(userName: $username, type: ANIME_LIST, sort: ID_DESC) {
      ... on ListActivity {
        id
        status
        progress
        createdAt
        media {
          title { romaji english }
          siteUrl
          coverImage { medium }
          episodes
        }
        user { name siteUrl }
      }
    }
  }
}
"""

# ── Persistent seen-activity store ───────────────────────────────────────────
def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# ── Fetch activity for one user ───────────────────────────────────────────────
async def fetch_activity(session: aiohttp.ClientSession, username: str) -> list:
    async with session.post(
        "https://graphql.anilist.co",
        json={"query": ACTIVITY_QUERY, "variables": {"username": username}},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    ) as resp:
        if resp.status != 200:
            print(f"[AniList] HTTP {resp.status} for {username}")
            return []
        data = await resp.json()
        return data.get("data", {}).get("Page", {}).get("activities", [])

# ── Build a Discord embed for one activity ────────────────────────────────────
def build_embed(activity: dict) -> discord.Embed:
    user   = activity["user"]
    media  = activity["media"]
    title  = media["title"]["english"] or media["title"]["romaji"]
    status = activity["status"].capitalize()   # e.g. "Watched"
    prog   = activity.get("progress")          # episode number or None
    eps    = media.get("episodes")

    # Progress line: "Ep 5 of 24" / "Ep 12" / "Completed"
    if status == "Completed":
        progress_str = "✅ Completed"
        color = discord.Color.green()
    elif prog:
        ep_of = f" of {eps}" if eps else ""
        progress_str = f"📺 Episode {prog}{ep_of}"
        color = discord.Color.blurple()
    else:
        progress_str = status
        color = discord.Color.light_grey()

    embed = discord.Embed(
        title=title,
        url=media["siteUrl"],
        color=color,
        timestamp=datetime.utcfromtimestamp(activity["createdAt"]),
    )
    embed.set_author(
        name=f"{user['name']} {status.lower()} some anime",
        url=user["siteUrl"],
        icon_url=f"https://img.anili.st/user/{user['name']}",
    )
    embed.add_field(name="Progress", value=progress_str, inline=True)
    cover = media.get("coverImage", {}).get("medium")
    if cover:
        embed.set_thumbnail(url=cover)
    embed.set_footer(text="via AniList")
    return embed

# ── Discord client ────────────────────────────────────────────────────────────
intents = discord.Intents.default()
client  = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} — watching {ANILIST_USERS}")
    client.loop.create_task(poll_loop())

async def poll_loop():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("ERROR: Could not find channel. Check CHANNEL_ID.")
        return

    seen = load_seen()

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            new_seen = set()
            to_post  = []

            for username in ANILIST_USERS:
                username = username.strip()
                try:
                    activities = await fetch_activity(session, username)
                except Exception as e:
                    print(f"[Error] Fetching {username}: {e}")
                    continue

                for act in activities:
                    aid = str(act["id"])
                    new_seen.add(aid)
                    if aid not in seen:
                        to_post.append(act)

            # Post oldest first
            for act in sorted(to_post, key=lambda a: a["createdAt"]):
                try:
                    embed = build_embed(act)
                    await channel.send(embed=embed)
                    await asyncio.sleep(1)   # small delay between posts
                except Exception as e:
                    print(f"[Error] Posting activity {act.get('id')}: {e}")

            seen = seen | new_seen
            save_seen(seen)
            await asyncio.sleep(CHECK_INTERVAL)

client.run(DISCORD_TOKEN)
