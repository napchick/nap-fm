import streamlit as st

import overview, library, artists, songs, reports

page = st.query_params.get("page", "overview")

# возможные страницы для перехода
tabs = {
    "overview": "Overview",
    "library": "Library",
    "reports": "Reports"
}

# делаем кнопки для переход на другую страницу
cols = st.columns(len(tabs))

for i, (key, label) in enumerate(tabs.items()):
    if cols[i].button(label, key=f"menu_{key}"):
        st.query_params.page = key
        st.rerun()


if page == "overview":
    back = page
    overview.render()
elif page == "library":
    back = page
    library.render()
elif page == "artist":
    artists.render()
elif page == "song":
    songs.render()
elif page == 'reports':
    reports.render()
else:
    st.write("Page not found")

# streamlit run router.py