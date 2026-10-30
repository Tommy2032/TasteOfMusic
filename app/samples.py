from typing import Dict, Any

SAMPLE_PLAYLIST_1 = {
    'title': 'Мне нравится (Erling)',
    'owner': 'Erling (@M3M0RY-R3D4KT0R)',
    'cover': 'https://avatars.yandex.net/get-music-user-playlist/11418140/favorit-playlist-cover.bb48fdb9b9f4/400x400',
    'url': 'https://music.yandex.ru/playlists/lk.0ce106d6-e6c0-4dd0-8173-3dba3e82cad6',
    'track_count': 25,
    'tracks': [
        {
            'id': '88219453',
            'title': 'а мой город',
            'artists': ['prvrln'],
            'artist': 'prvrln',
            'album': 'я, ты',
            'duration_sec': 234,
            'cover': 'https://avatars.yandex.net/get-music-content/5309210/1b1e253b.a.17141351-1/200x200',
            'url': 'https://music.yandex.ru/track/88219453'
        },
        {
            'id': '144206883',
            'title': 'когда-нибудь',
            'artists': ['Lizer', 'Highself', 'cold carti'],
            'artist': 'Lizer, Highself, cold carti',
            'album': '[без названия]',
            'duration_sec': 176,
            'cover': 'https://avatars.yandex.net/get-music-content/16469857/011e73cb.a.38745615-1/200x200',
            'url': 'https://music.yandex.ru/track/144206883'
        },
        {
            'id': '150273324',
            'title': 'одиноко',
            'artists': ['old honda'],
            'artist': 'old honda',
            'album': 'старые записи',
            'duration_sec': 197,
            'cover': 'https://avatars.yandex.net/get-music-content/15682289/f24289bc.a.41590963-1/200x200',
            'url': 'https://music.yandex.ru/track/150273324'
        },
        {
            'id': '50924041',
            'title': 'Дым сигарет с ментолом',
            'artists': ['Нэнси'],
            'artist': 'Нэнси',
            'album': 'Дым сигарет с ментолом',
            'duration_sec': 341,
            'cover': 'https://avatars.yandex.net/get-music-content/97284/ae09f729.a.4059315-1/200x200',
            'url': 'https://music.yandex.ru/track/50924041'
        },
        {
            'id': '122577743',
            'title': 'Lose Yourself',
            'artists': ['Eminem'],
            'artist': 'Eminem',
            'album': 'Curtain Call: The Hits',
            'duration_sec': 326,
            'cover': 'https://avatars.yandex.net/get-music-content/175094/e0a0d922.a.29666501-1/200x200',
            'url': 'https://music.yandex.ru/track/122577743'
        },
        {
            'id': '42359668',
            'title': 'Behind Blue Eyes',
            'artists': ['Nu Rock City'],
            'artist': 'Nu Rock City',
            'album': 'Rock Covers Volume 1',
            'duration_sec': 258,
            'cover': 'https://avatars.yandex.net/get-music-content/175094/c7ef28d9.a.14416075-1/200x200',
            'url': 'https://music.yandex.ru/track/42359668'
        },
        {
            'id': '53685454',
            'title': 'Я хороший',
            'artists': ['YUNG TRAPPA'],
            'artist': 'YUNG TRAPPA',
            'album': 'Forever',
            'duration_sec': 149,
            'cover': 'https://avatars.yandex.net/get-music-content/20622967/8345fc33.a.43905069-1/200x200',
            'url': 'https://music.yandex.ru/track/53685454'
        },
        {
            'id': '110356938',
            'title': 'Whistle',
            'artists': ['Merdy', 'Swizzy Max'],
            'artist': 'Merdy, Swizzy Max',
            'album': 'Whistle',
            'duration_sec': 142,
            'cover': 'https://avatars.yandex.net/get-music-content/24504859/6b8577bb.a.24504859-1/200x200',
            'url': 'https://music.yandex.ru/track/110356938'
        },
        {
            'id': '136300993',
            'title': 'Mockingbird',
            'artists': ['Eminem'],
            'artist': 'Eminem',
            'album': 'Encore',
            'duration_sec': 250,
            'cover': 'https://avatars.yandex.net/get-music-content/175094/e0a0d922.a.29666501-1/200x200',
            'url': 'https://music.yandex.ru/track/136300993'
        },
        {
            'id': '79142127',
            'title': 'Пачка сигарет',
            'artists': ['Lizer'],
            'artist': 'Lizer',
            'album': 'My Soul',
            'duration_sec': 158,
            'cover': 'https://avatars.yandex.net/get-music-content/13043189/57367f8c.p.795224/200x200',
            'url': 'https://music.yandex.ru/track/79142127'
        },
        {
            'id': '65432101',
            'title': 'Город дорог',
            'artists': ['CENTR', 'Баста'],
            'artist': 'CENTR, Баста',
            'album': 'Качели',
            'duration_sec': 267,
            'cover': 'https://avatars.yandex.net/get-music-content/28543/a123bc45.a.12345-1/200x200',
            'url': 'https://music.yandex.ru/track/65432101'
        },
        {
            'id': '78912345',
            'title': 'Blinding Lights',
            'artists': ['The Weeknd'],
            'artist': 'The Weeknd',
            'album': 'After Hours',
            'duration_sec': 200,
            'cover': 'https://avatars.yandex.net/get-music-content/123456/b789ef.a.654321-1/200x200',
            'url': 'https://music.yandex.ru/track/78912345'
        },
        {
            'id': '98765432',
            'title': 'Starboy',
            'artists': ['The Weeknd', 'Daft Punk'],
            'artist': 'The Weeknd, Daft Punk',
            'album': 'Starboy',
            'duration_sec': 230,
            'cover': 'https://avatars.yandex.net/get-music-content/654321/c987fa.a.987654-1/200x200',
            'url': 'https://music.yandex.ru/track/98765432'
        },
        {
            'id': '54321678',
            'title': 'I Got Love',
            'artists': ['Miyagi & Эндшпиль', 'Рем Дигга'],
            'artist': 'Miyagi & Эндшпиль, Рем Дигга',
            'album': 'Hajime, Pt. 2',
            'duration_sec': 275,
            'cover': 'https://avatars.yandex.net/get-music-content/112233/d543bb.a.543216-1/200x200',
            'url': 'https://music.yandex.ru/track/54321678'
        },
        {
            'id': '43219876',
            'title': 'Тамада',
            'artists': ['Miyagi & Эндшпиль'],
            'artist': 'Miyagi & Эндшпиль',
            'album': 'Hajime, Pt. 1',
            'duration_sec': 234,
            'cover': 'https://avatars.yandex.net/get-music-content/334455/e432cc.a.432198-1/200x200',
            'url': 'https://music.yandex.ru/track/43219876'
        }
    ]
}

