import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from database.models import engine
import page_reqs as pr


def render():
    st.set_page_config(page_icon="🎧", layout="wide")

    st.markdown("<a class='link' href='?page=library' target='_self' >← Back to the list</a>", 
                        unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    song_id = st.query_params.get("song_id")

    if not song_id:
        st.error("Song not specified")
        st.stop()

    else:
        # Преобразуем в int, если это число
        song_id = int(song_id)
        data = pd.read_sql(pr.get_song_information(song_id), engine)
        song_history = pd.read_sql(pr.get_song_history(song_id), engine)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(data["logo"][0], width=300)
        with col2:
            #st.markdown(f"***{data['name'][0]}***")
            st.title(f"{data['name'][0]} -- {data['title'][0]}")
            st.markdown("<hr>", unsafe_allow_html=True)
            #st.markdown(f"**{data['title'][0]}**")
            minutes = int(data['duration'][0] / 1000 // 60)
            seconds = int(data['duration'][0] / 1000 % 60)
            st.markdown(f"Duration: {minutes}:{seconds:02d}")
            st.markdown(f"Release date: {data['release_date'][0]}")
            st.markdown(f"Scrobbles: {len(song_history)}")

            # Делаем график с историей прослушиваний
            song_history["time"] = pd.to_datetime(song_history["time"])
            df = song_history.groupby(song_history["time"].dt.date).size().reset_index(name="plays")


            # Создание графика
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df["time"],
                y=df["plays"],
                mode="lines",
                line=dict(color="#1DB954", width=2.5),  # Spotify green
                fill="tozeroy",  # закрашивает под графиком
                fillcolor="rgba(29,185,84,0.15)",  # прозрачный зелёный
                #hovertemplate="%{x}<br><b>%{y}</b> plays<extra></extra>"
            ))

            fig.add_trace(go.Scatter(
                x=df.query("plays > 0")["time"],
                y=df.query("plays > 0")["plays"],
                mode="markers",
                marker=dict(
                    color="#1DB954",
                    size=8,
                    line=dict(width=2, color="#ffffff")
                ),
                hovertemplate="%{x|%d %b %Y}<br><b>%{y}</b> plays<extra></extra>",
                #name="Дни с прослушиваниями"
            ))

            # Настройки внешнего вида
            fig.update_layout(
                template="plotly_dark",
                height=350,
                margin=dict(l=20, r=20, t=20, b=40),
                plot_bgcolor="#000000",
                paper_bgcolor="#000000",
                showlegend=False,
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="rgba(200,200,200,0.7)"),
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="rgba(200,200,200,0.7)"),
                    visible=False  # можно скрыть ось Y, как в оригинале
                ),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        