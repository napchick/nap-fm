import pandas as pd
from database.models import engine

# последние 10 прослушанных песен
last10 = """
SELECT
    s.logo, s.title, a.name, h.time, s.song_id as id, a.photo, a.country, a.birthday, a.followers, a.artist_id
FROM songs s join history h on s.song_id = h.song_id 
    join songs2artists sa on s.song_id = sa.song_id
    join artists a on sa.artist_id = a.artist_id
order by h.id desc
LIMIT 10
"""


# все песни
all_songs = """
SELECT
    s.logo, s.title, a.name, h.time, s.song_id as id, a.artist_id
FROM songs s join history h on s.song_id = h.song_id 
    join songs2artists sa on s.song_id = sa.song_id
    join artists a on sa.artist_id = a.artist_id
order by h.id desc
"""


# Прослушивания артистов
artists_stream = """ 
    select a.artist_id, count(h.id) as count_plays, a.photo, a.name as artist_name
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
    group by a.artist_id
    order by count(h.id) desc
    """


# Агрегированные песни
songs_agr = """ 
    select h.song_id, count(h.id) as count_plays, s.logo, a.name as artist_name, s.title
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
    group by h.song_id, s.logo, a.name, s.title
    order by count(h.id) desc
    """

# число уникальных песен
unique_songs = """
SELECT count(song_id) as songs_count
FROM songs"""


# Число уникальных исполнителей
unique_artists = """
SELECT count(artist_id) as artists_count
FROM artists"""


# самые прослушиваемые песни
top_songs = """ 
select h.song_id, s.title, count(h.id) as count_plays, s.logo, a.name as artist_name
FROM songs s join history h on s.song_id = h.song_id 
    join songs2artists sa on s.song_id = sa.song_id
    join artists a on sa.artist_id = a.artist_id
group by h.song_id, s.logo, a.name, s.title
order by count(h.id) desc
limit 5
"""


# самые прослушиваемые исполнители
top_artists = """ 
select a.artist_id, count(h.id) as count_plays, a.photo, a.name as artist_name
FROM songs s join history h on s.song_id = h.song_id 
    join songs2artists sa on s.song_id = sa.song_id
    join artists a on sa.artist_id = a.artist_id
group by a.artist_id
order by count(h.id) desc
limit 5
"""


# количество прослушиваний 
scrobbles = """
select count(id)
from history
"""


# топ песни за последнюю неделю
def get_top_songs_period(top_tracks_period):
    top_songs_period = f"""
    select h.song_id as id, s.title, count(h.id) as count_plays, s.logo, a.name as artist_name, a.artist_id
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
    where h.time::timestamp >= now() - interval {top_tracks_period}
    group by h.song_id, s.logo, a.name, s.title, a.artist_id
    order by count(h.id) desc
    limit 5
    """

    return top_songs_period


# топ исполнителей за последнюю неделю
def get_top_artists_period(top_artists_period):
    top_artists_period_diff = f""" 
    select a.artist_id, count(h.id) as count_plays, a.photo, a.name as artist_name
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
    where h.time::timestamp >= now() - interval {top_artists_period}
    group by a.artist_id
    order by count(h.id) desc
    limit 5
    """

    return top_artists_period_diff


# Распределение песен по годам
def get_songs_per_year_period(whe):
    songs_per_year_period = f"""
    WITH subquery AS (
        SELECT 
            h.song_id, 
            CASE
                WHEN substring(s.release_date from 1 for 4)::int > 2020 THEN '2020'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 2011 AND 2020 THEN '2010'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 2001 AND 2010 THEN '2000'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1991 AND 2000 THEN '1990'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1981 AND 1990 THEN '1980'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1971 AND 1980 THEN '1970'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1961 AND 1970 THEN '1960'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1951 AND 1960 THEN '1950'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1941 AND 1950 THEN '1940'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1931 AND 1940 THEN '1930'
                WHEN substring(s.release_date from 1 for 4)::int BETWEEN 1921 AND 1930 THEN '1920'
            END AS song_year
        FROM songs s 
        JOIN history h ON s.song_id = h.song_id
        {whe}
    ),

    counted AS (
        SELECT 
            song_year,
            song_id,
            COUNT(*) AS play_count
        FROM subquery
        GROUP BY song_year, song_id
    ),

    ranked AS (
        SELECT 
            song_year,
            song_id,
            play_count,
            RANK() OVER (PARTITION BY song_year ORDER BY play_count DESC) AS rnk
        FROM counted
    ),

    top as (

    SELECT 
        song_year,
        COUNT(song_id) AS total_songs,
        MAX(song_id) FILTER (WHERE rnk = 1) AS top_song_id
    FROM ranked
    GROUP BY song_year
    ORDER BY song_year DESC
    )

    select t.song_year, t.total_songs, t.top_song_id, s.title, s.logo, a.name as artist_name
    from top t join songs s on t.top_song_id = s.song_id
        join songs2artists sa on sa.song_id = s.song_id
        join artists a on a.artist_id = sa.artist_id
    ORDER BY t.song_year

    """

    return songs_per_year_period


