#!/usr/bin/env python3
"""Add a new episode to the LOTM podcast RSS feed."""

import os
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import quote

# rss.xml lives in the same directory as this script
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
RSS_FILE = os.path.join(REPO_DIR, "rss.xml")
MARKER   = "    <!-- ===== EPISODES - ADD NEW ONES AT THE TOP ===== -->"


def main():
    print("=== Add New LOTM Episode ===\n")

    ep_num     = input("Episode number: ").strip()
    chapters   = input("Chapter range (e.g. 890-930): ").strip()
    default_id = f"LOTM-EP{ep_num}"
    identifier = input(f"Archive.org item identifier [{default_id}]: ").strip() or default_id
    mp3_file   = input("MP3 filename (e.g. episode.mp3): ").strip()
    duration   = input("Duration (HH:MM:SS): ").strip()
    size       = input("File size in bytes (press Enter to skip): ").strip() or "0"

    # URL-encode the filename so spaces / special chars are safe in XML
    mp3_url  = f"https://archive.org/download/{identifier}/{quote(mp3_file)}"

    pub_date    = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    title       = f"EP {ep_num} - Lord of the Mysteries Chapter {chapters}"
    description = (f"EP {ep_num} LOTM - Lord of the Mysteries Chapter {chapters} "
                   "\u2013 The Ultimate Audiobook Experience")
    guid        = f"LOTM-EP{ep_num}"

    new_item = f"""
    <item>
      <title>{title}</title>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="false">{guid}</guid>

      <enclosure
        url="{mp3_url}"
        length="{size}"
        type="audio/mpeg"/>

      <itunes:duration>{duration}</itunes:duration>
      <itunes:episode>{ep_num}</itunes:episode>
      <itunes:explicit>false</itunes:explicit>
    </item>"""

    with open(RSS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER not in content:
        print(f"Error: marker not found in {RSS_FILE}")
        print(f"Expected: {MARKER!r}")
        sys.exit(1)

    updated = content.replace(MARKER, MARKER + new_item, 1)

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"\n✓ Added EP {ep_num} to rss.xml")
    print(f"  URL: {mp3_url}")

    push = input("\nPush to GitHub now? (y/n): ").strip().lower()
    if push == "y":
        subprocess.run(["git", "-C", REPO_DIR, "add", "rss.xml"], check=True)
        subprocess.run(
            ["git", "-C", REPO_DIR, "commit", "-m", f"Add EP {ep_num} - Chapter {chapters}"],
            check=True,
        )
        subprocess.run(["git", "-C", REPO_DIR, "pull", "--rebase"], check=True)
        subprocess.run(["git", "-C", REPO_DIR, "push"], check=True)
        print("✓ Pushed to GitHub — feed will update in ~1 minute")


if __name__ == "__main__":
    main()