SAMPLE_PLAYLIST_2 = {
    'title': 'Вечерний Плейлист & Хиты',
    'owner': 'Александра (@sasha-music)',
    'cover': 'https://avatars.yandex.net/get-music-user-playlist/28543/evening-vibes/400x400',
    'url': 'https://music.yandex.ru/users/sasha-music/playlists/1005',
    'track_count': 18,
    'tracks': [
        {
            'id': '122577743',
            'title': 'Lose Yourself',
            'artists': ['Eminem'],
            'artist': 'Eminem',
            'album': 'Curtain Call: The Hits',
            'duration_sec': 326,
            'cover': 'https://avatars.yandex.net/get-music-content/175094/e0a0d922.a.29666501-1/200x200',
            'url': 'https://music.yandex.ru/track/122577743'
        },
        {
            'id': '144206883',
            'title': 'когда-нибудь',
            'artists': ['Lizer', 'Highself', 'cold carti'],
            'artist': 'Lizer, Highself, cold carti',
            'album': '[без названия]',
            'duration_sec': 176,
            'cover': 'https://avatars.yandex.net/get-music-content/16469857/011e73cb.a.38745615-1/200x200',
            'url': 'https://music.yandex.ru/track/144206883'
        },
        {
            'id': '79142127',
            'title': 'Пачка сигарет',
            'artists': ['Lizer'],
            'artist': 'Lizer',
            'album': 'My Soul',
            'duration_sec': 158,
            'cover': 'https://avatars.yandex.net/get-music-content/13043189/57367f8c.p.795224/200x200',
            'url': 'https://music.yandex.ru/track/79142127'
        },
        {
            'id': '42359668',
            'title': 'Behind Blue Eyes',
            'artists': ['Nu Rock City'],
            'artist': 'Nu Rock City',
            'album': 'Rock Covers Volume 1',
            'duration_sec': 258,
            'cover': 'https://avatars.yandex.net/get-music-content/175094/c7ef28d9.a.14416075-1/200x200',
            'url': 'https://music.yandex.ru/track/42359668'
        },
        {
            'id': '78912345',
            'title': 'Blinding Lights',
            'artists': ['The Weeknd'],
            'artist': 'The Weeknd',
            'album': 'After Hours',
            'duration_sec': 200,
            'cover': 'https://avatars.yandex.net/get-music-content/123456/b789ef.a.654321-1/200x200',
            'url': 'https://music.yandex.ru/track/78912345'
        },
        {
            'id': '54321678',
            'title': 'I Got Love',
            'artists': ['Miyagi & Эндшпиль', 'Рем Дигга'],
            'artist': 'Miyagi & Эндшпиль, Рем Дигга',
            'album': 'Hajime, Pt. 2',
            'duration_sec': 275,
            'cover': 'https://avatars.yandex.net/get-music-content/112233/d543bb.a.543216-1/200x200',
            'url': 'https://music.yandex.ru/track/54321678'
        },
        {
            'id': '111222333',
            'title': 'Sweater Weather',
            'artists': ['The Neighbourhood'],
            'artist': 'The Neighbourhood',
            'album': 'I Love You.',
            'duration_sec': 240,
            'cover': 'https://avatars.yandex.net/get-music-content/789012/nb11.a.111222-1/200x200',
            'url': 'https://music.yandex.ru/track/111222333'
        },
        {
            'id': '222333444',
            'title': 'Do I Wanna Know?',
            'artists': ['Arctic Monkeys'],
            'artist': 'Arctic Monkeys',
            'album': 'AM',
            'duration_sec': 272,
            'cover': 'https://avatars.yandex.net/get-music-content/890123/am22.a.222333-1/200x200',
            'url': 'https://music.yandex.ru/track/222333444'
        },
        {
            'id': '333444555',
            'title': 'Without Me',
            'artists': ['Eminem'],
            'artist': 'Eminem',
            'album': 'The Eminem Show',
            'duration_sec': 290,
            'cover': 'https://avatars.yandex.net/get-music-content/175094/e0a0d922.a.29666501-1/200x200',
            'url': 'https://music.yandex.ru/track/333444555'
        },
        {
            'id': '444555666',
            'title': 'The Hills',
            'artists': ['The Weeknd'],
            'artist': 'The Weeknd',
            'album': 'Beauty Behind the Madness',
            'duration_sec': 242,
            'cover': 'https://avatars.yandex.net/get-music-content/123456/b789ef.a.654321-1/200x200',
            'url': 'https://music.yandex.ru/track/444555666'
        },
        {
            'id': '555666777',
            'title': 'Minor',
            'artists': ['Miyagi & Andy Panda'],
            'artist': 'Miyagi & Andy Panda',
            'album': 'YAMAKASI',
            'duration_sec': 175,
            'cover': 'https://avatars.yandex.net/get-music-content/112233/d543bb.a.543216-1/200x200',
            'url': 'https://music.yandex.ru/track/555666777'
        }
    ]
}

def get_sample_playlists() -> Dict[str, Any]:
    return {
        'playlist1': SAMPLE_PLAYLIST_1,
        'playlist2': SAMPLE_PLAYLIST_2
    }

