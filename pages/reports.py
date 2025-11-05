import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import pycountry

import page_reqs as pr
from database.models import engine

#def render():

glob_col1, glob_col2 = st.columns([1, 1])

#-------------------------------------- Распределение по десятилетиям -----------------------------------------------

with glob_col1:
    st.set_page_config(page_title="Music by Decade", layout="wide")
    st.title("🎶 Music by decade")

    tracks_per_years_period = None

    period = st.segmented_control(
        "Choose period:",
        options=["last day", "last week", "last month", "last 3 months", "last 6 months", "last year", "all time"],
        default="last week",
        key='years_period'
    )

    if period == 'last day':
        tracks_per_years_period = "'1 day'"
    elif period == 'last week':
        tracks_per_years_period = "'7 days'"
    elif period == 'last month':
        tracks_per_years_period = "'1 month'"
    elif period == 'last 3 months':
        tracks_per_years_period = "'3 months'"
    elif period == 'last 6 months':
        tracks_per_years_period = "'6 months'"
    elif period == 'last year':
        tracks_per_years_period = "'1 year'"


    if tracks_per_years_period is not None:
        whe = f'WHERE h.time::timestamp >= now() - interval {tracks_per_years_period}'
    else:
        whe = ''
    df = pd.read_sql(pr.get_songs_per_year_period(whe), engine)


    # --- Создаем интерактивный график
    fig = px.bar(
        df,
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
        df["song_year"].sort_values(ascending=False)
    )

    # --- Находим песню для выбранного десятилетия
    row = df[df["song_year"] == selected_decade].iloc[0]

    st.markdown(f"### 🏆 Топ песня • {selected_decade}")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(row["logo"], width=100)
    with col2:
        st.markdown(f"**{row['title']}** by *{row['artist_name']}*")


#-------------------------------------- Распределение по часам ---------------------------------------------------

with glob_col2:
    st.title("🕒 Listening clock")

    period = st.segmented_control(
        "Choose period:",
        options=["last day", "last week", "last month", "last 3 months", "last 6 months", "last year", "all time"],
        default="last week",
        key='hours_period'
    )

    if period == 'last day':
        tracks_per_hours_period = "'1 day'"
    elif period == 'last week':
        tracks_per_hours_period = "'7 days'"
    elif period == 'last month':
        tracks_per_hours_period = "'1 month'"
    elif period == 'last 3 months':
        tracks_per_hours_period = "'3 months'"
    elif period == 'last 6 months':
        tracks_per_hours_period = "'6 months'"
    elif period == 'last year':
        tracks_per_hours_period = "'1 year'"


    if tracks_per_hours_period is not None:
        whe = f'WHERE time::timestamp >= now() - interval {tracks_per_hours_period}'
    else:
        whe = ''
    df = pd.read_sql(pr.get_songs_per_hours(whe), engine)

    zeros = pd.DataFrame({'hour' : [i for i in range(1, 25)], 'count': [0 for i in range(24)]})
    df = pd.merge(df, zeros, on='hour', how='right')


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
    #col1, col2 = st.columns([2, 1])
    #with col1:
    st.plotly_chart(fig, use_container_width=True)
    #with col2:
    st.markdown(f"""
    ### Busiest hour  
    **{max_hour:02d}:00**
    
    Scrobbles in busiest hour  
    **{max_plays}**
    """)

#------------------------------------ Распределение артистов по странам -------------------------------------------------

st.title("🗺️ Artists geography")


# пример данных
df = pd.read_sql(pr.artists_per_country, engine)

# переводим ISO-2 → ISO-3
def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

df["iso3"] = df["country"].apply(iso2_to_iso3)

all_countries = pd.DataFrame({
    "iso3": [c.alpha_3 for c in pycountry.countries],
    "country_name": [c.name for c in pycountry.countries]
})

# 🔹 Объединяем с твоими данными (outer join — сохраняет все страны)
merged = all_countries.merge(df[["iso3", "count"]], on="iso3", how="left")

# теперь строим карту
fig = px.choropleth(
    merged,
    locations="iso3",
    locationmode="ISO-3",
    color="count",
    #hover_name="artist_name",
    color_continuous_scale="mint",
    title="🎵 Топ артисты по странам",
)
fig.update_layout(
    geo=dict(
        showframe=True,
        showcoastlines=True,
        showcountries=True,
        projection_type="natural earth",
        bgcolor="black",
        
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    width=900,
    height=600,
    margin=dict(l=0, r=0, t=50, b=0),
)


st.plotly_chart(fig, use_container_width=True)

#------------------------------------- Распределение песен по странам -------------------------------------------------
st.title("🗺️ Songs geography")

# пример данных
df = pd.read_sql(pr.songs_per_country, engine)

# переводим ISO-2 → ISO-3
def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

df["iso3"] = df["country"].apply(iso2_to_iso3)

all_countries = pd.DataFrame({
    "iso3": [c.alpha_3 for c in pycountry.countries],
    "country_name": [c.name for c in pycountry.countries]
})

# 🔹 Объединяем с твоими данными (outer join — сохраняет все страны)
merged = all_countries.merge(df[["iso3", "count"]], on="iso3", how="left")

# теперь строим карту
fig = px.choropleth(
    merged,
    locations="iso3",
    locationmode="ISO-3",
    color="count",
    #hover_name="artist_name",
    color_continuous_scale="mint",
    title="🎵 Топ артисты по странам",
)
fig.update_layout(
    geo=dict(
        showframe=True,
        showcoastlines=True,
        showcountries=True,
        projection_type="natural earth",
        bgcolor="black",
        
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    width=900,
    height=600,
    margin=dict(l=0, r=0, t=50, b=0),
)


st.plotly_chart(fig, use_container_width=True)
