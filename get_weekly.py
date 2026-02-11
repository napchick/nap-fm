import pandas as pd
from datetime import timedelta, datetime
from database.models import engine
import page_reqs as pr
import json


with open("weekly_data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

# начало нового периоды. Пока так, но потом берем end из json
begin = loaded['end']
#begin = datetime.strptime('2026-02-02T00:00:07.566Z', "%Y-%m-%dT%H:%M:%S.%fZ") # "%Y-%m-%dT%H:%M:%SZ"
# Конец текущего периода
end = begin + timedelta(weeks=1)

# Количество прослушиваний за неделю
scrobbles = pd.read_sql(pr.get_scrobbles(f"where time >= '{begin}'"), engine)['count'].iloc[0]
# Количество уникальных артистов
artists = pd.read_sql(pr.get_unique_artists(f"where h.time >= '{begin}'"), engine)['artists_count'].iloc[0]
# Количество уникальных артистов всего. 
unique_artists = pd.read_sql(pr.unique_artists, engine)['artists_count'].iloc[0]
# Количество уникальных песен
songs = pd.read_sql(pr.get_unique_songs(f"where time >= '{begin}'"), engine)['songs_count'].iloc[0]
# Количество уникальных песен всего. При вычитании узнаем сколько появилось новых
unique_songs = pd.read_sql(pr.unique_songs, engine)['songs_count'].iloc[0]
# Топ 5 песен (не оч понятно как это хранить но пусть будет так)
top_songs = pd.read_sql(pr.get_top_songs(f"where h.time >= '{begin}'"), engine)
# Топ 5 артистов(также формат таблицы)
top_artists = pd.read_sql(pr.get_top_artists(f"where h.time >= '{begin}'"), engine)
# Получить жанры
top_genres = pd.read_sql(pr.get_genres(f"where time >= '{begin}'", "limit 5"), engine)
# ТОп песен по декадам
songs_per_decade = pd.read_sql(pr.get_songs_per_year_period(f"where h.time >= '{begin}'"), engine)
# Топ песен по часам
songs_per_hours = pd.read_sql(pr.get_songs_per_hours(f"where time >= '{begin}'"), engine)
# Топ стран по песням
songs_per_countries = pd.read_sql(pr.get_songs_per_country(f"where h.time >= '{begin}' and a.country is not null", 
                                                           'limit 5'), engine)

print(artists)


data = {
    'begin': begin.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    'end': end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    'scrobbles': int(scrobbles),
    'artists': int(artists),
    'unique_artists': int(unique_artists),
    'songs': int(songs),
    'unique_songs': int(unique_songs),
    'top_songs': top_songs.to_dict(orient='records'),
    'top_artists': top_artists.to_dict(orient='records'),
    'top_genres': top_genres.to_dict(orient='records'),
    'songs_per_decade': songs_per_decade.to_dict(orient='records'),
    'songs_per_hours': songs_per_hours.to_dict(orient='records'),
    'songs_per_countries': songs_per_countries.to_dict(orient='records')
}

with open("weekly_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# python get_weekly.py