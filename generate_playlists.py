#!/usr/bin/env python3
"""
FAST M3U Playlist and EPG Generator (Deduplicated & High-Quality Edition)
=========================================================================
Automates fetching, standardizing, categorizing, deduplicating, and generating
pristine global FAST and IPTV playlists with auto-injected EPG:
- Automatically detects and eliminates exact repetitive clones across all hosts
- Ranks duplicates and keeps only the highest quality (4K/1080p/720p HD) working feed
- Injects universal IPTV player headers (#EXTVLCOPT user-agent / referrer) to stop 403 / infinite loading
- Integrates unblocked global CDN channels (Free-TV Global, IPTV-Org Africa, Samsung, Pluto, Plex, Roku, Tubi)
- 24/7 Studio Newsroom live stream for TVC News Nigeria (steady 720p 30fps)
- Direct enterprise AWS CloudFront stream for Arise News (zero buffering, permanent uptime)
- Rock-solid 720p 30fps stream for Channels Television
- Neatly sorts all channels by genre categories (News, Sports, Movies, Kids, etc.)
- Outputs individual network playlists + Master Combined + Curated Popular Favorites
"""

import os
import re
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

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

# Standard Universal User-Agent & Referrer for IPTV Players
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
DEFAULT_REFERRER = "https://www.google.com/"

