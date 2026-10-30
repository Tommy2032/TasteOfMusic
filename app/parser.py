import re
import json
import logging
import urllib.parse
import urllib.request
import unicodedata
import socket
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Force IPv4 resolution to prevent IPv6 handshake timeouts on Windows/VPN environments
orig_getaddrinfo = socket.getaddrinfo
def force_ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = force_ipv4_getaddrinfo

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
}

def fix_mojibake(text: str) -> str:
    """Fix Russian strings mistakenly double-encoded or decoded as Latin-1/Windows-1252."""
    if not text or not isinstance(text, str):
        return text
    if any(marker in text for marker in ('Ð', 'Ñ', 'Ã', 'â\x80\x94', 'â\x80\x93')):
        try:
            return text.encode('latin1').decode('utf-8')
        except Exception:
            pass
    return text

def normalize_text(text: str) -> str:
    """Normalize text for fuzzy matching."""
    if not text:
        return ""
    text = fix_mojibake(text)
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text)
    # Remove contents of parentheses like (Remastered 2021), [Deluxe], (feat. ...)
    text = re.sub(r'[\(\[\{].*?[\)\]\}]', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_yandex_url(url: str) -> Dict[str, Any]:
    """Parse various Yandex Music URL structures."""
    cleaned_url = url.strip()
    parsed = urllib.parse.urlparse(cleaned_url)
    path = parsed.path.strip('/')
    parts = path.split('/')
    
    info = {
        'type': 'unknown',
        'raw_url': cleaned_url,
        'uuid': None,
        'user': None,
        'kind': None,
        'album_id': None,
    }
    
    # Format: playlists/lk.0ce106d6-e6c0-4dd0-8173-3dba3e82cad6 or playlists/{uuid}
    if len(parts) >= 2 and parts[0] == 'playlists':
        info['type'] = 'playlist_uuid'
        info['uuid'] = parts[1]
        return info
        
    # Format: users/{user}/playlists/{kind}
    if len(parts) >= 4 and parts[0] == 'users' and parts[2] == 'playlists':
        info['type'] = 'user_playlist'
        info['user'] = parts[1]
        info['kind'] = parts[3]
        return info

    # Format: album/{album_id}
    if len(parts) >= 2 and parts[0] == 'album':
        info['type'] = 'album'
        info['album_id'] = parts[1]
        return info
        
    return info

def fetch_html_with_retry(url: str, max_retries: int = 3, timeout: int = 6) -> str:
    """Fetch HTML content with automatic retries and standard headers."""
    req = urllib.request.Request(url, headers=HEADERS)
    last_err = None
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            last_err = e
            time.sleep(0.5)
    raise RuntimeError(f"Не удалось подключиться к странице плейлиста после {max_retries} попыток: {last_err}")

def enrich_tracks_metadata(tracks: List[Dict[str, Any]], max_to_enrich: int = 150) -> List[Dict[str, Any]]:
    """Enrich tracks lacking metadata by querying api.music.yandex.net/tracks in batches."""
    needed = [t for t in tracks if not t.get('title') or str(t.get('title', '')).startswith('Трек #') or t.get('artist') == 'Яндекс Музыка']
    if not needed:
        return tracks

    # Collect unique track IDs
    track_ids = []
    seen = set()
    for t in needed[:max_to_enrich]:
        tid = str(t.get('id', ''))
        if tid and not tid.startswith('custom_') and tid not in seen:
            seen.add(tid)
            track_ids.append(tid)

    if not track_ids:
        return tracks

    enriched_map = {}
    chunk_size = 50

    for i in range(0, len(track_ids), chunk_size):
        chunk = track_ids[i:i+chunk_size]
        url = f"https://api.music.yandex.net/tracks?track-ids={','.join(chunk)}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': HEADERS['User-Agent'],
                'Accept': 'application/json',
                'Accept-Language': 'ru-RU,ru;q=0.9',
            }
        )
        
        # Retry up to 3 times per chunk
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    for tr in data.get('result', []):
                        tid = str(tr.get('id'))
                        artists_list = [fix_mojibake(a.get('name')) for a in tr.get('artists', []) if a.get('name')]
                        artists_str = ", ".join(artists_list) if artists_list else "Неизвестный исполнитель"
                        albums = tr.get('albums', [])
                        album_title = fix_mojibake(albums[0].get('title', '')) if albums and isinstance(albums[0], dict) else ''
                        dur_ms = tr.get('durationMs', 0)
                        cover_uri = tr.get('coverUri', '')
                        cover_url = f"https://{cover_uri.replace('%%', '200x200')}" if cover_uri else ""
                        
                        enriched_map[tid] = {
                            'title': fix_mojibake(tr.get('title', f"Трек #{tid}")),
                            'artists': artists_list or [artists_str],
                            'artist': artists_str,
                            'album': album_title,
                            'duration_ms': dur_ms,
                            'duration_sec': dur_ms // 1000 if dur_ms else 0,
                            'cover': cover_url,
                            'url': f"https://music.yandex.ru/track/{tid}"
                        }
                    break
            except Exception as e:
                logger.warning(f"Track enrichment chunk attempt {attempt+1} failed: {e}")
                time.sleep(0.5)

    # Update tracks in-place
    for t in tracks:
        tid = str(t.get('id', ''))
        if tid in enriched_map:
            t.update(enriched_map[tid])

    return tracks

