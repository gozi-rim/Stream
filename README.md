# Global FAST M3U Playlist & EPG Generator (All Regions)

Automated global FAST (Free Ad-supported Streaming TV) and IPTV playlist generator with standardized EPG (Electronic Program Guide) auto-injection, dynamic category grouping (News, Sports, Movies, Kids, Nollywood, Entertainment), deduplication, and automated GitHub sync.

---

## 🌟 Curated & Popular Playlists (Recommended)

Copy and paste these direct Raw URLs into your IPTV player (**TiviMate**, **Kodi**, **Jellyfin**, **VLC**, **OTT Navigator**, **IPTV Smarters**, etc.):

| Curated Playlist | Direct Raw M3U Link | Direct Raw M3U8 Link | Channels | Description |
| :--- | :--- | :--- | :--- | :--- |
| **⭐ Popular Favorites** | [`popular_favorites.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/popular_favorites.m3u) | [`popular_favorites.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/popular_favorites.m3u8) | **247** | *Curated household names: BBC, CNN, Sky News, Bloomberg, ESPN, Nickelodeon, Paramount, Moviesphere, CSI, Top Gear, MTV, Vevo, Channels TV, Arise News, TVC News, Nolly Africa HD* |
| **🎬 Nollywood & African TV (Curated)** | [`nollywood.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/nollywood.m3u) | [`nollywood.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/nollywood.m3u8) | **4** | *Curated Nigerian news & Nollywood: Arise News (Live HD), TVC News Nigeria (24/7 Studio), Channels Television (Live HD), Nolly Africa HD* |
| **🌍 Africa Live Channels (Full Group)** | [`iptv_org_africa.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/iptv_org_africa.m3u) | [`iptv_org_africa.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/iptv_org_africa.m3u8) | **494** | *Full categorized regional group: African live channels across Nigeria, Ghana, Kenya, South Africa, Uganda, Cameroon, etc.* |
| **🌐 Global Open Live TV (Full Group)** | [`freetv_global.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/freetv_global.m3u) | [`freetv_global.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/freetv_global.m3u8) | **1,936** | *Full categorized regional group: Direct origin CDN streams without geo-blocking across all global genres* |
| **🌐 Master Combined (All Networks)** | [`all_combined.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u) | [`all_combined.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/all_combined.m3u8) | **5,707** | *Deduplicated master playlist containing every single unique working channel categorized cleanly* |

---

## 📺 Individual Network Playlists (All Regions - Categorized)

Every playlist is categorized by genre (**News & Weather**, **Sports & Racing**, **Movies & Cinema**, **Kids & Family**, **Animation & Anime**, **Comedy**, **Crime**, **Documentary**, **Music**, **Entertainment**):

| Network / Source | Direct Raw M3U Link | Direct Raw M3U8 Link | Injected EPG Source | Channels |
| :--- | :--- | :--- | :--- | :--- |
| **Samsung TV Plus (All)** | [`samsung_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u) | [`samsung_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/samsung_all.m3u8) | `https://i.mjh.nz/SamsungTVPlus/all.xml.gz` | **1,572** |
| **Pluto TV (All Regions)** | [`plutotv_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u) | [`plutotv_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plutotv_all.m3u8) | `https://i.mjh.nz/PlutoTV/all.xml.gz` | **1,512** |
| **Plex TV (All Regions)** | [`plex_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u) | [`plex_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/plex_all.m3u8) | `https://i.mjh.nz/Plex/all.xml.gz` | **948** |
| **Roku TV (All Regions)** | [`roku_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u) | [`roku_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/roku_all.m3u8) | `https://i.mjh.nz/Roku/all.xml.gz` | **286** |
| **Tubi TV (All Regions)** | [`tubi_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u) | [`tubi_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/tubi_all.m3u8) | Auto-injected XML | **179** |
| **Global FAST Channels** | [`mjh_all.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u) | [`mjh_all.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/mjh_all.m3u8) | `https://i.mjh.nz/all/epg.xml.gz` | **170** |
| **World Channels** | [`world.m3u`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u) | [`world.m3u8`](https://raw.githubusercontent.com/gozi-rim/Stream/main/playlists/world.m3u8) | `https://i.mjh.nz/world/epg.xml.gz` | **4** |

> 💡 **Auto EPG Injection**: Every playlist has `#EXTM3U url-tvg="..." x-tvg-url="..."` headers automatically injected. You do **not** need to manually copy or type separate EPG URLs in your IPTV client—it loads guide data automatically!

---

## ⚡ Automated Updates (GitHub Actions)

The repository runs [`.github/workflows/update_playlists.yml`](.github/workflows/update_playlists.yml) on a scheduled cron:
- **Frequency**: Runs automatically **every 2 hours** (`0 */2 * * *`).
- **Trigger**: Also supports manual run on-demand via the **Actions** tab in GitHub.
- **Auto-Sync**: Checks upstream providers, refreshes live stream tokens, regenerates `.m3u` and `.m3u8` playlists with dynamic category sorting and deduplication, and auto-commits any updates.

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