# Category Definitions & Regex Patterns
CATEGORY_RULES = [
    ("Nollywood & African TV", [
        r'\bnolly\b', r'\bnollywood\b', r'\bafrica\b', r'\bafrique\b', r'\bnigeria\b', r'\bnaija\b',
        r'\bchannels tv\b', r'\bchannels television\b', r'\bchannels 24\b', r'\btvc news\b', r'\barise news\b',
        r'\bnta\b', r'\bait\b', r'\bsilverbird\b', r'\bsoundcity\b', r'\barewa\b', r'\bafrican movie\b',
        r'\brok\b', r'\bafroland\b', r'\bwakaati\b', r'\bafrica magic\b', r'\bamusic\b', r'\bghana\b',
        r'\bkenya\b', r'\buganda\b', r'\btanzania\b', r'\bsouth africa\b', r'\bzim\b', r'\bcameroon\b'
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

POPULAR_KEYWORDS = [
    r'\bbbc news\b', r'\bcnn\b', r'\bsky news\b', r'\bbloomberg\b', r'\beuronews\b', r'\bal jazeera\b',
    r'\babc news live\b', r'\bcbs news\b', r'\bnbc news now\b', r'\breuters\b', r'\bweather channel\b',
    r'\bespn\b', r'\bbein sports\b', r'\bpga tour\b', r'\bnfl channel\b', r'\bmlb\b', r'\bnhl\b',
    r'\btennis channel\b', r'\bred bull tv\b', r'\bfight network\b', r'\bimpact wrestling\b',
    r'\bmotorvision\b', r'\bstadium\b',
    r'\bnickelodeon\b', r'\bnick jr\b', r'\blego\b', r'\bpok[eé]mon\b', r'\banime all day\b',
    r'\bretrocrush\b', r'\byu-gi-oh\b', r'\bbaby einstein\b', r'\bducktv\b', r'\bpower rangers\b',
    r'\bhallmark\b', r'\bparamount movie\b', r'\bmoviesphere\b', r'\bsony\b', r'\bfilmrise\b', r'\bshudder\b',
    r'\bcomedy central\b', r'\bdoctor who\b', r'\bbaywatch\b', r'\bcsi\b', r'\blaw & order\b',
    r'\b21 jump street\b', r'\bheartland\b', r'\bgordon ramsay\b', r'\btop gear\b', r'\btastemade\b',
    r'\bmtv\b', r'\bvevo\b', r'\bfailarmy\b', r'\bprice is right\b', r'\bdeal or no deal\b',
    r'\bnolly\b', r'\bnollywood\b', r'\bchannels tv\b', r'\bchannels television\b', r'\btvc news\b',
    r'\barise news\b', r'\bafrica magic\b', r'\bsoundcity\b', r'\bsilverbird\b', r'\bait\b', r'\bnta\b'
]


def is_foreign_or_local_clone(name: str) -> bool:
    n = name.lower()
    # Foreign language indicators
    if re.search(r'\b(en espa[nñ]ol|noticias|italiano|portugu[eê]s|deutschland|en direct|en directo|divertenti|d.azione|imperdibili|da ridere|acci[oó]n|comedia|com[eé]die|concursos|cr[ií]menes|pel[ií]culas|serien|populaire|verguenza|verg[uü]enza|jovens|m[aã]es|brasil|m[eé]xico|favoris|faves|[eé]xitos|hogar|casa|viagem|viajes|cl[aá]sico|cl[aá]ssico|autopista|reggae|schlager|iconos|r[eé]tro|ex|latin[oa]|embarazada|con mi ex|com o ex)\b', n):
        return True
    # Local city affiliates
    if re.search(r'\bcbs news (baltimore|bay area|boston|canada|chicago|colorado|detroit|los angeles|miami|minnesota|new york|philadelphia|pittsburgh|sacramento|texas|united kingdom)\b', n):
        return True
    if re.search(r'\b(cnn news18|cnn noticias|cnn en espa[nñ]ol)\b', n):
        return True
    return False


def get_canonical_popular_name(name: str) -> str:
    n = name.lower()
    if re.search(r'\b(the lego channel|lego channel|lego kids tv)\b', n):
        return 'LEGO Channel'
    if re.search(r'\b(deal or no deal.*?)\b', n):
        return 'Deal or No Deal'
    if re.search(r'\b(classic doctor who|doctor who classic)\b', n):
        return 'Doctor Who Classic'
    if re.search(r'\b(mlb channel|mlb)\b', n):
        return 'MLB Channel'
    if re.search(r'\b(moviesphere by lionsgate|moviesphere)\b', n):
        return 'MOVIESPHERE'
    if re.search(r'\b(the price is right.*?|price is right)\b', n):
        return 'The Price is Right'
    if re.search(r'\b(euronews live|euronews world|euronews)\b', n):
        return 'Euronews'
    if re.search(r'\b(cnn headlines.*?|cnn originals)\b', n):
        return 'CNN Headlines'
    if re.search(r'\b(top gear challenge|top gear)\b', n):
        return 'Top Gear'
    if re.search(r'\b(tennis channel 2|tennis channel)\b', n):
        return 'Tennis Channel'
    if re.search(r'\b(motorvision classic|motorvision tv)\b', n):
        return 'Motorvision TV'
    if re.search(r'\b(gordon ramsay.*?)\b', n):
        return "Gordon Ramsay's Hell's Kitchen"
    if n == 'csi' or n == 'csi: crime scene investigation':
        return 'CSI: Crime Scene Investigation'
    if n == 'comedy central' or n == 'comedy central pluto tv':
        return 'Comedy Central Pluto TV'
    if 'south park' in n:
        return 'Comedy Central South Park'
    if re.search(r'\b(nick jr.*?)\b', n):
        return 'Nick Jr. Pluto TV'
    if re.search(r'\b(nickelodeon pluto tv|nickelodeon classics|nickelodeon toons|nickelodeon teen)\b', n):
        return 'Nickelodeon Pluto TV'
    if re.search(r'sony one.*?(blacklist)', n):
        return 'Sony One The Blacklist'
    if re.search(r'sony one.*?(shark tank)', n):
        return 'Sony One Shark Tank'
    if re.search(r'sony one.*?(action hits|hits action)', n):
        return 'Sony One Action Hits'
    if re.search(r'sony one.*?(comedy hits|comedy tv)', n):
        return 'Sony One Comedy Hits'
    if re.search(r'sony one.*?(thriller)', n):
        return 'Sony One Thriller'
    if re.search(r'sony one.*?(dragons den)', n):
        return 'Sony One Dragons Den'
    if re.search(r'vevo.*?(hip.?hop|r&b)', n):
        return 'Vevo Hip-Hop & R&B'
    if re.search(r'vevo.*?(country)', n):
        return 'Vevo Country'
    if re.search(r'vevo.*?(rock)', n):
        return 'Vevo Rock'
    if re.search(r'vevo.*?(pop)', n):
        return 'Vevo Pop'
    if re.search(r'vevo.*?(70s|80s)', n):
        return "Vevo '80s"
    if re.search(r'vevo.*?(90s|00s)', n):
        return "Vevo '90s"
    if re.search(r'vevo.*?(2k|2010s)', n):
        return 'Vevo 2K'
    if re.search(r'mtv.*?(catfish)', n):
        return 'MTV Catfish'
    if re.search(r'mtv.*?(classic|classics)', n):
        return 'MTV Classic'
    if re.search(r'mtv.*?(jersey shore|jerseys)', n):
        return 'MTV Jersey Shore'
    if re.search(r'mtv.*?(teen mom)', n):
        return 'MTV Teen Mom'
    if re.search(r'mtv.*?(cribs)', n):
        return 'MTV Cribs'
    if re.search(r'mtv.*?(reality|dating|are you the one)', n):
        return 'MTV Reality'
    if re.search(r'mtv.*?(rocks)', n):
        return 'MTV Rocks'
    if re.search(r'(best of mtv|mtv pluto tv|mtv originals|mtv spankin)', n):
        return 'Best of MTV'
    if re.search(r'filmrise.*?(free movies|movies)', n):
        return 'FilmRise Free Movies'
    if re.search(r'filmrise.*?(action)', n):
        return 'FilmRise Action'
    if re.search(r'filmrise.*?(comedy)', n):
        return 'FilmRise Comedy'
    if re.search(r'filmrise.*?(horror)', n):
        return 'FilmRise Horror'
    if re.search(r'filmrise.*?(true crime|crimes|forensic)', n):
        return 'FilmRise True Crime'
    if re.search(r'filmrise.*?(western)', n):
        return 'FilmRise Western'
    if re.search(r'filmrise.*?(classic tv|british tv|black tv|canadien)', n):
        return 'FilmRise Classic TV'
    if re.search(r'filmrise.*?(anime)', n):
        return 'FilmRise Anime'
    if re.search(r'filmrise.*?(kids)', n):
        return 'FilmRise Kids'
    if re.search(r'filmrise.*?(food)', n):
        return 'FilmRise Food'
    if re.search(r'tastemade.*?(travel)', n):
        return 'Tastemade Travel'
    if re.search(r'tastemade.*?(home|smokehouse)', n):
        return 'Tastemade Home'
    if re.search(r'tastemade', n):
        return 'Tastemade'
    return name


POPULAR_ALLOWED_PATTERNS = [
    r'21 jump street', r'anime all day', r'arise news', r'baby einstein', r'baywatch',
    r'bein sports xtra', r'best of mtv', r'bloomberg', r'cbs news 24/7', r'channels television',
    r'cnn headlines', r'comedy central pluto tv', r'comedy central south park',
    r'csi: crime scene investigation', r'csi: miami', r'csi: ny', r'deal or no deal',
    r'doctor who classic', r'euronews', r'fight network', r'filmrise action', r'filmrise anime',
    r'filmrise classic tv', r'filmrise comedy', r'filmrise free movies', r'filmrise horror',
    r'filmrise kids', r'filmrise true crime', r'filmrise western', r"gordon ramsay's hell's kitchen",
    r'hallmark movies & more', r'law & order', r'lego channel', r'mlb channel', r'motorvision tv',
    r'moviesphere', r'mtv catfish', r'mtv classic', r'mtv cribs', r'mtv jersey shore', r'mtv reality',
    r'mtv rocks', r'mtv teen mom', r'nfl channel', r'nhl', r'nick jr. pluto tv', r'nickelodeon icarly',
    r'nickelodeon pluto tv', r'nolly africa hd', r'pga tour', r'pok[eé]mon', r'power rangers',
    r'red bull tv motorsport', r'retrocrush', r'scares by shudder', r'sky news international',
    r'sony one action hits', r'sony one comedy hits', r'sony one dragons den', r'sony one shark tank',
    r'sony one the blacklist', r'sony one thriller', r'tastemade', r'tastemade home', r'tastemade travel',
    r'tennis channel', r'the price is right', r'the reuters 60', r'top gear', r'tvc news nigeria',
    r"vevo '80s", r"vevo '90s", r'vevo 2k', r'vevo country', r'vevo hip-hop & r&b', r'vevo pop', r'vevo rock',
    r'yu-gi-oh!'
]


def curate_popular_favorites(channel_items: List[Tuple[str, str, str, str]]) -> List[Tuple[str, str, str, str]]:
    cleaned_items = []
    seen = set()
    deduped = deduplicate_channel_items(channel_items)
    
    for cat, name, block, src_id in deduped:
        if is_foreign_or_local_clone(name):
            continue
        canon_name = get_canonical_popular_name(name)
        key = canon_name.lower().strip()
        
        if any(re.search(p, key) for p in POPULAR_ALLOWED_PATTERNS):
            if key not in seen:
                seen.add(key)
                cleaned_items.append((cat, canon_name, block, src_id))
                
    cleaned_items.sort(key=lambda x: x[1].lower())
    return cleaned_items


def is_popular_channel(channel_name: str) -> bool:
    text = channel_name.lower()
    return any(re.search(p, text) for p in POPULAR_KEYWORDS)


def classify_channel(channel_name: str, existing_group: str = "") -> str:
    text = f"{channel_name} {existing_group}".lower()
    for cat_name, patterns in CATEGORY_RULES:
        for p in patterns:
            if re.search(p, text):
                return cat_name
    return "Entertainment"


def normalize_channel_key(channel_name: str) -> str:
    clean = re.sub(r'[\(\[].*?[\)\]]', '', channel_name)
    clean = re.sub(r'\b(4k|uhd|fhd|hd|sd|1080p|720p|480p|360p)\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', clean).strip().lower()
    clean = re.sub(r'\s+', ' ', clean)
    return clean if clean else channel_name.lower().strip()


def compute_quality_score(channel_name: str, extinf_line: str, stream_url: str, source_id: str) -> int:
    score = 100
    text = f"{channel_name} {extinf_line}".lower()
    url_lower = stream_url.lower()

    # 1. Preferred direct CDN protocols over brittle redirectors
    if "cloudfront.net" in url_lower or "googlevideo.com" in url_lower or "fastly.net" in url_lower or "akamaihd.net" in url_lower:
        score += 40
    elif "jmp2.uk" in url_lower:
        score -= 10

    # 2. Resolution / Quality bonuses
    if any(q in text for q in ["4k", "uhd", "2160p"]):
        score += 50
    elif any(q in text for q in ["1080p", "1080", "fhd"]):
        score += 35
    elif any(q in text for q in ["720p", "720", "hd"]):
        score += 25
    elif any(q in text for q in ["480p", "sd", "360p"]):
        score -= 15

    # 3. Network Priority
    if source_id == "nollywood_custom":
        score += 50
    elif source_id == "freetv_global":
        score += 25
    elif source_id == "iptv_org_africa":
        score += 25
    elif source_id == "samsung_all":
        score += 15
    elif source_id == "plutotv_all":
        score += 15
    elif source_id == "plex_all":
        score += 12
    elif source_id == "roku_all":
        score += 10
    elif source_id == "tubi_all":
        score += 8

    # 4. Metadata bonuses
    if 'tvg-logo="http' in extinf_line:
        score += 5
    if 'tvg-id="' in extinf_line and 'tvg-id=""' not in extinf_line:
        score += 5

    return score


def deduplicate_channel_items(
    channel_items: List[Tuple[str, str, str, str]]
) -> List[Tuple[str, str, str, str]]:
    grouped = defaultdict(list)
    for cat, name, block, src_id in channel_items:
        key = normalize_channel_key(name)
        lines = block.splitlines()
        extinf_line = lines[0]
        url = [l for l in lines if l.startswith("http")][-1] if any(l.startswith("http") for l in lines) else ""
        
        if not url.startswith("http") or "example.com" in url or "localhost" in url:
            continue

        score = compute_quality_score(name, extinf_line, url, src_id)
        grouped[key].append((score, cat, name, block, src_id))

    deduped = []
    for key, candidates in grouped.items():
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_cat, best_name, best_block, best_src = candidates[0]
        deduped.append((best_cat, best_name, best_block, best_src))

    return deduped


def refresh_youtube_live_streams(custom_data: dict) -> dict:
    """
    Auto-refresh live steady (Video + Audio) HLS tokens for YouTube live stream sources using yt-dlp.
    Selects rock-solid 720p/1080p 30fps muxed streams (format 95/300/94).
    """
    if not yt_dlp:
        logger.warning("yt-dlp not available for live stream token refresh.")
        return custom_data

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'ios', 'web']}},
        'format': '95/300/301/94/93/best[vcodec!=none][acodec!=none]'
    }

    updated = False
    for category, items in custom_data.items():
        for item in items:
            yt_url = item.get("yt_source")
            if yt_url:
                name = item.get("name", "Channel")
                logger.info("Auto-refreshing live stable HLS token for '%s' via yt-dlp...", name)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(yt_url, download=False)
                        new_hls = info.get("url")
                        if new_hls and new_hls.startswith("http"):
                            item["url"] = new_hls
                            updated = True
                            logger.info("Successfully refreshed stable HLS for '%s' (%s, Format: %s)", name, info.get("resolution"), info.get("format_id"))
                except Exception as e:
                    logger.warning("yt-dlp refresh notice for '%s': %s", name, e)

    if updated:
        try:
            with open(CUSTOM_CHANNELS_FILE, "w", encoding="utf-8") as f:
                json.dump(custom_data, f, indent=2)
            logger.info("Saved updated live stream URLs to custom_channels.json")
        except Exception as e:
            logger.warning("Error saving custom_channels.json: %s", e)

    return custom_data