def extract_tracks_from_html(html: str, target_url: str = "") -> Dict[str, Any]:
    """Extract playlist info and tracks from Yandex Music Next.js HTML page."""
    playlist_info = {
        'title': 'Плейлист Яндекс Музыки',
        'owner': '',
        'track_count': 0,
        'cover': '',
        'url': target_url,
        'tracks': []
    }
    
    # 1. Look for <title> tag
    title_m = re.search(r'<title>(.*?)</title>', html)
    if title_m:
        raw_title = title_m.group(1).replace('&quot;', '"').replace('&amp;', '&')
        clean_title = re.sub(r'\s*—\s*слушать.*$', '', raw_title)
        clean_title = re.sub(r'^Плейлист\s*', '', clean_title).strip()
        if clean_title:
            playlist_info['title'] = fix_mojibake(clean_title)

    # 2. Extract resolved tracks from window.__STATE_PATCHES__
    resolved_tracks_map: Dict[str, Dict[str, Any]] = {}
    patch_blocks = re.findall(r'window\.__STATE_PATCHES__\s*=\s*window\.__STATE_PATCHES__\s*\|\|\s*\[\]\)\.push\((\[.*?\])\);', html)
    for block in patch_blocks:
        try:
            patches = json.loads(block)
            for p in patches:
                val = p.get('value')
                if isinstance(val, dict):
                    data = val.get('data')
                    if isinstance(data, dict) and data.get('title'):
                        t_id = str(data.get('id') or val.get('id'))
                        title = fix_mojibake(data.get('title'))
                        artists_list = [fix_mojibake(a.get('name')) for a in data.get('artists', []) if isinstance(a, dict) and a.get('name')]
                        artists_str = ", ".join(artists_list) if artists_list else "Неизвестный исполнитель"
                        albums = data.get('albums', [])
                        album_title = fix_mojibake(albums[0].get('title', '')) if albums and isinstance(albums[0], dict) else ''
                        duration_ms = data.get('durationMs', 0)
                        cover_uri = data.get('coverUri', '')
                        cover_url = f"https://{cover_uri.replace('%%', '200x200')}" if cover_uri else ""
                        
                        resolved_tracks_map[t_id] = {
                            'id': t_id,
                            'title': title,
                            'artists': artists_list or [artists_str],
                            'artist': artists_str,
                            'album': album_title,
                            'duration_ms': duration_ms,
                            'duration_sec': duration_ms // 1000 if duration_ms else 0,
                            'cover': cover_url,
                            'url': f"https://music.yandex.ru/track/{t_id}"
                        }
        except Exception:
            pass

    # 3. Extract preloaded playlist data from Next.js server payload (without bytes.decode('unicode_escape')!)
    tracks_list: List[Dict[str, Any]] = []
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        if 'preloadedPlaylistByUuid' in s or 'trackCount' in s:
            m = re.search(r'self\.__next_f\.push\(\[1,\s*"(.*)"\s*\]\)', s, re.DOTALL)
            if m:
                try:
                    raw_content = m.group(1)
                    # Safe unescape: decode \uXXXX without double-decoding or corrupting UTF-8 characters
                    clean_content = re.sub(r'\\u([0-9a-fA-F]{4})', lambda x: chr(int(x.group(1), 16)), raw_content)
                    clean_content = clean_content.replace(r'\"', '"').replace(r'\/', '/').replace(r'\\', '\\')
                    
                    idx = clean_content.find('{"preloadedPlaylistByUuid"')
                    if idx == -1:
                        idx = clean_content.find('"preloadedPlaylistByUuid":')
                        if idx != -1:
                            idx = clean_content.rfind('{', 0, idx)
                            
                    if idx != -1:
                        decoder = json.JSONDecoder()
                        obj, _ = decoder.raw_decode(clean_content[idx:])
                        
                        def find_pl(node):
                            if isinstance(node, dict):
                                if 'preloadedPlaylistByUuid' in node:
                                    return node['preloadedPlaylistByUuid']
                                for v in node.values():
                                    res = find_pl(v)
                                    if res: return res
                            elif isinstance(node, list):
                                for item in node:
                                    res = find_pl(item)
                                    if res: return res
                            return None
                            
                        pl_data = find_pl(obj)
                        if pl_data:
                            if pl_data.get('title'):
                                playlist_info['title'] = fix_mojibake(pl_data.get('title'))
                            owner = pl_data.get('owner', {})
                            playlist_info['owner'] = fix_mojibake(owner.get('name') or owner.get('login', ''))
                            playlist_info['track_count'] = pl_data.get('trackCount', 0)
                            
                            cover = pl_data.get('cover', {})
                            cover_uri = cover.get('uri', '') or pl_data.get('ogImage', '')
                            if cover_uri:
                                playlist_info['cover'] = f"https://{cover_uri.replace('%%', '400x400')}"
                                
                            raw_tracks = pl_data.get('tracks', [])
                            for rt in raw_tracks:
                                tid = str(rt.get('id'))
                                if tid in resolved_tracks_map:
                                    tracks_list.append(resolved_tracks_map[tid])
                                else:
                                    tracks_list.append({
                                        'id': tid,
                                        'album_id': rt.get('albumId'),
                                        'title': f"Трек #{tid}",
                                        'artists': ["Яндекс Музыка"],
                                        'artist': "Яндекс Музыка",
                                        'album': "",
                                        'duration_ms': 0,
                                        'duration_sec': 0,
                                        'cover': "",
                                        'url': f"https://music.yandex.ru/track/{tid}"
                                    })
                except Exception as e:
                    logger.debug(f"Error parsing Next.js script payload: {e}")

    # If we didn't find the tracks array in Next.js preloaded state, use resolved tracks
    if not tracks_list and resolved_tracks_map:
        tracks_list = list(resolved_tracks_map.values())
        
    playlist_info['tracks'] = tracks_list
    if not playlist_info['track_count']:
        playlist_info['track_count'] = len(tracks_list)
        
    return playlist_info

