import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pycountry

import page_reqs as pr
from database.models import engine

with open("weekly_data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

begin = loaded['begin']
end = loaded['end']
scrobbles = loaded["scrobbles"]
scrobbles_prev = loaded['scrobbles_prev']
artists = loaded['artists']
artists_prev = loaded['artists_prev']
unique_artists = loaded['unique_artists']
# songs = loaded['songs']
# unique_songs = loaded['unique_songs']

top_songs = pd.DataFrame(loaded['top_songs'])
top_artists = pd.DataFrame(loaded['top_artists'])
top_genres = pd.DataFrame(loaded['top_genres'])
songs_per_decade = pd.DataFrame(loaded['songs_per_decade'])
songs_per_hours = pd.DataFrame(loaded['songs_per_hours'])
songs_per_countries = pd.DataFrame(loaded['songs_per_countries'])


def render():

    st.set_page_config(page_title=f"weekly", layout="wide")
    st.title(f"{begin.split('T')[0]} - {end.split('T')[0]}")
    st.markdown('---')
    col1, col2 = st.columns([1, 1])

    with col1:
        # ------------------------------- Количество прослушиваний ---------------------------
        diff_songs = scrobbles - scrobbles_prev
        if diff_songs > 0:
            diff = f"↑{(diff_songs / scrobbles_prev) * 100:.0f}% vs. last week"
        else:
            diff = f"↓{(abs(diff_songs) / scrobbles_prev) * 100:.0f}% vs. last week"
        st.markdown(
            f"""
            <div style="
                position: relative;
                text-align: left;
                color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                height: 200px;
                background-size: cover;
                background-position: center;
                background-color: #1db954;
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
                    <h4 style="margin: 0; font-size: 30px;">{scrobbles} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 20px;">{diff}</h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write('')
        # ---------------------------------- Топ песен -----------------------------------------
        st.markdown(
            f"""
            <div style="
                position: relative;
                text-align: left;
                color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                height: 500px;
                background-image: url('{top_songs['logo'].iloc[0]}');
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
                    <h4 style="margin: 0; font-size: 40px;">#1 {top_songs['title'].iloc[0]} - {top_songs['count_plays'].iloc[0]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;"> {top_songs['artist_name'].iloc[0]}</h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                position: relative;
                text-align: left;
                color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                height: 350px;
                background-color: #1db95433;
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding: 16px;
            ">
                <div style="
                    padding: 12px;
                    border-radius: 12px;
                ">
                    <h4 style="margin: 0; font-size: 35px;">#2 {top_songs['title'].iloc[1]} - {top_songs['count_plays'].iloc[1]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;">#3 {top_songs['title'].iloc[2]} - {top_songs['count_plays'].iloc[2]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;">#4 {top_songs['title'].iloc[3]} - {top_songs['count_plays'].iloc[3]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;">#5 {top_songs['title'].iloc[4]} - {top_songs['count_plays'].iloc[4]} scrobbles</h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    with col2:
        # ----------------------------------- Кол-во прослушанных артистов -------------------------------------
        diff_artists = artists - artists_prev
        if diff_artists > 0:
            diff = f"↑{(diff_artists / artists_prev) * 100:.0f}% vs. last week"
        else:
            diff = f'↓{(abs(diff_artists) / artists_prev) * 100:.0f}% vs. last weeks'
        st.markdown(
            f"""
            <div style="
                position: relative;
                text-align: left;
                color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                height: 200px;
                background-size: cover;
                background-position: center;
                background-color: #1db954;
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
                    <h4 style="margin: 0; font-size: 30px;">{artists} artists</h4>
                    <h4 style="margin: 0; font-size: 20px;">{diff}</h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write('')
        # ------------------------------- Топ артистов ----------------------------------------
        st.markdown(
            f"""
            <div style="
                position: relative;
                text-align: left;
                color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                height: 500px;
                background-image: url('{top_artists['photo'].iloc[0]}');
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
                    <h4 style="margin: 0; font-size: 40px;">#1 {top_artists['artist_name'].iloc[0]} - {top_artists['count_plays'].iloc[0]} scrobbles</h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                position: relative;
                text-align: left;
                color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                height: 350px;
                background-color: #1db95433;
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding: 16px;
            ">
                <div style="
                    padding: 12px;
                    border-radius: 12px;
                ">
                    <h4 style="margin: 0; font-size: 35px;">#2 {top_artists['artist_name'].iloc[1]} - {top_artists['count_plays'].iloc[1]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;">#3 {top_artists['artist_name'].iloc[2]} - {top_artists['count_plays'].iloc[2]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;">#4 {top_artists['artist_name'].iloc[3]} - {top_artists['count_plays'].iloc[3]} scrobbles</h4>
                    <h4 style="margin: 0; font-size: 35px;">#5 {top_artists['artist_name'].iloc[4]} - {top_artists['count_plays'].iloc[4]} scrobbles</h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # for i in range(1, 5):
        #     st.markdown(f"#{i+1} {top_artists['artist_name'].iloc[i]} - {top_artists['count_plays'].iloc[i]} scrobbles")
        


    st.title('*Charts*')
    charts_col1, charts_col2 = st.columns([1,1])
    with charts_col1:
        # ----------------------------- Распределение по десятилетиям ----------------------------
        st.markdown('Music by decade')
        st.markdown("---")

        # --- Создаем интерактивный график
        fig = px.bar(
            songs_per_decade,
            x="total_songs",
            y="song_year",
            orientation="h",
            color="total_songs",
            color_continuous_scale="mint",#teal
            hover_data=["title", "artist_name"],
        )

        fig.update_layout(
            # plot_bgcolor="#111",
            # paper_bgcolor="#111",
            font_color="white",
            yaxis_title="",
            xaxis_title="Количество песен",
            paper_bgcolor="black",
            plot_bgcolor="black",
        )


        # --- Вывод графика
        selected = st.plotly_chart(fig, use_container_width=True)

        # --- Выпадающий список (выбор десятилетия)
        selected_decade = st.selectbox(
            "Choose decade:",
            songs_per_decade["song_year"].sort_values(ascending=False)
        )

        # --- Находим песню для выбранного десятилетия
        row = songs_per_decade[songs_per_decade["song_year"] == selected_decade].iloc[0]

        st.markdown(f"### 🏆 Топ песня • {selected_decade}")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(row["logo"], width=100)
        with col2:
            st.markdown(f"**{row['title']}** by *{row['artist_name']}*")

    
    with charts_col2:

        # ----------------------------------- Распределение по часам ------------------------------------
        st.markdown('Listening clock')
        st.markdown("---")

        zeros = pd.DataFrame({'hour' : [i for i in range(1, 25)], 'count': [0 for i in range(24)]})
        df = pd.merge(songs_per_hours, zeros, on='hour', how='right')


        # Определяем "пиковый" час
        max_hour = df.loc[df["plays"].idxmax(), "hour"]
        max_plays = df["plays"].max()

        # Формируем подписи для hover
        df["label"] = df["hour"].apply(lambda x: f"{x:02d}:00")

        # Настройки графика
        fig = go.Figure()

        fig.add_trace(go.Barpolar(
            r=df["plays"],
            theta=df["hour"] * 15,         # 24 часа = 360°
            width=[10]*24,                 # немного меньше 15, чтобы был зазор между секторами
            marker_color=df["plays"],
            marker_colorscale="mint",
            opacity=0.9,
            hoverinfo="text+r",            # показываем только текст + значение
            text=df["label"],              # показываем время вместо угла
        ))

        # Настройки отображения
        fig.update_layout(
            template=None,
            polar=dict(
                bgcolor="black",
                angularaxis=dict(
                    tickvals=[0, 90, 180, 270],
                    ticktext=["00", "06", "12", "18"],
                    direction="clockwise",
                    rotation=90,
                    showline=False,
                    tickfont=dict(color="white", size=16)
                ),
                radialaxis=dict(showticklabels=False, ticks=''),
            ),
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="black",
            plot_bgcolor="black",
        )

        # Отображаем
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"""
        ### Busiest hour  
        **{max_hour:02d}:00**
        
        Scrobbles in busiest hour  
        **{max_plays}**
        """)
        st.write('')

    st.markdown("---")

    st.title('*Statistics*')
    stat_col1, stat_col2 = st.columns([1,1])

    with stat_col1:
# ----------------------------------- Топ стран по прослушиваниям ------------------------------------
        st.markdown('Countries')
        st.markdown('---')

        for i in range(5):
            country = pycountry.countries.get(alpha_2=songs_per_countries['country'].iloc[i])
            name = country.name
            flag = country.flag
            st.markdown(f"{i+1}: {flag} { name} - {songs_per_countries['count'].iloc[i]}")
    
    with stat_col2:
        # ---------------------------------------- Топ жанров ------------------------------------------

        st.markdown('Genres')
        st.markdown('---')

        for i in range(5):
            country = pycountry.countries.get(alpha_2=songs_per_countries['country'].iloc[i])
            name = country.name
            flag = country.flag
            st.markdown(f"{i+1}: {top_genres['new_genre'].iloc[i]} - {top_genres['count'].iloc[i]} plays")

# python weekly.py