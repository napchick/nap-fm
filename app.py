import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import spotipy.util as util
import pylab
import pandas as pd
from urllib.parse import unquote
import time
import datetime
from datetime import timedelta
import requests
import os
import json 

import database.reqs as rq

from dotenv import load_dotenv
if os.path.exists(".env"):
    load_dotenv()

############################################# Подключаемся к аккаунту ########################################


cid = os.getenv("SPOTIFY_CLIENT_ID")
secret = os.getenv("SPOTIFY_CLIENT_SECRET")
rur = os.getenv("SPOTIFY_REDIRECT_URI")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
scope = "user-read-private user-read-email user-library-read user-library-modify user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played user-top-read playlist-read-private playlist-modify-private playlist-modify-public"
user = '31t6epawnwecq5mlows2f57weyyy' # имя пользователя



# получаем доступ к spotify api для личной информации
sp_oauth = SpotifyOAuth(
    client_id=cid,
    client_secret=secret,
    redirect_uri=rur,
    scope=scope,
    username=user
)

# auth_url = sp_oauth.get_authorize_url()
# print("Пожалуйста, перейдите по этой ссылке, чтобы авторизоваться:")
# print(unquote(auth_url))

# code = str(input())

# # получем токен
# token_info = sp_oauth.get_access_token(code)
token_info = sp_oauth.refresh_access_token(refresh_token)
sp = spotipy.Spotify(auth=token_info["access_token"])



# Получаем доступ к spotify api для информации об артистах
sp_public = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=cid,
    client_secret=secret
))



########################################## Вспомогательные вещи для работы ##########################################


# поиск информации об артисте
def get_artist_info1(artist_name):
    url = "https://musicbrainz.org/ws/2/artist/"
    params = {'query': f'artist:{artist_name}', 'fmt': 'json'}
    headers = {"User-Agent": "MyMusicApp/1.0 (myemail@example.com)"}

    try:
        res = requests.get(url, params=params, headers=headers, timeout=60)
        data = res.json()
    except Exception as e:
        print(f"Ошибка при запросе MusicBrainz: {e}")
        return {"country": None, "birth_date": None, "type": None}

    if "artists" in data and data["artists"]:
        artist_data = data["artists"][0]
        return {
            "country": artist_data.get("country"),
            "birth_date": artist_data.get("life-span", {}).get("begin"),
            "type": artist_data.get("type")
        }

    # если ничего не нашли
    return {"country": None, "birth_date": None, "type": None}


TIMESTAMP_FILE = 'last_timestamp.json'

# функция для загрузки времени последнего прослушивания
def load_previous_time(default_value='2025-10-31T17:56:08.859Z'):  # Default — начальное значение, если файла нет
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, 'r') as f:
            data = json.load(f)
            return data.get('previous_time', default_value)
    return default_value

# функция для сохранения времени последнего прослушивания
def save_previous_time(timestamp):
    with open(TIMESTAMP_FILE, 'w') as f:
        json.dump({'previous_time': timestamp}, f)


song_id = None
#################################################### Цикл обработки информации #########################################


# создаем переменные для отслеживания времени
# previous_time = '2025-10-31T17:45:23.783Z'
def run():

#while True:
    # обращаемся к spotify за списком треков
    recent = sp.current_user_recently_played(limit=50)

    # загружаем время последнего прослушивания из файла
    previous_time = load_previous_time()

    n = 1
    # обрабатываем каждый трек отдельно
    for idx, item in enumerate(reversed(recent['items'])):
        if item['played_at'] > previous_time:
            # song
            track = item['track'] # получаем информацию о песне

            artist = item['track']['artists'][0]['name']
            title = item['track']['name']

            # Есть ли уже такая песня в базе
            if rq.is_song(title, artist) == 0:
                duration = item['track']['duration_ms']
                logo = item['track']['album']['images'][0]['url']
                popularity = item['track']['popularity']
                release_date = item['track']['album']['release_date']

                # добавление песни в соответствующую таблицу
                rq.set_song(title, duration, logo, release_date, popularity)
                song_id = rq.get_max_song_id()


            # artist
            # Есть ли уже такой артист в базе
            if rq.is_artist(artist) == 0:
                artist_info = get_artist_info1(artist) # ищем информацию по нашему артисту
                result = sp_public.search(q=artist, type='artist', limit=1) # ищем информацию по нашему артисту

                followers = result['artists']['items'][0]['followers']['total']
                genres = result['artists']['items'][0]['genres']
                popularity = result['artists']['items'][0]['popularity']
                try:
                    photo = result['artists']['items'][0]['images'][0]['url']
                except:
                    photo = ''
                birthday = artist_info['birth_date']
                typ = artist_info['type']
                country = artist_info['country']

                # Добавление информации об артисте
                rq.set_artist(artist, followers, popularity, photo, birthday, country)

                # Получим id артиста
                artist_id = rq.get_artist_id(artist)

                # Идем по всем жанрам:
                for genre in genres:
                    # Проверка наличия жанра:
                    if rq.is_genre(genre) == 0:
                        # добавление нового жанра в таблицу
                        rq.set_genre(genre)
                    
                    # Добавление связки жанр-артист
                    # Определим id жанра
                    genre_id = rq.get_genre_id(genre)
                    rq.set_genre_artist(artist_id, genre_id)
            

            # Определим id для песни
            
            new_song_id = rq.get_song_id(title, artist)
            if new_song_id != None:
                song_id = new_song_id
            # тут проблема в том, что мы join сонг-артист, но мы еще на этот момент не добавили эту запись, плэтому 
            # не находим id этой песни


            # Добавление песни в таблицу с историей
            play_time_str = item['played_at']
            try:
                play_time = datetime.datetime.strptime(play_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                prev_play_time = datetime.datetime.strptime(previous_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                play_time = datetime.datetime.strptime(play_time_str, "%Y-%m-%dT%H:%M:%SZ")
                prev_play_time = datetime.datetime.strptime(previous_time, "%Y-%m-%dT%H:%M:%SZ")
            play_time += timedelta(hours=3)
            prev_play_time += timedelta(hours=3)

            # Проверка, что песня была прослушана хотя бы 1 минуту, а не пролистана
            if play_time - prev_play_time >= timedelta(minutes=1):
                rq.set_history(song_id, play_time)


            # Добавление связки песня-артист
            if rq.is_artist_song_in_table(song_id) == 0:
                artist_id = rq.get_artist_id(artist)
                rq.set_song_artist(artist_id, song_id)

            print(f"Добавлена {n} песня: {item['played_at']}")
            n += 1
            previous_time = max(previous_time, item['played_at'])
            save_previous_time(previous_time)


    print('Все успешно прошло')

    #time.sleep(tim) # 1500


if __name__ == "__main__":
    run()
# source .venv/bin/activate