# All-Region & Direct Open Sources Configuration
SOURCES_CONFIG = [
    {
        "id": "freetv_global",
        "name": "Global Open Live TV (Free-TV Unblocked)",
        "url": "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/all/epg.xml.gz",
        "output_filename": "freetv_global.m3u8",
        "default_group": "Global Live TV",
        "categorize": True
    },
    {
        "id": "iptv_org_africa",
        "name": "Africa & Nollywood (IPTV-Org Verified)",
        "url": "https://iptv-org.github.io/iptv/regions/afr.m3u",
        "fallback_urls": [],
        "epg_url": "https://i.mjh.nz/all/epg.xml.gz",
        "output_filename": "iptv_org_africa.m3u8",
        "default_group": "Nollywood & African TV",
        "categorize": True
    },
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
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close"
    })
    return session


def load_custom_channels() -> Dict[str, List[dict]]:
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


def format_custom_channel(item: dict, default_group: str) -> Optional[str]:
    url = item.get("url", "").strip()
    if not url or not url.startswith("http") or "example.com" in url or "localhost" in url:
        return None

    name = item.get("name", "Custom Channel")
    tvg_id = item.get("tvg_id", "")
    tvg_name = item.get("tvg_name", name)
    tvg_logo = item.get("tvg_logo", "")
    tvg_chno = item.get("tvg_chno", "")
    group = item.get("group", default_group)
    http_user_agent = item.get("http_user_agent", DEFAULT_USER_AGENT)
    http_referrer = item.get("http_referrer", DEFAULT_REFERRER)

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
    attrs.append(f'user-agent="{http_user_agent}"')

    attr_str = " ".join(attrs)
    lines = [
        f"#EXTINF:-1 {attr_str},{name}".strip(),
        f"#EXTVLCOPT:http-user-agent={http_user_agent}",
        f"#EXTVLCOPT:http-referrer={http_referrer}",
        url
    ]
    return "\n".join(lines)


