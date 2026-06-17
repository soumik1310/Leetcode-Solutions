import os
import re
import requests
from datetime import datetime, timezone

# ── LeetCode session credentials from GitHub secrets ──────────────────────────
SESSION = os.environ["LEETCODE_SESSION"]
CSRF    = os.environ["LEETCODE_CSRF_TOKEN"]

HEADERS = {
    "Cookie": f"LEETCODE_SESSION={SESSION}; csrftoken={CSRF}",
    "x-csrftoken": CSRF,
    "Referer": "https://leetcode.com",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

# ── Priority order matters — more specific techniques beat generic topics ──────
# The script picks whichever folder appears EARLIEST in this list.
TOPIC_PRIORITY = [
    "sliding-window",       # → Sliding-Window   (beats Arrays/Strings)
    "two-pointers",         # → Two-Pointers      (beats Arrays/Strings)
    "binary-search",        # → Binary-Search
    "greedy",               # → Greedy
    "sorting",              # → Sorting
    "hash-table",           # → Hashing
    "string",               # → Strings
    "array",                # → Arrays            (last, most generic)
]

TOPIC_MAP = {
    "sliding-window": "Sliding-Window",
    "two-pointers":   "Two-Pointers",
    "binary-search":  "Binary-Search",
    "greedy":         "Greedy",
    "sorting":        "Sorting",
    "hash-table":     "Hashing",
    "string":         "Strings",
    "array":          "Arrays",
}

FALLBACK_FOLDER = "Misc"


def get_todays_submissions():
    """Fetch only today's accepted Java submissions (UTC day)."""
    url = "https://leetcode.com/api/submissions/?format=json&limit=50"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    data = r.json()

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts    = int(today_start.timestamp())

    return [
        s for s in data.get("submissions_dump", [])
        if s["status_display"] == "Accepted"
        and s["lang"] == "java"
        and int(s["timestamp"]) >= today_ts
    ]


def get_problem_info(title_slug):
    """Return topic tag slugs and difficulty for a given problem."""
    query = """
    query questionInfo($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        difficulty
        topicTags { slug }
      }
    }
    """
    r = requests.post(
        "https://leetcode.com/graphql",
        headers=HEADERS,
        json={"query": query, "variables": {"titleSlug": title_slug}},
    )
    r.raise_for_status()
    data       = r.json()["data"]["question"]
    tags       = [t["slug"] for t in data["topicTags"]]
    difficulty = data["difficulty"]  # "Easy" | "Medium" | "Hard"
    return tags, difficulty


def pick_folder(tags):
    """Pick the highest-priority matching folder for a problem's tags."""
    tag_set = set(tags)
    for topic in TOPIC_PRIORITY:
        if topic in tag_set:
            return TOPIC_MAP[topic]
    return FALLBACK_FOLDER


def title_to_filename(title):
    """Convert problem title to a safe Java filename."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    return clean.strip().replace(" ", "_") + ".java"


def main():
    print(f"Checking today's submissions ({datetime.now(timezone.utc).date()})…")
    submissions = get_todays_submissions()

    if not submissions:
        print("No new accepted Java submissions today.")
        return

    # de-duplicate: one entry per problem (latest submission wins)
    seen = {}
    for s in submissions:
        slug = s["title_slug"]
        if slug not in seen:
            seen[slug] = s

    synced = 0
    for slug, sub in seen.items():
        title    = sub["title"]
        code     = sub["code"]
        filename = title_to_filename(title)

        tags, difficulty = get_problem_info(slug)
        topic_folder     = pick_folder(tags)
        folder           = os.path.join(topic_folder, difficulty)  # e.g. Sliding-Window/Medium

        os.makedirs(folder, exist_ok=True)

        filepath = os.path.join(folder, filename)

        if os.path.exists(filepath):
            print(f"  skip  {folder}/{filename}  (already exists)")
            continue

        header = (
            f"// LeetCode – {title}\n"
            f"// URL: https://leetcode.com/problems/{slug}/\n"
            f"// Difficulty: {difficulty}\n"
            f"// Tags: {', '.join(tags)}\n\n"
        )
        with open(filepath, "w") as f:
            f.write(header + code)

        print(f"  wrote {folder}/{filename}")
        synced += 1

    print(f"\nDone. {synced} new solution(s) synced today.")


if __name__ == "__main__":
    main()