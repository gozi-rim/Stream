# Global FAST M3U Playlist & EPG Generator (All Regions)

Automated global FAST (Free Ad-supported Streaming TV) and IPTV playlist generator featuring:
- **Intelligent Deduplication**: Eliminates repetitive clones across all hosts and retains only the single highest quality (4K / 1080p / 720p HD) working feed.
- **Dead Stream Scrubbing**: Automatic validation and filtering of offline, non-HTTP, and broken placeholder streams.
- **Dynamic Live Stream Refresh**: Auto-extracts and refreshes 1080p Full HD live HLS feeds for African & Nigerian news channels (Channels Television, TVC News, Arise News) using `yt-dlp`.
- **Dynamic Category Grouping**: Channels sorted cleanly into genre folders (*News & Weather*, *Sports & Racing*, *Movies & Cinema*, *Kids & Family*, *Animation*, *Comedy*, *Crime*, *Music*, *Entertainment*).
- **Auto EPG Injection**: `#EXTM3U url-tvg="..." x-tvg-url="..."` headers are automatically embedded for instant guide data in IPTV apps.
- **Automated 4-Hour GitHub Sync**: Continual updates via GitHub Actions cron.

---

## 🌟 Curated & Master Playlists (Recommended)

Copy and paste these direct Raw URLs into your IPTV player (**TiviMate**, **Kodi**, **Jellyfin**, **VLC**, **OTT Navigator**, **IPTV Smarters**, etc.):

| Playlist | Direct Raw M3U Link | Direct Raw M3U8 Link | Channels | Description |
| :--- | :--- | :--- | :---: | :--- |
| **⭐ Popular Favorites (Curated Best)** | [`popular_favorites.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/popular_favorites.m3u) | [`popular_favorites.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/popular_favorites.m3u8) | **248** | *Top household names: BBC News, CNN, Sky News, Bloomberg, ESPN, Nickelodeon, Paramount, Hallmark, CSI, Top Gear, Channels TV, TVC News, Arise News* |
| **🌐 Master Combined (All Unique Channels)** | [`all_combined.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u) | [`all_combined.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u8) | **3,511** | *Complete worldwide catalog deduplicated to the highest quality stream per channel and categorized* |
| **🎬 Nollywood & African TV** | [`nollywood.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/nollywood.m3u) | [`nollywood.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/nollywood.m3u8) | **4** | *Channels Television, TVC News Nigeria, Arise News, Nolly Africa HD* |

---

## 📺 Individual Network Playlists (Categorized & Deduplicated)

| Network / Source | Direct Raw M3U Link | Direct Raw M3U8 Link | Injected EPG Source | Unique Channels |
| :--- | :--- | :--- | :--- | :---: |
| **Samsung TV Plus (All)** | [`samsung_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u) | [`samsung_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u8) | `https://i.mjh.nz/SamsungTVPlus/all.xml.gz` | **1,572** |
| **Pluto TV (All Regions)** | [`plutotv_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u) | [`plutotv_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u8) | `https://i.mjh.nz/PlutoTV/all.xml.gz` | **1,512** |
| **Plex TV (All Regions)** | [`plex_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u) | [`plex_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u8) | `https://i.mjh.nz/Plex/all.xml.gz` | **948** |
| **Roku TV (All Regions)** | [`roku_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u) | [`roku_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u8) | `https://i.mjh.nz/Roku/all.xml.gz` | **286** |
| **Tubi TV (All Regions)** | [`tubi_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u) | [`tubi_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u8) | Auto-injected XML | **179** |
| **Global FAST Channels** | [`mjh_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u) | [`mjh_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u8) | `https://i.mjh.nz/all/epg.xml.gz` | **213** |
| **World Channels** | [`world.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u) | [`world.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u8) | `https://i.mjh.nz/world/epg.xml.gz` | **4** |

> 💡 **Auto EPG Injection**: Every playlist has `#EXTM3U url-tvg="..." x-tvg-url="..."` headers automatically injected. Your IPTV player will load program schedules without extra configuration!

---

## ⚡ Automated Updates (GitHub Actions)

The repository runs [`.github/workflows/update_playlists.yml`](.github/workflows/update_playlists.yml) on a scheduled cron:
- **Frequency**: Runs automatically **every 4 hours** (`0 */4 * * *`).
- **Trigger**: Also supports manual run on-demand via the **Actions** tab in GitHub.
- **Auto-Sync**: Checks upstream providers, refreshes live stream tokens via `yt-dlp`, eliminates duplicates, applies dynamic category sorting, and auto-commits any updates with `[skip ci]`.

---

## 💻 Local Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run generator locally
python generate_playlists.py
```

---

## ⚖️ Legal Disclaimer

This repository does **not** host, broadcast, archive, or re-transmit any media, video, or audio streams. It is an open-source educational aggregation and indexing tool that standardizes playlist metadata and links to publicly available, free-to-air third-party streams and FAST providers. All channel names, marks, and logos belong to their respective copyright holders.

For full legal terms and DMCA notice procedures, please refer to [**`DISCLAIMER.md`**](DISCLAIMER.md).

---

## 📄 License

Distributed under the **MIT License**. See [**`LICENSE`**](LICENSE) for more information.