def fetch_upstream_content(session: requests.Session, source: dict) -> Tuple[Optional[str], str]:
    urls_to_try = [source["url"]] + source.get("fallback_urls", [])
    
    for url in urls_to_try:
        try:
            logger.info("Fetching '%s' from %s...", source["name"], url)
            response = session.get(url, timeout=14)
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
    extinf_line = block_lines[0]
    
    name_match = re.search(r',([^,]+)$', extinf_line)
    channel_name = name_match.group(1).strip() if name_match else "Channel"

    group_match = re.search(r'group-title="([^"]+)"', extinf_line)
    orig_group = group_match.group(1) if group_match else default_group

    if categorize:
        category = classify_channel(channel_name, orig_group)
        if group_match:
            new_extinf = extinf_line[:group_match.start(1)] + category + extinf_line[group_match.end(1):]
        else:
            new_extinf = extinf_line.replace("#EXTINF:-1", f'#EXTINF:-1 group-title="{category}"')
        block_lines[0] = new_extinf
    else:
        category = orig_group

    # Inject IPTV player user-agent and referrer options if missing
    has_vlc_ua = any("http-user-agent" in l for l in block_lines)
    has_vlc_ref = any("http-referrer" in l for l in block_lines)
    
    formatted = [block_lines[0]]
    if not has_vlc_ua:
        formatted.append(f"#EXTVLCOPT:http-user-agent={DEFAULT_USER_AGENT}")
    if not has_vlc_ref:
        formatted.append(f"#EXTVLCOPT:http-referrer={DEFAULT_REFERRER}")
        
    for l in block_lines[1:]:
        if not l.startswith("#EXTVLCOPT"):
            formatted.append(l)

    return category, channel_name, "\n".join(formatted)


