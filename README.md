# FAST M3U Playlist & EPG Generator

Automated FAST (Free Ad-supported Streaming TV) and regional IPTV M3U8 playlist generator with standardized EPG (Electronic Program Guide) auto-injection for New Zealand, Australia, Samsung TV Plus NZ, Plex AU, DStv South Africa, and custom sources.

---

## 📺 Generated Playlists & EPG Mappings

When hosted on GitHub, you can load raw playlist URLs directly into your IPTV client:

| Playlist Name | Generated M3U8 File | Primary EPG XML Source |
| :--- | :--- | :--- |
| **Combined Master Playlist** | [`playlists/all_combined.m3u8`](playlists/all_combined.m3u8) | Unified Multi-EPG XML.gz |
| **NZ / AU Combined** | [`playlists/nzau.m3u8`](playlists/nzau.m3u8) | `https://i.mjh.nz/nzau/epg.xml.gz` |
| **AU All Channels** | [`playlists/au_all.m3u8`](playlists/au_all.m3u8) | `https://i.mjh.nz/au/all/epg.xml.gz` |
| **NZ All Channels** | [`playlists/nz_all.m3u8`](playlists/nz_all.m3u8) | `https://i.mjh.nz/nz/epg.xml.gz` |
| **Samsung TV Plus NZ** | [`playlists/samsung_nz.m3u8`](playlists/samsung_nz.m3u8) | `https://i.mjh.nz/SamsungTVPlus/nz.xml.gz` |
| **Plex TV AU** | [`playlists/plex_au.m3u8`](playlists/plex_au.m3u8) | `https://i.mjh.nz/Plex/au.xml.gz` |
| **DStv South Africa** | [`playlists/dstv.m3u8`](playlists/dstv.m3u8) | `https://i.mjh.nz/DStv/za.xml.gz` |

> Every generated `.m3u8` file automatically includes standardized `#EXTM3U url-tvg="..." x-tvg-url="..."` tags, allowing supported players (TiviMate, Kodi, Jellyfin, OTT Navigator, etc.) to automatically link the EPG without manual setup.

---

## 🚀 GitHub Actions Automation

The repository includes an automated workflow [`.github/workflows/update_playlists.yml`](.github/workflows/update_playlists.yml):
- **Schedule**: Runs automatically every day at `03:00 UTC` (`0 3 * * *`).
- **Manual Trigger**: Can be run on-demand using GitHub's `workflow_dispatch`.
- **Auto Commit**: Fetches fresh upstream streams and pushes updated `.m3u8` files with `[skip ci]`.

---

## 🛠️ Adding Custom Streams

You can add custom channels or fallback streams directly in [`custom_channels.json`](custom_channels.json):

```json
{
  "dstv": [
    {
      "name": "SuperSport Premier League",
      "tvg_id": "supersport-premier-league",
      "tvg_name": "SuperSport Premier League",
      "tvg_logo": "https://raw.githubusercontent.com/iptv-org/epg/master/logos/za/SuperSportPremierLeague.png",
      "group": "DStv Sports",
      "url": "https://example.com/streams/dstv/ss_pl.m3u8"
    }
  ],
  "custom": [
    {
      "name": "My Custom FAST Channel",
      "tvg_id": "my-channel-id",
      "tvg_logo": "https://example.com/logo.png",
      "group": "Entertainment",
      "url": "https://example.com/stream/index.m3u8"
    }
  ]
}
```

---

## 💻 Local Usage

### Prerequisites
- Python 3.10+

### Installation & Run
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run generator
python generate_playlists.py
```
Generated `.m3u8` playlists and `index.json` metadata will be saved in the `playlists/` directory.

---

## 📱 IPTV Player Compatibility
- **TiviMate** (Android TV / FireStick)
- **Kodi** (IPTV Simple Client)
- **Jellyfin / Emby / Plex** (Live TV & DVR)
- **OTT Navigator / IPTV Smarters**
- **VLC Media Player / IINA**