# распределение прослушивания по часам
def get_songs_per_hours(period):
    songs_per_hours = f"""
    select substring(time from 12 for 2)::int as hour, count(id) as plays
    from history
    {period}
    group by substring(time from 12 for 2)::int
    order by hour
    """

    return songs_per_hours



# распределение песен по странам
songs_per_country = """
select a.country, count(h.id)
FROM songs s join history h on s.song_id = h.song_id 
    join songs2artists sa on s.song_id = sa.song_id
    join artists a on sa.artist_id = a.artist_id
group by a.country
order by count(h.id) desc
"""

############# добавить еще топ песню/артиста для кажой страны

# распределение артистов по странам
artists_per_country = """
select country, count(artist_id)
from artists
group by country 
order by count(artist_id)
"""


# жанры
def get_genres(first_date, second_date):
    genres =f"""
    with subquery as (
    select h.time, h.song_id, g.genre_name, s.title, a.name,
        case 
        when g.genre_name like '%%rap' or g.genre_name like '%% rap' or g.genre_name like '%% hip hop' then 'rap'
        when g.genre_name like 'folk' or g.genre_name like 'folr %%' then 'folk'
        when g.genre_name like 'death%%' or g.genre_name like 'death %%' then 'deathcore'
        when g.genre_name like '%%core' or g.genre_name like 'emo' or g.genre_name like 'djent' or g.genre_name like 'scream%%'
            or g.genre_name like 'khaleeji' then 'metalcore'
        when g.genre_name like 'power metal' or g.genre_name like 'symphonic metal' then 'power metal'
        when g.genre_name like '%% metal' or g.genre_name like 'metal' or g.genre_name like 'industrial' then 'metal'
        when g.genre_name like '%% rock' or g.genre_name like '%%rock' or g.genre_name like 'rock %%' then 'rock'
        when g.genre_name like 'jazz' or g.genre_name like 'jazz %%' or g.genre_name like '%% jazz' 
            or g.genre_name like 'swing music' or g.genre_name like 'big band' then 'jazz'
        when g.genre_name like 'schlager' or g.genre_name like 'chanson' then 'schlager'
        when g.genre_name like 'christmas' or g.genre_name like 'adult standards' 
            or g.genre_name like 'singer-songwriter' or g.genre_name like 'doo-wop' then 'oldies'
        when g.genre_name like 'punk' or g.genre_name like '%%punk' or g.genre_name like '%% punk' then 'punk'
        when g.genre_name like 'pop' or g.genre_name like '%% pop' or g.genre_name like '%%pop' or g.genre_name like 'bolero'
            or g.genre_name like 'variété française' or g.genre_name like '%% dance' or g.genre_name like '%%dance' 
            then 'pop'
        when g.genre_name like 'elctro%%' or g.genre_name like '%% house' then 'electro'
        when g.genre_name like 'soundtrack' then 'soundtrack'
        when g.genre_name like '%%wave' or g.genre_name like '%% wave' then 'wave'
        when g.genre_name like 'opera' or g.genre_name like 'musicals' then 'opera'
        when g.genre_name like 'grunge' then 'grunge'
        when g.genre_name like 'motown' then 'motown'
        when g.genre_name like 'classical' then 'classic'
        else '-'
        end as new_genre
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
        join artists2genres ag on ag.artist_id = a.artist_id
        join genres g on g.genre_id = ag.genre_id
    ), 
    sub2 as (
    select distinct time, song_id, new_genre
    from subquery
    )

    select new_genre, count(song_id)
    from sub2
    group by new_genre
    order by count desc
    """

    return genres


#     where time >= now() - {first_date} and time <= now() - '' {second_date}
# деткор (deathcore, death metal)

# металкор (metalcore, post-hardcore, emo, melodic hardcore, djent, screamo, mathcore, hardcore, hardcore punk, 
# horrorcore, khaleeji,)

# метал (metal, glam metal, power metal, symphonic metal, speed metal, folk metal, industrial metal, heavy metal)
# ню метал (rap metal,  nu metal, alternative metal, medieval metal, progressive metal)

# рок (glam rock, art rock, noise rock, yacht rock, soft rock, hard rock, rock, country rock, alternative rock, 
# progressive rock, psychedelick rock, j-rock)

# джаз(jazz, swing music, big band, vocal jazz, jazz blues, )

# schlager(schlager, chanson, )

# oldies(christmas, adult standarts, singer-songwriter)

# pop(pop, bolero, variété française, baroque pop, soft pop, britpop, art pop, dance pop, swedish pop, french pop, synthpop)

# wave (new wave, synthwave, coldwave, drakwave)

