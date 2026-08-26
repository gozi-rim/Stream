#!/usr/bin/env python3
"""
FAST M3U Playlist and EPG Generator (All-Region Edition)
=========================================================
Automates fetching, standardizing, and generating global FAST
(Free Ad-supported Streaming TV) and IPTV playlists with auto-injected EPG:
- Roku All Regions
- Pluto TV All Regions
- Samsung TV Plus All Regions
- Plex TV All Regions
- Tubi TV All Regions
- MJH Global All Channels
- MJH World Channels
- DStv South Africa / Africa (with custom channels support)
- Master All-Region Combined Playlist
"""

import os
import re
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FASTGenerator")

# Output directory for generated playlists
PLAYLISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "playlists")
CUSTOM_CHANNELS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_channels.json")

# All-Region Sources Configuration
SOURCES_CONFIG = [
    {
        "id": "roku_all",
        "name": "Roku TV (All Regions)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/roku_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/Roku/all.xml.gz",
        "output_filename": "roku_all.m3u8",
        "default_group": "Roku TV"
    },
    {
        "id": "plutotv_all",
        "name": "Pluto TV (All Regions)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plutotv_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/PlutoTV/all.xml.gz",
        "output_filename": "plutotv_all.m3u8",
        "default_group": "Pluto TV"
    },
    {
        "id": "samsung_all",
        "name": "Samsung TV Plus (All Regions)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_all.m3u",
        "fallback_urls": [
            "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_us.m3u"
        ],
        "epg_url": "https://i.mjh.nz/SamsungTVPlus/all.xml.gz",
        "output_filename": "samsung_all.m3u8",
        "default_group": "Samsung TV Plus"
    },
    {
        "id": "plex_all",
        "name": "Plex TV (All Regions)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plex_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/Plex/all.xml.gz",
        "output_filename": "plex_all.m3u8",
        "default_group": "Plex TV"
    },
    {
        "id": "tubi_all",
        "name": "Tubi TV (All Regions)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_epg.xml",
        "output_filename": "tubi_all.m3u8",
        "default_group": "Tubi TV"
    },
    {
        "id": "mjh_all",
        "name": "Global / All Channels (MJH)",
        "url": "https://i.mjh.nz/all/raw-tv.m3u8",
        "fallback_urls": [
            "https://i.mjh.nz/all/kodi-tv.m3u8"
        ],
        "epg_url": "https://i.mjh.nz/all/epg.xml.gz",
        "output_filename": "mjh_all.m3u8",
        "default_group": "Global FAST"
    },
    {
        "id": "world",
        "name": "World Channels (MJH)",
        "url": "https://i.mjh.nz/world/raw-tv.m3u8",
        "fallback_urls": [
            "https://i.mjh.nz/world/kodi-tv.m3u8"
        ],
        "epg_url": "https://i.mjh.nz/world/epg.xml.gz",
        "output_filename": "world.m3u8",
        "default_group": "World TV"
    },
    {
        "id": "dstv",
        "name": "DStv South Africa / Africa",
        "url": "https://i.mjh.nz/DStv/raw-tv.m3u8",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/DStv/za.xml.gz",
        "output_filename": "dstv.m3u8",
        "default_group": "DStv"
    }
]


def create_session() -> requests.Session:
    """Create a resilient requests session with fast retry handling."""
    session = requests.Session()
    retries = Retry(
        total=2,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close"
    })
    return session


