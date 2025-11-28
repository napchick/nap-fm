import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from database.models import engine
import page_reqs as pr



# Создание кнопок с жанрами у артистов
def render_genre_buttons(tags):
    st.markdown(
        """
        <style>
        .genre-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .genre-btn {
            background-color: #111;
            color: white;
            padding: 8px 15px;
            border-radius: 10px;
            border: 1px solid #333;
            cursor: pointer;
            font-size: 15px;
        }
        .genre-btn:hover {
            background-color: #222;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    html = '<div class="genre-container">'
    for tag in tags:
        html += f"<button class='genre-btn'>{tag}</button>"
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

def render():
    st.set_page_config(page_icon="🎧", layout="wide")
    
    st.markdown("<a class='link' href='?page=home' target='_self' >← Back to the list</a>", 
                        unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    artist_id = st.query_params.get("artist_id")

    if not artist_id:
        st.error("Artist not specified")
        st.stop()

    else:
        # Преобразуем в int, если это число
        artist_id = int(artist_id)
        info = pd.read_sql(pr.get_artist_information(artist_id), engine)
        genres = pd.read_sql(pr.get_artist_genres(artist_id), engine)
        artist_history = pd.read_sql(pr.get_artist_history(artist_id), engine)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(info["photo"][0], width=400)
        with col2:
            #st.markdown(f"**{info['name'][0]}**")
            st.title(info['name'][0])
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"Birthday: {info['birthday'][0]}")
            st.markdown(f"Country: {info['country'][0]}")
            st.markdown(f"Followers: {info['followers'][0]}")
            st.markdown(f"Scrobbles: {len(artist_history)}")
            if len(genres) > 0:
                st.markdown("Tags:")
                render_genre_buttons(genres['genre_name'])

            # график показывающий как менялось кол-во прослушиваний за день
            st.write("""\n \n""")
            st.markdown("History of listening:")

            # Делаем график с историей прослушиваний
            artist_history["time"] = pd.to_datetime(artist_history["time"])
            df = artist_history.groupby(artist_history["time"].dt.date).size().reset_index(name="plays")

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
                    tickfont=dict(color="rgba(200,200,200,0.7)")
                ),
                yaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="rgba(200,200,200,0.7)"),
                    visible=False  # можно скрыть ось Y, как в оригинале
                ),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)