# punk(post-punk, pop punk)

# electro (witch house, )
# folk(folk rock, folk)
# rap(trap metal, emo rap)
# soundtrack (soundtrack)
# opera (opera, musicals)
# grunge(grunge)
# motown

# поиск жанров, которые не попали ни в одну из категорий
def get_mising_genres(first_date, second_date):
    genres =f"""
    with subquery as (
    select h.time, h.song_id, g.genre_name, s.title, a.name,
        case 
        when g.genre_name like '%%rap' or g.genre_name like '%% rap' or g.genre_name like '%% hip hop' then 'rap'
        when g.genre_name like 'folk' or g.genre_name like 'folr %%' then 'folk'
        when g.genre_name like 'death%%' or g.genre_name like 'death %%' then 'deathcore'
        when g.genre_name like '%%core' or g.genre_name like 'emo' or g.genre_name like 'djent' or g.genre_name like 'scream%%'
            or g.genre_name like 'khaleeji' then 'metalcore'
        when g.genre_name like 'power metal' or g.genre_name like 'symphonic metal' then 'power metal'
        when g.genre_name like '%% metal' or g.genre_name like 'metal' or g.genre_name like 'industrial' then 'metal'
        when g.genre_name like '%% rock' or g.genre_name like '%%rock' or g.genre_name like 'rock %%' then 'rock'
        when g.genre_name like 'jazz' or g.genre_name like 'jazz %%' or g.genre_name like '%% jazz' 
            or g.genre_name like 'swing music' or g.genre_name like 'big band' then 'jazz'
        when g.genre_name like 'schlager' or g.genre_name like 'chanson' then 'schlager'
        when g.genre_name like 'christmas' or g.genre_name like 'adult standards' 
            or g.genre_name like 'singer-songwriter' or g.genre_name like 'doo-wop' then 'oldies'
        when g.genre_name like 'punk' or g.genre_name like '%%punk' or g.genre_name like '%% punk' then 'punk'
        when g.genre_name like 'pop' or g.genre_name like '%% pop' or g.genre_name like '%%pop' or g.genre_name like 'bolero'
            or g.genre_name like 'variété française' or g.genre_name like '%% dance' or g.genre_name like '%%dance' 
            then 'pop'
        when g.genre_name like 'elctro%%' or g.genre_name like '%% house' then 'electro'
        when g.genre_name like 'soundtrack' then 'soundtrack'
        when g.genre_name like '%%wave' or g.genre_name like '%% wave' then 'wave'
        when g.genre_name like 'opera' or g.genre_name like 'musicals' then 'opera'
        when g.genre_name like 'grunge' then 'grunge'
        when g.genre_name like 'motown' then 'motown'
        when g.genre_name like 'classical' then 'classic'
        else '-'
        end as new_genre
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
        join artists2genres ag on ag.artist_id = a.artist_id
        join genres g on g.genre_id = ag.genre_id
    )

    select distinct time, song_id, genre_name, new_genre
    from subquery
    where new_genre = '-'
    """

    return genres


# вспомогательная функция для определения артистов по id жанра
def get_art(id):
    genar = f"""
    select a.name
    from genres g join artists2genres ag on g.genre_id = ag.genre_id
        join artists a on a.artist_id = ag.artist_id
    where g.genre_id = {id}
    """

    return genar


# определить текущую дату
get_data = """
select now()::date
"""

# информация о песне по ее id
def get_song_information(id):
    song_information = f"""
    select s.title, s.duration, s.logo, s.release_date, s.popularity, a.name
    FROM songs s join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
    where s.song_id = {id}
    """

    return song_information


# история прослушивания песни
def get_song_history(id):
    song_history = f""" 
    select time
    from history
    where song_id = {id}
    order by time
    """

    return song_history


# информация об исполнителе
def get_artist_information(id):
    artist_info = f"""
    select name, followers, photo, country, birthday
    from artists
    where artist_id = {id}
    """

    return artist_info


# жанры исполнителя
def get_artist_genres(id):
    artist_genres = f"""
    select g.genre_name
    from genres g join artists2genres ag on g.genre_id = ag.genre_id
    where ag.artist_id = {id}
    """

    return artist_genres


# история прослушивания исполнителя
def get_artist_history(id):
    artist_history = f"""
    select h.time
    FROM songs s join history h on s.song_id = h.song_id 
        join songs2artists sa on s.song_id = sa.song_id
        join artists a on sa.artist_id = a.artist_id
    where a.artist_id = {id}
    order by h.time
    """

    return artist_history





df = pd.read_sql(get_genres('', ''), engine)
#df = pd.read_sql(get_mising_genres('', ''), engine)
# # # df = pd.read_sql(get_artist_genres(2), engine)
# df = pd.read_sql(get_artist_genres(39), engine)

print(df)


# python page_reqs.py