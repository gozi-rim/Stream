# Global FAST M3U Playlist & EPG Generator (All Regions)

Automated global FAST (Free Ad-supported Streaming TV) and IPTV playlist generator with standardized EPG (Electronic Program Guide) auto-injection, dynamic category grouping (News, Sports, Movies, Kids, Nollywood, Entertainment), and automated 4-hour GitHub sync.

---

## 🌟 Curated & Popular Playlists (Recommended)

Copy and paste these direct Raw URLs into your IPTV player (**TiviMate**, **Kodi**, **Jellyfin**, **VLC**, **OTT Navigator**, **IPTV Smarters**, etc.):

| Curated Playlist | Direct Raw M3U Link | Direct Raw M3U8 Link | Channels | Description |
| :--- | :--- | :--- | :--- | :--- |
| **⭐ Popular Favorites (Curated Best)** | [`popular_favorites.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/popular_favorites.m3u) | [`popular_favorites.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/popular_favorites.m3u8) | **277** | *Famous household names: BBC, CNN, Sky News, ESPN, Nickelodeon, Hallmark, Paramount, CSI, Top Gear, MTV, Vevo, Nollywood* |
| **🎬 Nollywood & African TV** | [`nollywood.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/nollywood.m3u) | [`nollywood.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/nollywood.m3u8) | **13** | *Channels TV, Nolly Africa HD, TVC News, AIT, Silverbird, Soundcity, Africa Magic, NTA News 24, Arewa 24* |
| **🌐 Master Combined (All Networks)** | [`all_combined.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u) | [`all_combined.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u8) | **9,056** | *Everything combined and sorted into structured category folders* |

---

## 📺 Individual Network Playlists (All Regions - Categorized)

Every playlist is categorized by genre (**News & Weather**, **Sports & Racing**, **Movies & Cinema**, **Kids & Family**, **Animation & Anime**, **Comedy**, **Crime**, **Documentary**, **Music**, **Entertainment**):

| Network / Source | Direct Raw M3U Link | Direct Raw M3U8 Link | Injected EPG Source | Channels |
| :--- | :--- | :--- | :--- | :--- |
| **Samsung TV Plus (All)** | [`samsung_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u) | [`samsung_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u8) | `https://i.mjh.nz/SamsungTVPlus/all.xml.gz` | **2,603** |
| **Pluto TV (All Regions)** | [`plutotv_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u) | [`plutotv_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u8) | `https://i.mjh.nz/PlutoTV/all.xml.gz` | **2,862** |
| **Plex TV (All Regions)** | [`plex_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u) | [`plex_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u8) | `https://i.mjh.nz/Plex/all.xml.gz` | **2,824** |
| **Roku TV (All Regions)** | [`roku_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u) | [`roku_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u8) | `https://i.mjh.nz/Roku/all.xml.gz` | **286** |
| **Tubi TV (All Regions)** | [`tubi_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u) | [`tubi_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u8) | Auto-injected XML | **179** |
| **Global FAST Channels** | [`mjh_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u) | [`mjh_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u8) | `https://i.mjh.nz/all/epg.xml.gz` | **282** |
| **World Channels** | [`world.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u) | [`world.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u8) | `https://i.mjh.nz/world/epg.xml.gz` | **4** |
| **DStv South Africa / Africa** | [`dstv.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/dstv.m3u) | [`dstv.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/dstv.m3u8) | `https://i.mjh.nz/DStv/za.xml.gz` | **6** (Custom) |

> 💡 **Auto EPG Injection**: Every playlist has `#EXTM3U url-tvg="..." x-tvg-url="..."` headers automatically injected. You do **not** need to manually copy or type separate EPG URLs in your IPTV client—it loads guide data automatically!

---

## ⚡ Automated Updates (GitHub Actions)

The repository runs [`.github/workflows/update_playlists.yml`](.github/workflows/update_playlists.yml) on a scheduled cron:
- **Frequency**: Runs automatically **every 4 hours** (`0 */4 * * *`).
- **Trigger**: Also supports manual run on-demand via the **Actions** tab in GitHub.
- **Auto-Sync**: Checks upstream providers, regenerates `.m3u` and `.m3u8` playlists with dynamic category sorting, and auto-commits any updates with `[skip ci]`.
- Your IPTV player simply fetches your GitHub raw URL and always stays up to date!

---

## 🛠️ Adding Custom Streams & Channels

You can add custom channels or fallback streams directly in [`custom_channels.json`](custom_channels.json):

```json
{
  "nollywood": [
    {
      "name": "My Custom African Movie Channel",
      "tvg_id": "custom-african-movie",
      "tvg_logo": "https://example.com/logo.png",
      "group": "Nollywood & African TV",
      "url": "https://example.com/streams/live.m3u8"
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

---

## ⚖️ Legal Disclaimer

This repository does **not** host, broadcast, archive, or re-transmit any media, video, or audio streams. It is an open-source educational aggregation and indexing tool that standardizes playlist metadata and links to publicly available, free-to-air third-party streams and FAST providers. All channel names, marks, and logos belong to their respective copyright holders.

For full legal terms and DMCA notice procedures, please refer to [**`DISCLAIMER.md`**](DISCLAIMER.md).

---

## 📄 License

Distributed under the **MIT License**. See [**`LICENSE`**](LICENSE) for more information.
