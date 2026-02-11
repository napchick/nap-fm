import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta, datetime

from database.models import engine
import page_reqs as pr



def render():
    # ------------------------
    st.set_page_config(page_title="nap.fm", page_icon="🎧", layout="wide")

    hist = pd.read_sql(pr.last10, engine)

    # стиль для надписей
    st.markdown("""
    <style>
    a.link {
        color: white;
        text-decoration: none;
        transition: color 0.2s;
    }
    a.link:hover {
        color: #1DB954; /* Spotify-зелёный при наведении */
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    # стиль для segmented_control
    st.markdown("""
        <style>
        /* Контейнер segmented control */
        [data-testid="stSegmentedControl"] {
            background-color: #121212; /* фон Spotify */
            border-radius: 10px;
            padding: 4px;
        }

        /* Кнопки */
        [data-testid="stSegmentedControl"] > div {
            color: #b3b3b3; /* серый текст */
            font-weight: 500;
            background-color: transparent;
            transition: all 0.2s ease;
        }

        /* Наведение */
        [data-testid="stSegmentedControl"] > div:hover {
            color: #1db954; /* зелёный Spotify */
        }

        /* Активная кнопка */
        [data-testid="stSegmentedControl"] [aria-checked="true"] {
            background-color: #1db954 !important;
            color: white !important;
            border-radius: 8px;
        }

        /* Текст активной кнопки */
        [data-testid="stSegmentedControl"] [aria-checked="true"] p {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)



    st.title("Staticstic information")

    # -------------------------------------- Статистические значения -----------------------------------------
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

    with col1:
        st.markdown(f"**SCROBBLES**")
        data = pd.read_sql(pr.get_scrobbles(''), engine)
        st.markdown(f"{data['count'][0]}")
    with col2:
        st.markdown(f"**ARTISTS**")
        data = pd.read_sql(pr.get_unique_artists(''), engine)
        #data = pd.read_sql(pr.unique_artists, engine)
        st.markdown(f"{data['artists_count'][0]}")


    # -------------------------------------- Последние прослушанные треки -----------------------------------------
    st.title("🎵 Recent tracks")

    for _, row in hist.iterrows():
        col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1.5])
        with col1:
            st.image(row["logo"], width=80)
        with col2:
            st.markdown(
                f"<a class='link' href='?page=song&song_id={row['id']}' target='_self'>{row['title']}</a>",
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(f"<a class='link' href='?page=artist&artist_id={row['artist_id']}' target='_self'>{row['name']}</a>",
                unsafe_allow_html=True)
        with col4:
            time_of_song = datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S.%f')
            time_of_song -= timedelta(hours=3)
            difference = datetime.now() - time_of_song
            minutes = difference.total_seconds() / 60
            if minutes < 60:
                st.write(f"{int(minutes)} minutes ago")
            elif minutes >= 60 and minutes < 1440:
                st.write(f"{int(minutes // 60)} hours ago")
            else:
                st.write(row["time"])
        st.divider()
    col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1.5])
    with col4:
        st.markdown("<a class='link' href='?page=library' target='_self' > More tracks </a>", 
                    unsafe_allow_html=True)

    # --------------------------------------------- Самые прослушиваемые треки -------------------------------------------

    st.title("🔥 Top tracks")

    # -------- Разбивка по периодам ---------
    period = st.segmented_control(
        "Choose period:",
        options=["last day", "last week", "last month", "last 3 months", "last 6 months", "last year", "all time"],
        default="last week",
        key='song_period'
    )

    top_tracks_period = None

    if period == 'last day':
        top_tracks_period = "'1 day'"
    elif period == 'last week':
        top_tracks_period = "'7 days'"
    elif period == 'last month':
        top_tracks_period = "'1 month'"
    elif period == 'last 3 months':
        top_tracks_period = "'3 months'"
    elif period == 'last 6 months':
        top_tracks_period = "'6 months'"
    elif period == 'last year':
        top_tracks_period = "'1 year'"


    if top_tracks_period is not None:
        top_songs = pd.read_sql(pr.get_top_songs_period(top_tracks_period), engine)
    else:
        #top_songs = pd.read_sql(pr.top_songs, engine)
        top_songs = pd.read_sql(pr.get_top_songs(''), engine)


    # ------------- Отображаем карточки в 5 колонках ----------------
    cols = st.columns(5)

    for i, col in enumerate(cols):
        if i < len(top_songs):
            row = top_songs.iloc[i]
            with col:
                st.markdown(
                    f"""
                    <div style="
                        position: relative;
                        text-align: left;
                        color: white;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                        height: 400px;
                        background-image: url('{row.logo}');
                        background-size: cover;
                        background-position: center;
                        display: flex;
                        flex-direction: column;
                        justify-content: flex-end;
                        padding: 16px;
                    ">
                        <div style="
                            background: linear-gradient(transparent, rgba(0,0,0,0.8));
                            padding: 12px;
                            border-radius: 12px;
                        ">
                            <h4 style="margin: 0; font-size: 20px;">{row.title}</h4>
                            <p style="margin: 4px 0 0; font-size: 16px; opacity: 0.9;">{row.artist_name}</p>
                            <p style="margin: 0; font-size: 14px; opacity: 0.8;">{row.count_plays} plays</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --------------------------------------------- Самые прослушиваемые артисты -------------------------------------------
    st.markdown("---")  # горизонтальная линия-разделитель
    st.title("🎤 Top artists")

    # -------- Разбивка по периодам ---------
    period_art = st.segmented_control(
        "Choose period:",
        options=["last day", "last week", "last month", "last 3 months", "last 6 months", "last year", "all time"],
        default="last week",
        key='artist_period'
    )

    top_artists_period = None

    if period_art == 'last day':
        top_artists_period = "'1 day'"
    elif period_art == 'last week':
        top_artists_period = "'7 days'"
    elif period_art == 'last month':
        top_artists_period = "'1 month'"
    elif period_art == 'last 3 months':
        top_artists_period = "'3 months'"
    elif period_art == 'last 6 months':
        top_artists_period = "'6 months'"
    elif period_art == 'last year':
        top_artists_period = "'1 year'"


    if top_artists_period is not None:
        top_artists = pd.read_sql(pr.get_top_artists_period(top_artists_period), engine)
    else:
        top_artists = pd.read_sql(pr.get_top_artists(''), engine)

    # -------Отображаем карточки в 5 колонках--------
    cols = st.columns(5)

    for i, col in enumerate(cols):
        if i < len(top_artists):
            row = top_artists.iloc[i]
            with col:
                st.markdown(
                    f"""
                    <div style="
                        position: relative;
                        text-align: left;
                        color: white;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                        height: 400px;
                        background-image: url('{row.photo}');
                        background-size: cover;
                        background-position: center;
                        display: flex;
                        flex-direction: column;
                        justify-content: flex-end;
                        padding: 16px;
                    ">
                        <div style="
                            background: linear-gradient(transparent, rgba(0,0,0,0.8));
                            padding: 12px;
                            border-radius: 12px;
                        ">
                            <h4 style="margin: 0; font-size: 20px;">{row.artist_name}</h4>
                            <p style="margin: 0; font-size: 14px; opacity: 0.8;">{row.count_plays} plays</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )



    # streamlit run overview.py
