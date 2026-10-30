import re
from typing import Dict, List, Any, Set, Tuple
from app.parser import normalize_text, fix_mojibake, enrich_tracks_metadata

def format_duration(seconds: int) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    if not seconds:
        return "0:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def get_track_key(track: Dict[str, Any]) -> str:
    """Generate normalized matching key for a track."""
    norm_title = normalize_text(track.get('title', ''))
    # Extract primary artist
    artists = track.get('artists', [])
    if isinstance(artists, list) and artists:
        norm_artist = normalize_text(artists[0])
    else:
        norm_artist = normalize_text(track.get('artist', ''))
    return f"{norm_artist}___{norm_title}"

def compare_playlists(p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two playlists, enrich matching tracks with real metadata, and calculate metrics."""
    tracks1 = p1.get('tracks', [])
    tracks2 = p2.get('tracks', [])
    
    total_1 = len(tracks1)
    total_2 = len(tracks2)
    
    # Track ID lookup
    id_map2 = {str(t['id']): t for t in tracks2 if t.get('id') and not str(t['id']).startswith('custom_')}
    
    # Key lookup
    key_map2 = {}
    for t in tracks2:
        k = get_track_key(t)
        if k and k != "___":
            key_map2[k] = t

    matching_tracks = []
    matched_ids_in_2: Set[str] = set()
    matched_keys_in_2: Set[str] = set()

    for t1 in tracks1:
        tid1 = str(t1.get('id', ''))
        matched = False
        match_source = None
        match_type = ""
        
        # 1. Exact ID match (both Yandex Music tracks)
        if tid1 and tid1 in id_map2 and not tid1.startswith('custom_'):
            match_source = id_map2[tid1]
            matched = True
            match_type = "Точное совпадение ID"
            matched_ids_in_2.add(tid1)
        else:
            # 2. Fuzzy key match
            k1 = get_track_key(t1)
            if k1 and k1 in key_map2 and k1 not in matched_keys_in_2:
                match_source = key_map2[k1]
                matched = True
                match_type = "По названию и исполнителю"
                matched_keys_in_2.add(k1)
                
        if matched and match_source:
            best_title = t1.get('title') or match_source.get('title', '')
            best_artists = t1.get('artists') if t1.get('artists') != ["Яндекс Музыка"] else match_source.get('artists', [])
            best_artist = t1.get('artist') if t1.get('artist') != "Яндекс Музыка" else match_source.get('artist', '')
            best_cover = t1.get('cover') or match_source.get('cover', '')
            best_duration = max(t1.get('duration_sec', 0), match_source.get('duration_sec', 0))
            best_album = t1.get('album') or match_source.get('album', '')
            best_url = t1.get('url') or match_source.get('url', f"https://music.yandex.ru/track/{tid1}")
            
            matching_tracks.append({
                'id': tid1,
                'title': fix_mojibake(best_title),
                'artists': [fix_mojibake(a) for a in best_artists] if best_artists else ["Яндекс Музыка"],
                'artist': fix_mojibake(best_artist),
                'album': fix_mojibake(best_album),
                'duration_sec': best_duration,
                'duration_fmt': format_duration(best_duration),
                'cover': best_cover,
                'url': best_url,
                'match_type': match_type
            })

    # ENRICH MATCHING TRACKS: Fetch real titles and artists for matching tracks!
    if matching_tracks:
        try:
            matching_tracks = enrich_tracks_metadata(matching_tracks, max_to_enrich=200)
            # Reformat duration_fmt
            for mt in matching_tracks:
                mt['duration_fmt'] = format_duration(mt.get('duration_sec', 0))
        except Exception:
            pass

    match_count = len(matching_tracks)
    
    # Calculate Jaccard similarity and percentage
    union_count = (total_1 + total_2 - match_count) if (total_1 + total_2 - match_count) > 0 else 1
    jaccard_score = round((match_count / union_count) * 100, 1)
    
    pct_of_p1 = round((match_count / total_1 * 100), 1) if total_1 > 0 else 0.0
    pct_of_p2 = round((match_count / total_2 * 100), 1) if total_2 > 0 else 0.0
    
    # Compatibility rating verdict
    if jaccard_score >= 70 or (pct_of_p1 >= 80 and pct_of_p2 >= 80):
        verdict = "Родственные души 🎧🔥"
        verdict_desc = "Практически идентичные музыкальные вкусы! Вы могли бы слушать один плеер на двоих."
    elif jaccard_score >= 40 or (pct_of_p1 >= 50 and pct_of_p2 >= 50):
        verdict = "На одной волне 🌊"
        verdict_desc = "Отличное взаимопонимание в музыке! Множество любимых треков совпадает."
    elif jaccard_score >= 20 or match_count >= 10:
        verdict = "Музыкальный консенсус 🤝"
        verdict_desc = "Есть крепкая общая база треков, при этом у каждого есть своя уникальная специфика."
    elif match_count >= 1:
        verdict = "Интересный контраст 🎨"
        verdict_desc = "Разные предпочтения, но найдены классные точки соприкосновения."
    else:
        verdict = "Полная эклектика 🚀"
        verdict_desc = "Два совершенно уникальных музыкальных мира без прямых пересечений треков."

    # Shared artists analysis (include artists from enriched matching tracks!)
    def extract_artist_set(tracks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        res: Dict[str, List[Dict[str, Any]]] = {}
        for t in tracks:
            for art in t.get('artists', []):
                cleaned = fix_mojibake(art.strip())
                if cleaned and cleaned != "Яндекс Музыка":
                    if cleaned not in res:
                        res[cleaned] = []
                    res[cleaned].append(t)
        return res

    artists_1 = extract_artist_set(tracks1)
    artists_2 = extract_artist_set(tracks2)
    
    # Also add artists from enriched matching tracks to both sets if not already present
    for mt in matching_tracks:
        for art in mt.get('artists', []):
            cleaned = fix_mojibake(art.strip())
            if cleaned and cleaned != "Яндекс Музыка":
                if cleaned not in artists_1:
                    artists_1[cleaned] = [mt]
                if cleaned not in artists_2:
                    artists_2[cleaned] = [mt]

    common_artist_names = sorted(list(set(artists_1.keys()) & set(artists_2.keys())))
    shared_artists_list = []
    for art_name in common_artist_names:
        shared_artists_list.append({
            'name': art_name,
            'tracks_in_p1': len(artists_1[art_name]),
            'tracks_in_p2': len(artists_2[art_name]),
            'total_tracks': len(artists_1[art_name]) + len(artists_2[art_name]),
            'sample_titles_1': [t.get('title', '') for t in artists_1[art_name][:3]],
            'sample_titles_2': [t.get('title', '') for t in artists_2[art_name][:3]]
        })
    shared_artists_list.sort(key=lambda x: x['total_tracks'], reverse=True)

    # Total shared duration
    total_shared_duration_sec = sum(t.get('duration_sec', 0) for t in matching_tracks)

    return {
        'playlist1': {
            'title': fix_mojibake(p1.get('title', 'Плейлист 1')),
            'owner': fix_mojibake(p1.get('owner', '')),
            'cover': p1.get('cover', ''),
            'url': p1.get('url', ''),
            'total_tracks': total_1,
            'match_percent': pct_of_p1,
            'tracks': tracks1
        },
        'playlist2': {
            'title': fix_mojibake(p2.get('title', 'Плейлист 2')),
            'owner': fix_mojibake(p2.get('owner', '')),
            'cover': p2.get('cover', ''),
            'url': p2.get('url', ''),
            'total_tracks': total_2,
            'match_percent': pct_of_p2,
            'tracks': tracks2
        },
        'stats': {
            'matching_tracks_count': match_count,
            'shared_artists_count': len(shared_artists_list),
            'jaccard_score': jaccard_score,
            'unique_to_p1': total_1 - match_count,
            'unique_to_p2': total_2 - match_count,
            'total_union': total_1 + total_2 - match_count,
            'total_shared_duration_sec': total_shared_duration_sec,
            'total_shared_duration_fmt': format_duration(total_shared_duration_sec),
            'verdict': verdict,
            'verdict_desc': verdict_desc
        },
        'matching_tracks': matching_tracks,
        'shared_artists': shared_artists_list
    }