def parse_text_tracklist(text: str) -> Dict[str, Any]:
    """Parse plain text track list (e.g. Artist - Title or Title - Artist per line)."""
    text = fix_mojibake(text)
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    tracks = []
    
    for idx, line in enumerate(lines, start=1):
        cleaned = re.sub(r'^\d+[\.\-\)\s]+', '', line).strip()
        parts = re.split(r'\s+[-–—]\s+', cleaned, maxsplit=1)
        if len(parts) == 2:
            artist, title = parts[0].strip(), parts[1].strip()
        else:
            title = cleaned
            artist = "Неизвестный исполнитель"
            
        tracks.append({
            'id': f"custom_{idx}",
            'title': fix_mojibake(title),
            'artists': [fix_mojibake(artist)],
            'artist': fix_mojibake(artist),
            'album': "",
            'duration_ms': 180000,
            'duration_sec': 180,
            'cover': "",
            'url': ""
        })
        
    return {
        'title': 'Пользовательский список',
        'owner': 'Пользователь',
        'track_count': len(tracks),
        'cover': '',
        'url': '',
        'tracks': tracks
    }

def fetch_playlist_by_url(url: str) -> Dict[str, Any]:
    """Main entrypoint to parse a Yandex Music playlist by URL with multiple fallbacks."""
    url_info = parse_yandex_url(url)
    
    # 1. If it's a user/kind URL format, try API first
    if url_info['type'] == 'user_playlist' and url_info['user'] and url_info['kind']:
        api_url = f"https://api.music.yandex.net/users/{url_info['user']}/playlists/{url_info['kind']}"
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    api_url,
                    headers={'User-Agent': HEADERS['User-Agent'], 'Accept': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    result = data.get('result', {})
                    tracks_raw = result.get('tracks', [])
                    tracks = []
                    for t_item in tracks_raw:
                        t = t_item.get('track', t_item)
                        tid = str(t.get('id', ''))
                        artists = [fix_mojibake(a.get('name', '')) for a in t.get('artists', []) if a.get('name')]
                        albums = [fix_mojibake(a.get('title', '')) for a in t.get('albums', []) if a.get('title')]
                        cover = t.get('coverUri', '')
                        tracks.append({
                            'id': tid,
                            'title': fix_mojibake(t.get('title', f"Трек #{tid}")),
                            'artists': artists or ["Яндекс Музыка"],
                            'artist': ", ".join(artists) or "Яндекс Музыка",
                            'album': albums[0] if albums else "",
                            'duration_ms': t.get('durationMs', 0),
                            'duration_sec': t.get('durationMs', 0) // 1000,
                            'cover': f"https://{cover.replace('%%', '200x200')}" if cover else "",
                            'url': f"https://music.yandex.ru/track/{tid}"
                        })
                    owner = result.get('owner', {})
                    cover_uri = result.get('cover', {}).get('uri', '')
                    return {
                        'title': fix_mojibake(result.get('title', 'Плейлист Яндекс Музыки')),
                        'owner': fix_mojibake(owner.get('name') or owner.get('login', '')),
                        'track_count': result.get('trackCount', len(tracks)),
                        'cover': f"https://{cover_uri.replace('%%', '400x400')}" if cover_uri else "",
                        'url': url,
                        'tracks': tracks
                    }
            except Exception as e:
                logger.warning(f"API fetch attempt {attempt+1} failed for user playlist: {e}")
                time.sleep(0.5)

    # 2. Fetch the Web HTML with automatic retries
    try:
        html = fetch_html_with_retry(url, max_retries=3, timeout=6)
        playlist_data = extract_tracks_from_html(html, target_url=url)
        if playlist_data['tracks']:
            return playlist_data
    except Exception as e:
        logger.error(f"HTML fetch failed: {e}")
        raise RuntimeError(f"Не удалось получить доступ к плейлисту: {e}")

    raise RuntimeError("Не удалось извлечь треки из плейлиста. Возможно, плейлист приватный или ссылка некорректна.")
