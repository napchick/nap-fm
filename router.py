import streamlit as st

import overview, library, artists, songs, reports

def render_genre_buttons(pages):
    st.markdown(
        """
        <style>
        .page-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .page-btn {
            background-color: #111;
            color: white;
            padding: 8px 15px;
            border-radius: 10px;
            border: 1px solid #333;
            cursor: pointer;
            font-size: 15px;
        }
        .page-btn:hover {
            background-color: #222;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    html = '<div class="page-container">'
    for page in pages:
        html += f"<button class='page-btn'>{page}</button>"
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)

page = st.query_params.get("page", "overview")

# возможные страницы для перехода
tabs = {
    "overview": "Overview",
    "library": "Library",
    "reports": "Reports"
}



# делаем кнопки для переход на другую страницу
# render_genre_buttons(pages=tabs.keys())
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