def load_custom_channels() -> Dict[str, List[dict]]:
    """Load custom channels from custom_channels.json if present."""
    if not os.path.exists(CUSTOM_CHANNELS_FILE):
        return {}
    try:
        with open(CUSTOM_CHANNELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info("Loaded custom channels from %s", CUSTOM_CHANNELS_FILE)
            return data
    except Exception as e:
        logger.warning("Could not read custom_channels.json: %s", e)
        return {}


def format_custom_channel(item: dict, default_group: str) -> str:
    """Format a custom channel dictionary into M3U8 string entry."""
    name = item.get("name", "Custom Channel")
    tvg_id = item.get("tvg_id", "")
    tvg_name = item.get("tvg_name", name)
    tvg_logo = item.get("tvg_logo", "")
    tvg_chno = item.get("tvg_chno", "")
    group = item.get("group", default_group)
    url = item.get("url", "")
    http_user_agent = item.get("http_user_agent", "")
    http_referrer = item.get("http_referrer", "")

    attrs = []
    if tvg_id:
        attrs.append(f'tvg-id="{tvg_id}"')
    if tvg_name:
        attrs.append(f'tvg-name="{tvg_name}"')
    if tvg_logo:
        attrs.append(f'tvg-logo="{tvg_logo}"')
    if tvg_chno:
        attrs.append(f'tvg-chno="{tvg_chno}"')
    if group:
        attrs.append(f'group-title="{group}"')

    attr_str = " ".join(attrs)
    lines = [f"#EXTINF:-1 {attr_str},{name}".strip()]
    if http_user_agent:
        lines.append(f"#EXTVLCOPT:http-user-agent={http_user_agent}")
    if http_referrer:
        lines.append(f"#EXTVLCOPT:http-referrer={http_referrer}")
    lines.append(url)
    return "\n".join(lines)


def fetch_upstream_content(session: requests.Session, source: dict) -> Tuple[Optional[str], str]:
    """
    Fetch M3U playlist from primary URL or fallback URLs.
    Returns (content, used_url).
    """
    urls_to_try = [source["url"]] + source.get("fallback_urls", [])
    
    for url in urls_to_try:
        try:
            logger.info("Fetching '%s' from %s...", source["name"], url)
            response = session.get(url, timeout=12)
            if response.status_code == 200 and response.text.strip():
                logger.info("Successfully fetched %d bytes from %s", len(response.text), url)
                return response.text, url
            elif response.status_code == 404:
                logger.warning("Source '%s' returned 404 at %s", source["name"], url)
            else:
                logger.warning("Received status %d from %s", response.status_code, url)
        except Exception as e:
            logger.warning("Notice fetching %s: %s", url, e)

    return None, ""


def standardize_playlist(
    raw_content: Optional[str],
    epg_url: str,
    custom_entries: List[dict],
    default_group: str
) -> Tuple[str, int]:
    """
    Standardize the M3U8 content:
    - Auto-injects `#EXTM3U url-tvg="<epg_url>" x-tvg-url="<epg_url>"` header
    - Parses and cleans up stream entries
    - Appends any custom/fallback channel entries
    - Returns (standardized_m3u8_string, total_channel_count)
    """
    header = f'#EXTM3U url-tvg="{epg_url}" x-tvg-url="{epg_url}"'
    parsed_channels = []
    
    if raw_content:
        lines = [line.strip() for line in raw_content.splitlines() if line.strip()]
        
        current_entry_lines = []
        for line in lines:
            if line.startswith("#EXTM3U"):
                continue  # Skip raw header; standardized header injected
            
            if line.startswith("#EXTINF"):
                if current_entry_lines:
                    if any(not l.startswith("#") for l in current_entry_lines):
                        parsed_channels.append("\n".join(current_entry_lines))
                    current_entry_lines = []
                current_entry_lines.append(line)
            elif current_entry_lines:
                current_entry_lines.append(line)
        
        if current_entry_lines and any(not l.startswith("#") for l in current_entry_lines):
            parsed_channels.append("\n".join(current_entry_lines))

    # Append custom channels
    for custom_item in custom_entries:
        custom_block = format_custom_channel(custom_item, default_group)
        if custom_block.strip():
            parsed_channels.append(custom_block)

    # Assemble complete playlist
    output_lines = [header, ""]
    for ch in parsed_channels:
        output_lines.append(ch)
        output_lines.append("")
        
    return "\n".join(output_lines).strip() + "\n", len(parsed_channels)


def generate_all():
    """Main execution function to process all playlists and generate master outputs."""
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)
    session = create_session()
    custom_channels = load_custom_channels()
    
    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "edition": "All-Region Global FAST",
        "playlists": []
    }
    
    all_combined_channels = []
    all_epg_urls = []

    print("\n" + "=" * 75)
    print("  ALL-REGION GLOBAL FAST M3U PLAYLIST & EPG GENERATOR")
    print("=" * 75)

    for source in SOURCES_CONFIG:
        source_id = source["id"]
        source_name = source["name"]
        epg_url = source["epg_url"]
        output_filename = source["output_filename"]
        output_path = os.path.join(PLAYLISTS_DIR, output_filename)
        default_group = source.get("default_group", source_name)
        source_customs = custom_channels.get(source_id, [])

        if epg_url not in all_epg_urls:
            all_epg_urls.append(epg_url)

        logger.info("Processing source: %s (%s)", source_name, source_id)
        
        raw_content, used_url = fetch_upstream_content(session, source)
        
        final_content, channel_count = standardize_playlist(
            raw_content=raw_content,
            epg_url=epg_url,
            custom_entries=source_customs,
            default_group=default_group
        )
        
        # Write individual playlist files (.m3u8 and .m3u)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        m3u_output_path = os.path.splitext(output_path)[0] + ".m3u"
        with open(m3u_output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        file_size_kb = os.path.getsize(output_path) / 1024
        logger.info("Wrote %s (and .m3u): %d channels (%.2f KB)", output_filename, channel_count, file_size_kb)

        # Extract channel blocks for combined playlist (excluding header)
        channel_blocks = [block.strip() for block in final_content.split("\n\n") if block.strip() and not block.startswith("#EXTM3U")]
        all_combined_channels.extend(channel_blocks)

        manifest["playlists"].append({
            "id": source_id,
            "name": source_name,
            "file": output_filename,
            "file_m3u": os.path.splitext(output_filename)[0] + ".m3u",
            "channels_count": channel_count,
            "epg_url": epg_url,
            "upstream_url": used_url if used_url else source["url"],
            "status": "active" if channel_count > 0 else "empty"
        })

    # Process global custom sources if any
    global_customs = custom_channels.get("custom", [])
    if global_customs:
        logger.info("Processing global custom channels: %d entries", len(global_customs))
        custom_blocks = [format_custom_channel(item, "Custom") for item in global_customs]
        all_combined_channels.extend([b for b in custom_blocks if b.strip()])

    # Generate Combined / Master Playlist (.m3u8 and .m3u)
    combined_epg_str = ",".join(all_epg_urls)
    combined_header = f'#EXTM3U url-tvg="{combined_epg_str}" x-tvg-url="{combined_epg_str}"'
    combined_output_lines = [combined_header, ""]
    for block in all_combined_channels:
        combined_output_lines.append(block)
        combined_output_lines.append("")
        
    combined_file_path = os.path.join(PLAYLISTS_DIR, "all_combined.m3u8")
    with open(combined_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_output_lines).strip() + "\n")
        
    combined_m3u_path = os.path.join(PLAYLISTS_DIR, "all_combined.m3u")
    with open(combined_m3u_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_output_lines).strip() + "\n")
        
    combined_size_kb = os.path.getsize(combined_file_path) / 1024
    logger.info("Wrote Master All-Region Playlist 'all_combined.m3u8' / 'all_combined.m3u': %d total channels (%.2f KB)", len(all_combined_channels), combined_size_kb)

    manifest["master_playlist"] = {
        "file": "all_combined.m3u8",
        "file_m3u": "all_combined.m3u",
        "total_channels": len(all_combined_channels),
        "epg_urls": all_epg_urls
    }

    # Write manifest index.json
    manifest_path = os.path.join(PLAYLISTS_DIR, "index.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Print Summary Table
    print("\n" + "=" * 75)
    print("  ALL-REGION GENERATION SUMMARY")
    print("=" * 75)
    print(f"  {'Network / Playlist Name':<34} | {'Filename':<20} | {'Channels':<8}")
    print("  " + "-" * 71)
    for p in manifest["playlists"]:
        print(f"  {p['name']:<34} | {p['file_m3u']:<20} | {p['channels_count']:<8}")
    print("  " + "-" * 71)
    print(f"  {'* MASTER COMBINED (ALL REGIONS) *':<34} | {'all_combined.m3u':<20} | {len(all_combined_channels):<8}")
    print("=" * 75)
    print(f"Playlists successfully generated in: {PLAYLISTS_DIR}\n")


if __name__ == "__main__":
    generate_all()
