import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import timedelta, datetime

import page_reqs as pr
from database.models import engine




st.set_page_config(page_title="library.fm", page_icon="🎧", layout="wide")

# ------------------------- Стили отображения ------------------------------------------
# отображение ссылки на артиста/песню
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

# отрисовка bar в количестве прослушиваний
st.markdown("""
<style>
.artist-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: transparent;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.artist-info {
    display: flex;
    align-items: center;
    gap: 16px;
}
.artist-rank {
    color: white;
    font-weight: 600;
    width: 20px;
    text-align: center;
}
.artist-img {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
}
.artist-name {
    color: white;
    font-size: 1rem;
    font-weight: 600;
}
.song-name {
    color: white;
    font-size: 1rem;
    font-weight: 800;
}          
.play-bar {
    background-color: #1db95433; /* прозрачный зелёный фон */
    border-radius: 8px;
    height: 24px;
    position: relative;
    width: 300px;
    margin-left: 20px;
}
.play-bar-fill {
    background-color: #1db954; /* Spotify зелёный */
    height: 100%;
    border-radius: 8px;
    transition: width 0.4s ease;
}
.play-count {
    position: absolute;
    right: 10px;
    top: 3px;
    color: white;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# отрисовка ссылок на страницы
st.markdown("""
<style>
div[data-testid="stButton"] > button {
    background-color: #1DB954 !important;  /* Spotify green */
    color: black !important;
    border-radius: 6px;
    border: none;
    padding: 6px 12px;
    font-weight: 500;
    cursor: pointer;
}
div[data-testid="stButton"] > button:hover {
    background-color: #1ed760 !important;
}
div[data-testid="stButton"] > button:disabled {
    background-color: #15883e !important;
    color: #b3b3b3 !important;
}
</style>
""", unsafe_allow_html=True)



# ---------------------------------- Специальные функции -----------------------------------------
# функция для создания списка ссылок для прехода снизу 
def make_page_list(cur, total, max_buttons=9):
    if total <= max_buttons:
        return list(range(1, total + 1))
    half = max_buttons // 2
    left = max(1, cur - half)
    right = min(total, cur + half)
    if left == 1:
        right = min(total, max_buttons)
    elif right == total:
        left = max(1, total - max_buttons + 1)

    pages = list(range(left, right + 1))
    if pages[0] > 2:
        pages = [1, '...'] + pages
    elif pages[0] == 2:
        pages = [1] + pages
    if pages[-1] < total - 1:
        pages = pages + ['...', total]
    elif pages[-1] == total - 1:
        pages = pages + [total]
    return pages

# функция для отрисовки пагинации с помощью кнопок Streamlit
def render_pagination(current_page, total_pages, lib_type):
    page_list = make_page_list(current_page, total_pages)
    num_cols = len(page_list) + 2  # для Previous и Next
    cols = st.columns(num_cols)
    if lib_type == "Scrobbles":
        page_param = "scrobble_page"
    elif lib_type == "Artists":
        page_param = "artist_page"
    else:
        page_param = "song_page"


    # Page buttons
    for i, p in enumerate(page_list):
        with cols[i + 1]:
            if p == '...':
                st.write('...')
            elif p == current_page:
                st.button(str(p), disabled=True, key=f"page_current_{p}_{lib_type}")
            else:
                if st.button(str(p), key=f"page_{p}_{lib_type}"):
                    st.query_params[page_param] = str(p)
                    st.rerun()



st.title(f"Library")

qp = st.query_params

valid_options = ["Scrobbles", "Artists", "Songs"]

# Get lib_type from session_state if exists, else from query_params
if "library_type" not in st.session_state:
    lib_type_from_qp = qp.get("lib_type", ["Scrobbles"])[0]
    if lib_type_from_qp in valid_options:
        st.session_state.library_type = lib_type_from_qp
    else:
        st.session_state.library_type = "Scrobbles"

# элемент переключения
st.segmented_control(
    "",
    options=valid_options,
    key="library_type"
)

# Sync query_params to session_state.library_type if different
if qp.get("lib_type", [None])[0] != st.session_state.library_type:
    st.query_params["lib_type"] = st.session_state.library_type

lib_type = st.session_state.library_type

# Делаем заголовок и делим на колонки
st.markdown("---")

if lib_type == 'Scrobbles':
    st.markdown(f"**SCROBBLES**")
    data = pd.read_sql(pr.scrobbles, engine)
    st.markdown(f"{data['count'][0]}")
elif lib_type == 'Artists':
    st.markdown(f"**ARTISTS**")
    data = pd.read_sql(pr.unique_artists, engine)
    st.markdown(f"{data['artists_count'][0]}")
else:
    st.markdown(f"**SONGS**")
    data = pd.read_sql(pr.unique_songs, engine)
    st.markdown(f"{data['songs_count'][0]}")

st.markdown("")
col11, col12, col13 = st.columns([1, 8, 5])


with col12:
    if lib_type == 'Scrobbles':
        data = pd.read_sql(pr.all_songs, engine)

        ITEMS_PER_PAGE = 20

        # Считаем количество страниц
        scrobbles = pd.read_sql(pr.scrobbles, engine)
        total_items = scrobbles['count'][0]
        total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE > 0 else 0)


        # ======= Определяем текущую страницу =======
        try:
            current_page = int(qp.get("scrobble_page", ["1"])[0])
        except Exception:
            current_page = 1
        current_page = max(1, min(current_page, total_pages))  # защита от выхода за границы


        # Определяем текущий диапазон
        start = (current_page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_data = data.iloc[start:end]


        for _, row in page_data.iterrows():
            col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1.5])
            with col1:
                st.image(row["logo"], width=50)
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
                time_of_song += timedelta(hours=3)
                difference = datetime.now() - time_of_song
                minutes = difference.total_seconds() / 60
                if minutes < 60:
                    st.write(f"{int(minutes)} minutes ago")
                elif minutes >= 60 and minutes < 1440:
                    st.write(f"{int(minutes // 60)} hours ago")
                else:
                    st.write(row["time"])
            st.divider()

        # Пагинация с кнопками
        render_pagination(current_page, total_pages, lib_type)



    elif lib_type == 'Artists':
        data = pd.read_sql(pr.artists_stream, engine)
        max_plays = data['count_plays'][0] if not data.empty else 1

        ITEMS_PER_PAGE = 20

        # Считаем количество страниц
        artists = pd.read_sql(pr.unique_artists, engine)
        total_items = artists['artists_count'][0]
        total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE > 0 else 0)


        # ======= Определяем текущую страницу =======
        try:
            current_page = int(qp.get("artist_page", ["1"])[0])
        except Exception:
            current_page = 1
        current_page = max(1, min(current_page, total_pages))  # защита от выхода за границы


        # Определяем текущий диапазон
        start = (current_page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_data = data.iloc[start:end]


        for i, row in enumerate(page_data.itertuples(), start=(current_page - 1) * ITEMS_PER_PAGE + 1):
            width_percent = int((row.count_plays / max_plays) * 100)
            st.markdown(f"""
                <div class="artist-row">
                    <div class="artist-info">
                        <div class="artist-rank">{i}</div>
                        <img src="{row.photo}" class="artist-img">
                        <div class="artist-name">{row.artist_name}</div>
                    </div>
                    <div class="play-bar">
                        <div class="play-bar-fill" style="width: {width_percent}%;"></div>
                        <div class="play-count">{row.count_plays:,}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        # Пагинация с кнопками
        render_pagination(current_page, total_pages, lib_type)


    elif lib_type == 'Songs':
        data = pd.read_sql(pr.songs_agr, engine)
        max_plays = data['count_plays'][0] if not data.empty else 1

        ITEMS_PER_PAGE = 20

        # Считаем количество страниц
        songs = pd.read_sql(pr.unique_songs, engine)
        total_items = songs['songs_count'][0]
        total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE > 0 else 0)


        # ======= Определяем текущую страницу =======
        try:
            current_page = int(qp.get("song_page", ["1"])[0])
        except Exception:
            current_page = 1
        current_page = max(1, min(current_page, total_pages))  # защита от выхода за границы


        # Определяем текущий диапазон
        start = (current_page - 1) * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_data = data.iloc[start:end]


        for i, row in enumerate(page_data.itertuples(), start=(current_page - 1) * ITEMS_PER_PAGE + 1):
            width_percent = int((row.count_plays / max_plays) * 100)
            st.markdown(f"""
                <div class="artist-row">
                    <div class="artist-info">
                        <div class="artist-rank">{i}</div>
                        <img src="{row.logo}" class="artist-img">
                        <div class="song-name">{row.title}</div>
                        <div class="artist-name">{row.artist_name}</div>
                    </div>
                    <div class="play-bar">
                        <div class="play-bar-fill" style="width: {width_percent}%;"></div>
                        <div class="play-count">{row.count_plays:,}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)



        st.divider()
        # Пагинация с кнопками
        render_pagination(current_page, total_pages, lib_type)







