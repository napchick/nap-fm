from database.models import History, Song, Artist, Genre, Song2Artist, Artist2Genre, engine
#from models import History, Song, Artist, Genre, Song2Artist, Artist2Genre
from sqlalchemy import select, func, BigInteger, text, join, delete, union, insert, update, desc, exists
from sqlalchemy.orm import Session


# определить id для песни
def get_song_id(title, artist):
    with Session(engine) as session:
        result = (
            session.query(Song.song_id)
            .join(Song2Artist, Song.song_id == Song2Artist.song_id)
            .join(Artist, Song2Artist.artist_id == Artist.artist_id)
            .filter(Song.title == title, Artist.name == artist)
        ).scalar()
        
        return result
    
# определить max song id
def get_max_song_id():
    with Session(engine) as session:
        result = (
            session.query(func.max(Song.song_id))
        ).scalar()

        return result
    

# определить id для артиста
def get_artist_id(artist):
    with Session(engine) as session:
        result = (
            session.query(Artist.artist_id)
            .filter(Artist.name == artist)
        ).scalar()

        return result

# определить id жанра
def get_genre_id(genre):
    with Session(engine) as session:
        result = (
            session.query(Genre.genre_id)
            .filter(Genre.genre_name == genre)
        ).scalar()
        
        return result


# проверка существования песни в таблице (+)
def is_song(title, artist):
    with Session(engine) as session:
        result = (
            session.query(func.count(Song.song_id))
            .join(Song2Artist, Song.song_id == Song2Artist.song_id)
            .join(Artist, Song2Artist.artist_id == Artist.artist_id)
            .filter(Song.title == title, Artist.name == artist)
        ).scalar()
        
        return result if result else 0
    

# проверка существования артиста в таблице
def is_artist(artist):
    with Session(engine) as session:
        result = (
            session.query(func.count(Artist.artist_id))
            .filter(Artist.name == artist)
        ).scalar()
        
        return result if result else 0
    

# проверка существования артиста в таблице с артист-жанр
def is_artist_in_genre(artist):
    with Session(engine) as session:
        result = (
            session.query(func.count(Artist2Genre.artist_id))
            .filter(Artist.name == artist)
        ).scalar()
        
        return result if result else 0
    

# проверка есть ли связка песня-артист
def is_artist_song_in_table(song_id):
    with Session(engine) as session:
        result = (
            session.query(func.count(Song2Artist.artist_id))
            .filter(Song2Artist.song_id == song_id)
        ).scalar()
        
        return result if result else 0


# проверка существования жанра в таблице
def is_genre(genre):
    with Session(engine) as session:
        result = (
            session.query(func.count(Genre.genre_id))
            .filter(Genre.genre_name == genre)
        ).scalar()
        
        return result if result else 0

# добавление жанра genre (+)
def set_genre(genre_name):
    with Session(engine) as session:
        # определяем id 
        count_genre = select(func.count(Genre.genre_id))
        result = session.execute(count_genre)
        genre_id = result.scalar()
        # добавляем жанр
        genre = Genre(genre_id=genre_id + 1, genre_name=genre_name)
        session.add(genre)
        session.commit()


# добавление соответствия genre-artist
def set_genre_artist(artist_id, genre_id):
    with Session(engine) as session:
        # добавляем связку артист-жанр
        genre_artist = Artist2Genre(genre_id=genre_id, artist_id=artist_id)
        session.add(genre_artist)
        session.commit()


# добавление артиста в artist (+)
def set_artist(artist_name, followers, popularity, photo, birthday, country): 
    with Session(engine) as session:
        # определяем id 
        count_artist = select(func.count(Artist.artist_id))
        result = session.execute(count_artist)
        artist_id = result.scalar()
        # добавляем артиста
        artist = Artist(artist_id=artist_id + 1, name=artist_name, followers=followers, popularity=popularity, 
                        photo=photo, birthday=birthday, country=country, country_code= '', tags='')
        session.add(artist)
        session.commit()


# добавление соответствия artist-song (+)
def set_song_artist(artist_id, song_id):
    with Session(engine) as session:
        # добавляем связку песня-артист
        song_artist = Song2Artist(song_id=song_id, artist_id=artist_id)
        session.add(song_artist)
        session.commit()


# добавить новую песню (+)
def set_song(title, duration, logo, release_date, popularity): 
    with Session(engine) as session:
        # определяем id песни
        count_song = select(func.count(Song.song_id))
        result = session.execute(count_song)
        song_id = result.scalar()
        # добавляем новую песню в таблицу
        song = Song(song_id=song_id + 1, title=title, duration=duration, logo=logo, release_date=release_date,
                     popularity=popularity)
        session.add(song)
        session.commit()


# добавить песню в историю
def set_history(song_id, time):
    with Session(engine) as session:
        # определяем id
        count_song = select(func.count(History.id))
        result = session.execute(count_song)
        history_id = result.scalar()
        # добавляем новую песню в таблицу
        song = History(id=history_id + 1, song_id=song_id, time=time)
        session.add(song)
        session.commit()


####
# Добавление песни
# 1. Получаем информацию о прослушанных песнях  python(+/-)
# 2. Проверить есть ли такая песня в таблице с песнями по названию и артисту  sql(+)
# 3.1 Если есть, то добавить в таюлицу с историей нужный id (-)
# 3.2.1 Если нет, то определить id новой песни sql(+)
# 3.2.2 Добавить информацию о песне в таблицу songs sql(+)
# 3.2.3 Добавить информацию об артисте/-тах в таблицу artists sql(+)
# 3.2.4.1 
# 3.2.4.2 Если текущего жанра нет, то создаем нужный в genres sql(+)
# 3.2.5 Добавить соответствие в таблицу связку artist2song sql(-)