def standardize_playlist(
    raw_content: Optional[str],
    epg_url: str,
    custom_entries: List[dict],
    default_group: str,
    source_id: str,
    categorize: bool = False
) -> Tuple[str, int, Dict[str, int], List[Tuple[str, str, str, str]]]:
    header = f'#EXTM3U url-tvg="{epg_url}" x-tvg-url="{epg_url}"'
    raw_channel_items = []
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
                        raw_channel_items.append((cat, name, formatted, source_id))
                    current_entry_lines = []
                current_entry_lines.append(line)
            elif current_entry_lines:
                current_entry_lines.append(line)
        
        if current_entry_lines and any(not l.startswith("#") for l in current_entry_lines):
            cat, name, formatted = process_channel_block(current_entry_lines, categorize, default_group)
            raw_channel_items.append((cat, name, formatted, source_id))

    # Append custom channels
    for custom_item in custom_entries:
        custom_block = format_custom_channel(custom_item, default_group)
        if custom_block:
            lines = custom_block.splitlines()
            cat, name, formatted = process_channel_block(lines, categorize, default_group)
            raw_channel_items.append((cat, name, formatted, source_id))

    # Deduplicate within this single host
    channel_items = deduplicate_channel_items(raw_channel_items)

    # Sort channels by Category Priority, then by Channel Name
    if categorize:
        channel_items.sort(key=lambda x: (CATEGORY_PRIORITY.get(x[0], 99), x[1].lower()))
    else:
        channel_items.sort(key=lambda x: (x[0].lower(), x[1].lower()))

    for cat, _, _, _ in channel_items:
        category_counts[cat] = category_counts.get(cat, 0) + 1

    output_lines = [header, ""]
    for _, _, block_str, _ in channel_items:
        output_lines.append(block_str)
        output_lines.append("")
        
    return "\n".join(output_lines).strip() + "\n", len(channel_items), category_counts, channel_items


