#!/usr/bin/env python3
"""
FAST M3U Playlist and EPG Generator (All-Region & Categorized Edition)
======================================================================
Automates fetching, standardizing, categorizing, and generating global FAST
and IPTV playlists with auto-injected EPG:
- Samsung TV Plus (All Regions - Categorized)
- Pluto TV (All Regions - Categorized)
- Plex TV (All Regions - Categorized)
- Roku TV (All Regions - Categorized)
- Tubi TV (All Regions - Categorized)
- Global FAST Channels (MJH)
- World Channels (MJH)
- DStv South Africa / Africa
- Nollywood & African TV (Dedicated Curated Playlist)
- Popular Favorites (Curated Best-of-the-Best across all categories)
- Master Combined (All Networks - 9,000+ Channels Categorized)
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

# Category Definitions & Regex Patterns
CATEGORY_RULES = [
    ("Nollywood & African TV", [
        r'\bnolly\b', r'\bnollywood\b', r'\bafrica\b', r'\bafrique\b', r'\bnigeria\b', r'\bnaija\b',
        r'\bchannels tv\b', r'\bchannels 24\b', r'\btvc news\b', r'\bnta\b', r'\bait\b', r'\bsilverbird\b',
        r'\bsoundcity\b', r'\barewa\b', r'\bafrican movie\b', r'\brok\b', r'\bafroland\b', r'\bwakaati\b',
        r'\bafrica magic\b', r'\bamusic\b'
    ]),
    ("News & Weather", [
        r'\bnews\b', r'\bweather\b', r'\bbloomberg\b', r'\bcnn\b', r'\bnbc news\b', r'\bcbs news\b',
        r'\babc news\b', r'\beuronews\b', r'\breuters\b', r'\bjournal\b', r'\bnoticias\b', r'\bnachrichten\b',
        r'\bpress\b', r'\bheadline\b', r'\btoday\b', r'\bactualit', r'\btg\b', r'\binform\b', r'\bal jazeera\b',
        r'\bfinance\b', r'\bmarket\b', r'\bmeteorolog\b', r'\bmeteo\b', r'\baccuweather\b', r'\blive now\b',
        r'\bsky news\b', r'\bcnbc\b', r'\bmsnbc\b', r'\bfrance 24\b', r'\bdw\b', r'\bweather channel\b'
    ]),
    ("Sports & Racing", [
        r'\bsport\b', r'\bsports\b', r'\bespn\b', r'\bracing\b', r'\bmoto\b', r'\bf1\b', r'\bnfl\b', r'\bnba\b',
        r'\bmlb\b', r'\bnhl\b', r'\bpga\b', r'\bgolf\b', r'\btennis\b', r'\bfight\b', r'\bmma\b', r'\bboxing\b',
        r'\bwrestling\b', r'\bimpact\b', r'\bstadium\b', r'\bred bull\b', r'\bsoccer\b', r'\bfootball\b',
        r'\bfifa\b', r'\buefa\b', r'\blucha\b', r'\bfis\b', r'\bsurf\b', r'\bskate\b', r'\bextreme\b',
        r'\bworld poker\b', r'\bpoker\b', r'\bbilliard\b', r'\bdarts\b', r'\boutdoor\b', r'\bhunt\b', r'\bfish\b',
        r'\bcricket\b', r'\brugby\b', r'\btennis channel\b', r'\bworld of freesports\b', r'\bhard knocks\b',
        r'\bbein\b', r'\bsupersport\b', r'\bmotorvision\b', r'\bmotorsport\b'
    ]),
    ("Movies & Cinema", [
        r'\bmovie\b', r'\bmovies\b', r'\bfilm\b', r'\bfilms\b', r'\bcinema\b', r'\bcine\b', r'\bpelicula\b',
        r'\bhallmark\b', r'\bmoviesphere\b', r'\bparamount\b', r'\bsony\b', r'\bhorror\b', r'\bthriller\b',
        r'\bwesterns?\b', r'\baction movie\b', r'\bclassic movie\b', r'\bhollywood\b', r'\bblockbuster\b',
        r'\bfilmtastic\b', r'\bshudder\b', r'\bfilmrise\b', r'\bmovieland\b', r'\bcinemax\b', r'\bcinevault\b',
        r'\bdust\b'
    ]),
    ("Animation & Anime", [
        r'\banime\b', r'\banimation\b', r'\bcartoon\b', r'\bretrocrush\b', r'\byu-gi-oh\b', r'\bbeyblade\b',
        r'\btoon\b', r'\bmanga\b', r'\banimedia\b', r'\btoku\b', r'\banime all day\b'
    ]),
    ("Kids & Family", [
        r'\bkids\b', r'\bkid\b', r'\bchildren\b', r'\bnick\b', r'\bnickelodeon\b', r'\bjr\b', r'\blego\b',
        r'\bpok[eé]mon\b', r'\bbaby\b', r'\bteletubbies\b', r'\bbarney\b', r'\bducktv\b', r'\bdisney\b',
        r'\bfamily\b', r'\bjunior\b', r'\benfant\b', r'\bkind\b', r'\bniñ\b', r'\bcaillou\b', r'\bcare bears\b',
        r'\byo gabba\b', r'\btransformers\b', r'\bpower rangers\b', r'\bkartoon\b', r'\btoontastic\b'
    ]),
    ("Comedy & Stand-up", [
        r'\bcomedy\b', r'\bcomedies\b', r'\blaugh\b', r'\bstand-?up\b', r'\bfailarmy\b', r'\bwipeout\b',
        r'\bjust for laughs\b', r'\bfunny\b', r'\bhumor\b', r'\bcomedia\b', r'\bhumour\b', r'\bpranks?\b',
        r'\banger management\b', r'\bthe pet collective\b', r'\bchuckle\b'
    ]),
    ("Crime & Mystery", [
        r'\bcrime\b', r'\bmystery\b', r'\bdetective\b', r'\bforensic\b', r'\bcourt\b', r'\bjudge\b',
        r'\blaw & order\b', r'\bcsi\b', r'\bunsolved\b', r'\bcops\b', r'\bpolice\b', r'\binvestigat\b',
        r'\btrue crime\b', r'\bhomicide\b', r'\bmurder\b', r'\bfbi\b', r'\bswat\b', r'\b48 hours\b'
    ]),
    ("Documentary & Nature", [
        r'\bdoc\b', r'\bdocumentar\b', r'\bnat geo\b', r'\bdiscovery\b', r'\bhistory\b', r'\bscience\b',
        r'\bnature\b', r'\bwild\b', r'\bwildlife\b', r'\bplanet\b', r'\banimal\b', r'\bspace\b',
        r'\bgeo\b', r'\bterranova\b', r'\bvoyage\b', r'\bplan[eè]te\b', r'\bcuriosity\b', r'\bhistory time\b'
    ]),
    ("Lifestyle, Food & Travel", [
        r'\bfood\b', r'\bcooking\b', r'\bcook\b', r'\bkitchen\b', r'\bchef\b', r'\btastemade\b',
        r'\bbon app[eé]tit\b', r'\bhgtv\b', r'\bhome\b', r'\bhouse\b', r'\bgarden\b', r'\bdesign\b',
        r'\bfashion\b', r'\btravel\b', r'\bluxury\b', r'\bvoyage\b', r'\bauto\b', r'\bmotor\b', r'\bgarage\b',
        r'\bcraft\b', r'\bdiy\b', r'\bhealth\b', r'\bfitness\b', r'\byoga\b', r'\bgordon ramsay\b',
        r'\bjames may\b', r'\btop gear\b', r'\bchasse\b', r'\bpêche\b', r'\brestaurant\b'
    ]),
    ("Music & Audio", [
        r'\bmusic\b', r'\bmusica\b', r'\bmusik\b', r'\bmtv\b', r'\bvevo\b', r'\bstingray\b', r'\bqello\b',
        r'\bconcert\b', r'\bhit\b', r'\bhits\b', r'\bpop\b', r'\brock\b', r'\bhip hop\b', r'\bjazz\b',
        r'\bclassic[ao]\b', r'\bdance\b', r'\bradio\b', r'\bk-?pop\b', r'\br&b\b', r'\bcountry music\b'
    ]),
    ("Reality & Game Shows", [
        r'\breality\b', r'\bgame show\b', r'\bprice is right\b', r'\bdeal or no deal\b', r'\bfear factor\b',
        r'\bsurvivor\b', r'\bpawn stars\b', r'\bstorage wars\b', r'\bantiques roadshow\b', r'\bhell\'?s kitchen\b',
        r'\bmasterchef\b', r'\bbachelor\b', r'\bbig brother\b', r'\btalent\b', r'\bidol\b'
    ]),
    ("Classic TV & Sitcoms", [
        r'\bclassic\b', r'\bsitcom\b', r'\bretro\b', r'\b21 jump street\b', r'\bbaywatch\b', r'\bdegDegrassi\b',
        r'\bmarried with children\b', r'\b3rd rock\b', r'\bcarol burnett\b', r'\bjohnny carson\b', r'\bhappy days\b'
    ]),
    ("Drama & Series", [
        r'\bdrama\b', r'\bseries\b', r'\bsoap\b', r'\btelenovela\b', r'\btv series\b', r'\bk-drama\b',
        r'\bdoctor who\b', r'\bmidsomer\b', r'\bheartland\b', r'\bholby\b', r'\bcasualty\b', r'\bcoronation\b'
    ]),
    ("Gaming & Tech", [
        r'\bgaming\b', r'\bgame\b', r'\bign\b', r'\bgamespot\b', r'\besports\b', r'\btwitch\b', r'\btech\b'
    ]),
    ("Entertainment", [
        r'\bshow\b', r'\bentertainment\b', r'\btv\b', r'\bvariety\b', r'\bcelebrity\b', r'\binterviews?\b'
    ])
]

# Order for sorting categories in playlist
CATEGORY_ORDER = [
    "Nollywood & African TV",
    "News & Weather",
    "Sports & Racing",
    "Movies & Cinema",
    "Animation & Anime",
    "Kids & Family",
    "Comedy & Stand-up",
    "Crime & Mystery",
    "Documentary & Nature",
    "Lifestyle, Food & Travel",
    "Music & Audio",
    "Reality & Game Shows",
    "Classic TV & Sitcoms",
    "Drama & Series",
    "Gaming & Tech",
    "Entertainment"
]

CATEGORY_PRIORITY = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}

# Popular Brand Channel Filters (Famous household names only)
POPULAR_KEYWORDS = [
    # News
    r'\bbbc news\b', r'\bcnn\b', r'\bsky news\b', r'\bbloomberg\b', r'\beuronews\b', r'\bal jazeera\b',
    r'\babc news live\b', r'\bcbs news\b', r'\bnbc news now\b', r'\breuters\b', r'\bweather channel\b',
    # Sports
    r'\bespn\b', r'\bbein sports\b', r'\bpga tour\b', r'\bnfl channel\b', r'\bmlb\b', r'\bnhl\b',
    r'\btennis channel\b', r'\bred bull tv\b', r'\bfight network\b', r'\bimpact wrestling\b',
    r'\bmotorvision\b', r'\bstadium\b',
    # Kids & Animation
    r'\bnickelodeon\b', r'\bnick jr\b', r'\blego\b', r'\bpok[eé]mon\b', r'\banime all day\b',
    r'\bretrocrush\b', r'\byu-gi-oh\b', r'\bbaby einstein\b', r'\bducktv\b', r'\bpower rangers\b',
    # Movies
    r'\bhallmark\b', r'\bparamount movie\b', r'\bmoviesphere\b', r'\bsony\b', r'\bfilmrise\b', r'\bshudder\b',
    # Comedy, Drama & Entertainment
    r'\bcomedy central\b', r'\bdoctor who\b', r'\bbaywatch\b', r'\bcsi\b', r'\blaw & order\b',
    r'\b21 jump street\b', r'\bheartland\b', r'\bgordon ramsay\b', r'\btop gear\b', r'\btastemade\b',
    r'\bmtv\b', r'\bvevo\b', r'\bfailarmy\b', r'\bprice is right\b', r'\bdeal or no deal\b',
    # Nollywood & Africa
    r'\bnolly\b', r'\bnollywood\b', r'\bchannels tv\b', r'\btvc news\b', r'\bafrica magic\b',
    r'\bsoundcity\b', r'\bsilverbird\b', r'\bait\b', r'\bnta\b'
]


def is_popular_channel(channel_name: str) -> bool:
    """Check if channel belongs to famous popular brand channels."""
    text = channel_name.lower()
    return any(re.search(p, text) for p in POPULAR_KEYWORDS)


def classify_channel(channel_name: str, existing_group: str = "") -> str:
    """Determine the channel category based on name and context."""
    text = f"{channel_name} {existing_group}".lower()
    for cat_name, patterns in CATEGORY_RULES:
        for p in patterns:
            if re.search(p, text):
                return cat_name
    return "Entertainment"


# All-Region Sources Configuration
SOURCES_CONFIG = [
    {
        "id": "samsung_all",
        "name": "Samsung TV Plus (All Regions - Categorized)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_all.m3u",
        "fallback_urls": [
            "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/samsungtvplus_us.m3u"
        ],
        "epg_url": "https://i.mjh.nz/SamsungTVPlus/all.xml.gz",
        "output_filename": "samsung_all.m3u8",
        "default_group": "Entertainment",
        "categorize": True
    },
    {
        "id": "plutotv_all",
        "name": "Pluto TV (All Regions - Categorized)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plutotv_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/PlutoTV/all.xml.gz",
        "output_filename": "plutotv_all.m3u8",
        "default_group": "Entertainment",
        "categorize": True
    },
    {
        "id": "plex_all",
        "name": "Plex TV (All Regions - Categorized)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/plex_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/Plex/all.xml.gz",
        "output_filename": "plex_all.m3u8",
        "default_group": "Entertainment",
        "categorize": True
    },
    {
        "id": "roku_all",
        "name": "Roku TV (All Regions - Categorized)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/roku_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/Roku/all.xml.gz",
        "output_filename": "roku_all.m3u8",
        "default_group": "Entertainment",
        "categorize": True
    },
    {
        "id": "tubi_all",
        "name": "Tubi TV (All Regions - Categorized)",
        "url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_all.m3u",
        "fallback_urls": [],
        "epg_url": "https://raw.githubusercontent.com/BuddyChewChew/app-m3u-generator/main/playlists/tubi_epg.xml",
        "output_filename": "tubi_all.m3u8",
        "default_group": "Entertainment",
        "categorize": True
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
        "default_group": "Global FAST",
        "categorize": True
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
        "default_group": "World TV",
        "categorize": True
    },
    {
        "id": "dstv",
        "name": "DStv South Africa / Africa",
        "url": "https://i.mjh.nz/DStv/raw-tv.m3u8",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/DStv/za.xml.gz",
        "output_filename": "dstv.m3u8",
        "default_group": "Nollywood & African TV",
        "categorize": True
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


def process_channel_block(block_lines: List[str], categorize: bool, default_group: str) -> Tuple[str, str, str]:
    """
    Process a single channel block:
    - Extracts channel name
    - Classifies category if categorize=True and updates group-title
    - Returns (category, channel_name, formatted_block_string)
    """
    extinf_line = block_lines[0]
    
    # Extract channel name
    name_match = re.search(r',([^,]+)$', extinf_line)
    channel_name = name_match.group(1).strip() if name_match else "Channel"

    # Extract existing group-title
    group_match = re.search(r'group-title="([^"]+)"', extinf_line)
    orig_group = group_match.group(1) if group_match else default_group

    if categorize:
        category = classify_channel(channel_name, orig_group)
        # Replace or add group-title
        if group_match:
            new_extinf = extinf_line[:group_match.start(1)] + category + extinf_line[group_match.end(1):]
        else:
            new_extinf = extinf_line.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{category}"')
        block_lines[0] = new_extinf
    else:
        category = orig_group

    return category, channel_name, "\n".join(block_lines)


def standardize_playlist(
    raw_content: Optional[str],
    epg_url: str,
    custom_entries: List[dict],
    default_group: str,
    categorize: bool = False
) -> Tuple[str, int, Dict[str, int], List[Tuple[str, str, str]]]:
    """
    Standardize, categorize, and sort M3U8 content.
    Returns (standardized_m3u8_string, total_channel_count, category_breakdown, channel_items_list)
    """
    header = f'#EXTM3U url-tvg="{epg_url}" x-tvg-url="{epg_url}"'
    channel_items = []  # List of tuples: (category, channel_name, block_str)
    category_counts = {}

    if raw_content:
        lines = [line.strip() for line in raw_content.splitlines() if line.strip()]
        
        current_entry_lines = []
        for line in lines:
            if line.startswith("#EXTM3U"):
                continue
            
            if line.startswith("#EXTINF"):
                if current_entry_lines:
                    if any(not l.startswith("#") for l in current_entry_lines):
                        cat, name, formatted = process_channel_block(current_entry_lines, categorize, default_group)
                        channel_items.append((cat, name, formatted))
                        category_counts[cat] = category_counts.get(cat, 0) + 1
                    current_entry_lines = []
                current_entry_lines.append(line)
            elif current_entry_lines:
                current_entry_lines.append(line)
        
        if current_entry_lines and any(not l.startswith("#") for l in current_entry_lines):
            cat, name, formatted = process_channel_block(current_entry_lines, categorize, default_group)
            channel_items.append((cat, name, formatted))
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Append custom channels
    for custom_item in custom_entries:
        custom_block = format_custom_channel(custom_item, default_group)
        if custom_block.strip():
            lines = custom_block.splitlines()
            cat, name, formatted = process_channel_block(lines, categorize, default_group)
            channel_items.append((cat, name, formatted))
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Sort channels by Category Priority, then by Channel Name
    if categorize:
        channel_items.sort(key=lambda x: (CATEGORY_PRIORITY.get(x[0], 99), x[1].lower()))
    else:
        channel_items.sort(key=lambda x: (x[0].lower(), x[1].lower()))

    # Assemble complete playlist
    output_lines = [header, ""]
    for _, _, block_str in channel_items:
        output_lines.append(block_str)
        output_lines.append("")
        
    return "\n".join(output_lines).strip() + "\n", len(channel_items), category_counts, channel_items


def generate_all():
    """Main execution function to process all playlists and generate master outputs."""
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)
    session = create_session()
    custom_channels = load_custom_channels()
    
    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "edition": "All-Region Global FAST (Categorized Edition)",
        "playlists": []
    }
    
    all_combined_channels = []  # Tuples of (category, name, block_str)
    all_epg_urls = []
    seen_channel_names = set()

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
        categorize = source.get("categorize", True)
        source_customs = custom_channels.get(source_id, [])

        if epg_url not in all_epg_urls:
            all_epg_urls.append(epg_url)

        logger.info("Processing source: %s (%s)", source_name, source_id)
        
        raw_content, used_url = fetch_upstream_content(session, source)
        
        final_content, channel_count, cat_counts, channel_items = standardize_playlist(
            raw_content=raw_content,
            epg_url=epg_url,
            custom_entries=source_customs,
            default_group=default_group,
            categorize=categorize
        )
        
        # Write individual playlist files (.m3u8 and .m3u)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        m3u_output_path = os.path.splitext(output_path)[0] + ".m3u"
        with open(m3u_output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        file_size_kb = os.path.getsize(output_path) / 1024
        logger.info("Wrote %s (and .m3u): %d channels (%.2f KB)", output_filename, channel_count, file_size_kb)

        all_combined_channels.extend(channel_items)

        manifest["playlists"].append({
            "id": source_id,
            "name": source_name,
            "file": output_filename,
            "file_m3u": os.path.splitext(output_filename)[0] + ".m3u",
            "channels_count": channel_count,
            "categories": cat_counts,
            "epg_url": epg_url,
            "upstream_url": used_url if used_url else source["url"],
            "status": "active" if channel_count > 0 else "empty"
        })

    # Add Nollywood custom list entries if configured
    nolly_customs = custom_channels.get("nollywood", [])
    if nolly_customs:
        logger.info("Processing dedicated Nollywood channels: %d entries", len(nolly_customs))
        for item in nolly_customs:
            block = format_custom_channel(item, "Nollywood & African TV")
            if block.strip():
                lines = block.splitlines()
                cat, name, formatted = process_channel_block(lines, True, "Nollywood & African TV")
                all_combined_channels.append((cat, name, formatted))

    # Process global custom sources if any
    global_customs = custom_channels.get("custom", [])
    if global_customs:
        logger.info("Processing global custom channels: %d entries", len(global_customs))
        for item in global_customs:
            block = format_custom_channel(item, "Custom")
            if block.strip():
                lines = block.splitlines()
                cat, name, formatted = process_channel_block(lines, True, "Custom")
                all_combined_channels.append((cat, name, formatted))

    # Build Master Combined Playlist (Categorized and Deduplicated)
    all_combined_channels.sort(key=lambda x: (CATEGORY_PRIORITY.get(x[0], 99), x[1].lower()))
    
    combined_epg_str = ",".join(all_epg_urls)
    combined_header = f'#EXTM3U url-tvg="{combined_epg_str}" x-tvg-url="{combined_epg_str}"'
    combined_output_lines = [combined_header, ""]
    for _, _, block in all_combined_channels:
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

    # Build Dedicated Nollywood & African TV Playlist
    nolly_channels = [ch for ch in all_combined_channels if ch[0] == "Nollywood & African TV"]
    # Deduplicate Nollywood channels by name
    unique_nolly = []
    seen_nolly = set()
    for cat, name, block in nolly_channels:
        key = name.lower()
        if key not in seen_nolly:
            seen_nolly.add(key)
            unique_nolly.append((cat, name, block))

    nolly_epg_str = "https://i.mjh.nz/DStv/za.xml.gz,https://i.mjh.nz/SamsungTVPlus/all.xml.gz,https://i.mjh.nz/all/epg.xml.gz"
    nolly_header = f'#EXTM3U url-tvg="{nolly_epg_str}" x-tvg-url="{nolly_epg_str}"'
    nolly_output_lines = [nolly_header, ""]
    for _, _, block in unique_nolly:
        nolly_output_lines.append(block)
        nolly_output_lines.append("")

    nolly_m3u8_path = os.path.join(PLAYLISTS_DIR, "nollywood.m3u8")
    with open(nolly_m3u8_path, "w", encoding="utf-8") as f:
        f.write("\n".join(nolly_output_lines).strip() + "\n")
    nolly_m3u_path = os.path.join(PLAYLISTS_DIR, "nollywood.m3u")
    with open(nolly_m3u_path, "w", encoding="utf-8") as f:
        f.write("\n".join(nolly_output_lines).strip() + "\n")
    logger.info("Wrote Dedicated Nollywood Playlist 'nollywood.m3u': %d channels", len(unique_nolly))

    manifest["playlists"].append({
        "id": "nollywood",
        "name": "Nollywood & African TV",
        "file": "nollywood.m3u8",
        "file_m3u": "nollywood.m3u",
        "channels_count": len(unique_nolly),
        "epg_url": nolly_epg_str,
        "status": "active"
    })

    # Build Curated Popular Favorites Playlist (Famous top channels across all genres)
    popular_channels = []
    seen_popular = set()
    for cat, name, block in all_combined_channels:
        if is_popular_channel(name) or cat == "Nollywood & African TV":
            key = name.lower()
            if key not in seen_popular:
                seen_popular.add(key)
                popular_channels.append((cat, name, block))

    popular_channels.sort(key=lambda x: (CATEGORY_PRIORITY.get(x[0], 99), x[1].lower()))
    popular_header = f'#EXTM3U url-tvg="{combined_epg_str}" x-tvg-url="{combined_epg_str}"'
    popular_output_lines = [popular_header, ""]
    for _, _, block in popular_channels:
        popular_output_lines.append(block)
        popular_output_lines.append("")

    popular_m3u8_path = os.path.join(PLAYLISTS_DIR, "popular_favorites.m3u8")
    with open(popular_m3u8_path, "w", encoding="utf-8") as f:
        f.write("\n".join(popular_output_lines).strip() + "\n")
    popular_m3u_path = os.path.join(PLAYLISTS_DIR, "popular_favorites.m3u")
    with open(popular_m3u_path, "w", encoding="utf-8") as f:
        f.write("\n".join(popular_output_lines).strip() + "\n")
    logger.info("Wrote Curated Popular Favorites Playlist 'popular_favorites.m3u': %d channels", len(popular_channels))

    manifest["playlists"].append({
        "id": "popular_favorites",
        "name": "Popular Favorites (Curated Best)",
        "file": "popular_favorites.m3u8",
        "file_m3u": "popular_favorites.m3u",
        "channels_count": len(popular_channels),
        "epg_url": combined_epg_str,
        "status": "active"
    })

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
    print("  ALL-REGION & POPULAR FAVORITES GENERATION SUMMARY")
    print("=" * 75)
    print(f"  {'Network / Playlist Name':<38} | {'Filename':<22} | {'Channels':<8}")
    print("  " + "-" * 75)
    for p in manifest["playlists"]:
        print(f"  {p['name']:<38} | {p['file_m3u']:<22} | {p['channels_count']:<8}")
    print("  " + "-" * 75)
    print(f"  {'* MASTER COMBINED (ALL REGIONS) *':<38} | {'all_combined.m3u':<22} | {len(all_combined_channels):<8}")
    print("=" * 75)

    print(f"Playlists successfully generated in: {PLAYLISTS_DIR}\n")


if __name__ == "__main__":
    generate_all()
