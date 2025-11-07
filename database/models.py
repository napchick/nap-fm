from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Date
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import streamlit as st
from datetime import datetime, date



# url = 'postgresql+psycopg2://neondb_owner:npg_8e7UwjHYWzRa@ep-summer-queen-adz2anyx-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=verify-ca&sslrootcert=isrgrootx1.pem'

# engine = create_engine(
#     'postgresql+psycopg2://neondb_owner:npg_8e7UwjHYWzRa@ep-summer-queen-adz2anyx-pooler.c-2.us-east-1.aws.neon.tech/neondb'
#     '?sslmode=verify-ca&sslrootcert=isrgrootx1.pem'
# )

url = st.secrets["connections"]["postgres"]["url"]
engine = create_engine(url)

async_session = sessionmaker(engine)



# Создание таблиц
class Base(DeclarativeBase):
    pass


class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(primary_key=True)
    time: Mapped[datetime] = mapped_column(DateTime)
    song_id: Mapped[int] = mapped_column(ForeignKey('songs.song_id'))

    
class Song(Base):
    __tablename__ = 'songs'

    song_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    duration: Mapped[int] = mapped_column()
    logo: Mapped[str] = mapped_column(String(50))
    release_date: Mapped[str] = mapped_column(String(20))
    popularity: Mapped[int] = mapped_column()


class Artist(Base):
    __tablename__ = 'artists'

    artist_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    followers: Mapped[int] = mapped_column()
    popularity: Mapped[int] = mapped_column()
    photo: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(20))
    country_code: Mapped[str] = mapped_column(String(5))
    birthday: Mapped[str] = mapped_column(String(20))
    tags: Mapped[str] = mapped_column(String(300))



class Genre(Base):
    __tablename__ = 'genres'

    genre_id: Mapped[int] = mapped_column(primary_key=True)
    genre_name: Mapped[str] = mapped_column(String(50))


class Song2Artist(Base):
    __tablename__ = 'songs2artists'

    song_id: Mapped[int] = mapped_column(ForeignKey('songs.song_id'), primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey('artists.artist_id'), primary_key=True)
    

class Artist2Genre(Base):
    __tablename__ = 'artists2genres'

    genre_id: Mapped[int] = mapped_column(ForeignKey('genres.genre_id'), primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey('artists.artist_id'), primary_key=True)



#Base.metadata.create_all(engine)