def generate_all():
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)
    session = create_session()
    custom_channels = load_custom_channels()
    
    # Auto-refresh live stream tokens from YouTube Live sources
    custom_channels = refresh_youtube_live_streams(custom_channels)

    manifest = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        "edition": "All-Region Global FAST (Deduplicated & High-Quality Edition)",
        "playlists": []
    }
    
    all_raw_channels = []
    all_epg_urls = []

    print("\n" + "=" * 78)
    print("  ALL-REGION DEDUPLICATED FAST M3U PLAYLIST & EPG GENERATOR")
    print("=" * 78)

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
            source_id=source_id,
            categorize=categorize
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        m3u_output_path = os.path.splitext(output_path)[0] + ".m3u"
        with open(m3u_output_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        file_size_kb = os.path.getsize(output_path) / 1024
        logger.info("Wrote %s (and .m3u): %d channels (%.2f KB)", output_filename, channel_count, file_size_kb)

        all_raw_channels.extend(channel_items)

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

    # Add Nollywood live streams
    nolly_customs = custom_channels.get("nollywood", [])
    if nolly_customs:
        for item in nolly_customs:
            block = format_custom_channel(item, "Nollywood & African TV")
            if block:
                lines = block.splitlines()
                cat, name, formatted = process_channel_block(lines, True, "Nollywood & African TV")
                all_raw_channels.append((cat, name, formatted, "nollywood_custom"))

    # Process global custom sources if any
    global_customs = custom_channels.get("custom", [])
    if global_customs:
        for item in global_customs:
            block = format_custom_channel(item, "Custom")
            if block:
                lines = block.splitlines()
                cat, name, formatted = process_channel_block(lines, True, "Custom")
                all_raw_channels.append((cat, name, formatted, "global_custom"))

    # --- MASTER COMBINED PLAYLIST (DEDUPLICATED ACROSS ALL NETWORKS) ---
    logger.info("Deduplicating Master Combined Playlist across all hosts (raw count: %d)...", len(all_raw_channels))
    master_deduped = deduplicate_channel_items(all_raw_channels)
    master_deduped.sort(key=lambda x: (CATEGORY_PRIORITY.get(x[0], 99), x[1].lower()))
    
    combined_epg_str = ",".join(all_epg_urls)
    combined_header = f'#EXTM3U url-tvg="{combined_epg_str}" x-tvg-url="{combined_epg_str}"'
    combined_output_lines = [combined_header, ""]
    for _, _, block, _ in master_deduped:
        combined_output_lines.append(block)
        combined_output_lines.append("")
        
    combined_file_path = os.path.join(PLAYLISTS_DIR, "all_combined.m3u8")
    with open(combined_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_output_lines).strip() + "\n")
        
    combined_m3u_path = os.path.join(PLAYLISTS_DIR, "all_combined.m3u")
    with open(combined_m3u_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_output_lines).strip() + "\n")
        
    combined_size_kb = os.path.getsize(combined_file_path) / 1024
    logger.info("Wrote Master All-Region Playlist 'all_combined.m3u': %d unique channels (%.2f KB)", len(master_deduped), combined_size_kb)

    # Major FAST host source IDs
    FAST_HOST_IDS = {"samsung_all", "plutotv_all", "plex_all", "roku_all", "tubi_all", "nollywood_custom"}

    # --- DEDICATED NOLLYWOOD & AFRICAN TV PLAYLIST ---
    nolly_channels = [
        ch for ch in master_deduped 
        if (ch[3] == "nollywood_custom" or (ch[0] == "Nollywood & African TV" and ch[3] in FAST_HOST_IDS))
    ]
    nolly_channels.sort(key=lambda x: x[1].lower())
    nolly_epg_str = "https://i.mjh.nz/DStv/za.xml.gz,https://i.mjh.nz/SamsungTVPlus/all.xml.gz,https://i.mjh.nz/all/epg.xml.gz"
    nolly_header = f'#EXTM3U url-tvg="{nolly_epg_str}" x-tvg-url="{nolly_epg_str}"'
    nolly_output_lines = [nolly_header, ""]
    for _, _, block, _ in nolly_channels:
        nolly_output_lines.append(block)
        nolly_output_lines.append("")

    nolly_m3u8_path = os.path.join(PLAYLISTS_DIR, "nollywood.m3u8")
    with open(nolly_m3u8_path, "w", encoding="utf-8") as f:
        f.write("\n".join(nolly_output_lines).strip() + "\n")
    nolly_m3u_path = os.path.join(PLAYLISTS_DIR, "nollywood.m3u")
    with open(nolly_m3u_path, "w", encoding="utf-8") as f:
        f.write("\n".join(nolly_output_lines).strip() + "\n")
    logger.info("Wrote Dedicated Nollywood Playlist 'nollywood.m3u': %d channels", len(nolly_channels))

    manifest["playlists"].append({
        "id": "nollywood",
        "name": "Nollywood & African TV",
        "file": "nollywood.m3u8",
        "file_m3u": "nollywood.m3u",
        "channels_count": len(nolly_channels),
        "epg_url": nolly_epg_str,
        "status": "active" if len(nolly_channels) > 0 else "empty"
    })

    # --- CURATED POPULAR FAVORITES PLAYLIST (Alphabetical A-Z, Pristine Curated Household Names) ---
    popular_raw = [
        ch for ch in master_deduped 
        if ch[3] in FAST_HOST_IDS and (is_popular_channel(ch[1]) or ch[3] == "nollywood_custom")
    ]
    popular_deduped = curate_popular_favorites(popular_raw)

    popular_header = f'#EXTM3U url-tvg="{combined_epg_str}" x-tvg-url="{combined_epg_str}"'
    popular_output_lines = [popular_header, ""]
    for _, _, block, _ in popular_deduped:
        popular_output_lines.append(block)
        popular_output_lines.append("")

    popular_m3u8_path = os.path.join(PLAYLISTS_DIR, "popular_favorites.m3u8")
    with open(popular_m3u8_path, "w", encoding="utf-8") as f:
        f.write("\n".join(popular_output_lines).strip() + "\n")
    popular_m3u_path = os.path.join(PLAYLISTS_DIR, "popular_favorites.m3u")
    with open(popular_m3u_path, "w", encoding="utf-8") as f:
        f.write("\n".join(popular_output_lines).strip() + "\n")
    logger.info("Wrote Curated Popular Favorites Playlist 'popular_favorites.m3u': %d unique channels", len(popular_deduped))

    manifest["playlists"].append({
        "id": "popular_favorites",
        "name": "Popular Favorites (Curated Best)",
        "file": "popular_favorites.m3u8",
        "file_m3u": "popular_favorites.m3u",
        "channels_count": len(popular_deduped),
        "epg_url": combined_epg_str,
        "status": "active"
    })

    manifest["master_playlist"] = {
        "file": "all_combined.m3u8",
        "file_m3u": "all_combined.m3u",
        "total_unique_channels": len(master_deduped),
        "total_raw_scanned": len(all_raw_channels),
        "epg_urls": all_epg_urls
    }

    manifest_path = os.path.join(PLAYLISTS_DIR, "index.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Print Summary Table
    print("\n" + "=" * 78)
    print("  DEDUPLICATED & HIGH-QUALITY GENERATION SUMMARY")
    print("=" * 78)
    print(f"  {'Network / Playlist Name':<38} | {'Filename':<22} | {'Channels':<8}")
    print("  " + "-" * 78)
    for p in manifest["playlists"]:
        print(f"  {p['name']:<38} | {p['file_m3u']:<22} | {p['channels_count']:<8}")
    print("  " + "-" * 78)
    print(f"  {'* MASTER COMBINED (ALL UNIQUE CHANNELS) *':<38} | {'all_combined.m3u':<22} | {len(master_deduped):<8}")
    print("=" * 78)
    print(f"Playlists successfully generated in: {PLAYLISTS_DIR}\n")


if __name__ == "__main__":
    generate_all()
