# Global FAST M3U Playlist & EPG Generator (All Regions)

Automated global FAST (Free Ad-supported Streaming TV) and IPTV playlist generator with standardized EPG (Electronic Program Guide) auto-injection across all worldwide regions (Roku, Pluto TV, Samsung TV Plus, Plex TV, Tubi TV, Global FAST, and DStv).

---

## 📺 Direct Raw Stream URLs (For your IPTV Player)

Copy and paste any of these direct Raw URLs into your IPTV player (**TiviMate**, **Kodi**, **Jellyfin**, **VLC**, **OTT Navigator**, **IPTV Smarters**, etc.):

### 🌟 Master Combined Playlist (9,000+ Channels Across All Networks)
- **M3U**: `https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u`
- **M3U8**: `https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u8`

---

### 🌐 Individual Network Playlists (All Regions)

| Network / Source | Direct Raw M3U Link | Direct Raw M3U8 Link | Injected EPG Source | Channels |
| :--- | :--- | :--- | :--- | :--- |
| **Roku TV (All Regions)** | [`roku_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u) | [`roku_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u8) | `https://i.mjh.nz/Roku/all.xml.gz` | **286** |
| **Pluto TV (All Regions)** | [`plutotv_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u) | [`plutotv_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u8) | `https://i.mjh.nz/PlutoTV/all.xml.gz` | **2,862** |
| **Samsung TV Plus (All)** | [`samsung_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u) | [`samsung_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u8) | `https://i.mjh.nz/SamsungTVPlus/all.xml.gz` | **2,603** |
| **Plex TV (All Regions)** | [`plex_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u) | [`plex_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u8) | `https://i.mjh.nz/Plex/all.xml.gz` | **2,824** |
| **Tubi TV (All Regions)** | [`tubi_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u) | [`tubi_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u8) | Auto-injected XML | **179** |
| **Global All Channels** | [`mjh_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u) | [`mjh_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u8) | `https://i.mjh.nz/all/epg.xml.gz` | **282** |
| **World Channels** | [`world.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u) | [`world.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u8) | `https://i.mjh.nz/world/epg.xml.gz` | **4** |
| **DStv South Africa / Africa** | [`dstv.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/dstv.m3u) | [`dstv.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/dstv.m3u8) | `https://i.mjh.nz/DStv/za.xml.gz` | **3** (Custom) |

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
