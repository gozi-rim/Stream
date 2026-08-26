# FAST M3U Playlist & EPG Generator

Automated FAST (Free Ad-supported Streaming TV) and regional IPTV M3U8/M3U playlist generator with standardized EPG (Electronic Program Guide) auto-injection for New Zealand, Australia, Samsung TV Plus NZ, Plex TV AU, DStv South Africa, and custom sources.

---

## 📺 Direct Raw Stream URLs (For your IPTV Player)

Once pushed to your GitHub repository (e.g. `https://github.com/gozi-rim/STREAM`), you can copy and paste any of the following direct Raw URLs directly into your IPTV Player (TiviMate, Kodi, Jellyfin, VLC, OTT Navigator, IPTV Smarters, etc.):

### 🌟 Master Combined Playlist (All Regions & Channels)
- **M3U**: `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/all_combined.m3u`
- **M3U8**: `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/all_combined.m3u8`

---

### 🌐 Regional Playlists

| Regional Source | Direct Raw M3U URL | Direct Raw M3U8 URL | Injected EPG Source |
| :--- | :--- | :--- | :--- |
| **NZ / AU Combined** | `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/nzau.m3u` | `.../playlists/nzau.m3u8` | `https://i.mjh.nz/nzau/epg.xml.gz` |
| **AU All Channels** | `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/au_all.m3u` | `.../playlists/au_all.m3u8` | `https://i.mjh.nz/au/all/epg.xml.gz` |
| **NZ All Channels** | `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/nz_all.m3u` | `.../playlists/nz_all.m3u8` | `https://i.mjh.nz/nz/epg.xml.gz` |
| **DStv South Africa** | `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/dstv.m3u` | `.../playlists/dstv.m3u8` | `https://i.mjh.nz/DStv/za.xml.gz` |
| **Samsung TV Plus NZ** | `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/samsung_nz.m3u` | `.../playlists/samsung_nz.m3u8` | `https://i.mjh.nz/SamsungTVPlus/nz.xml.gz` |
| **Plex TV AU** | `https://raw.githubusercontent.com/gozi-rim/STREAM/main/playlists/plex_au.m3u` | `.../playlists/plex_au.m3u8` | `https://i.mjh.nz/Plex/au.xml.gz` |

> 💡 **Auto EPG Injection**: Every playlist has `#EXTM3U url-tvg="..." x-tvg-url="..."` headers automatically injected. You do **not** need to manually copy or type separate EPG URLs in your IPTV client—it loads guide data automatically!

---

## ⚡ Automated Updates (GitHub Actions)

The repository runs [`.github/workflows/update_playlists.yml`](.github/workflows/update_playlists.yml) on a scheduled cron:
- **Frequency**: Runs automatically **every 4 hours** (`0 */4 * * *`).
- **Trigger**: Also supports manual run on-demand via the **Actions** tab in GitHub.
- **Auto-Sync**: Checks upstream providers, regenerates `.m3u` and `.m3u8` playlists, and auto-commits any updates with `[skip ci]`.
- Your IPTV player simply fetches your GitHub raw URL and always stays up to date!

---

## 🛠️ Adding Custom Streams & Channels

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

## 💻 Local Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run generator locally
python generate_playlists.py
```
