import streamlit as st

import overview, library, artists, songs, reports, weekly


def render_top_menu(active_page):
    st.markdown("""
        <style>
        .menu-container {
            display: flex;
            gap: 35px;
            padding: 20px 40px;
            font-size: 22px;
            font-weight: 600;
        }

        .menu-item {
            color: white;
            text-decoration: none;
            position: relative;
            padding-bottom: 6px;
        }
                
        .menu-item:hover {
            color: white;
        }

        .menu-item:hover::after {
            color: white;
            content: "";
            position: absolute;
            left: 0;
            bottom: 0;
            height: 3px;
            width: 100%;
            background-color: #1DB954;
        }

        .menu-item-active {
            color: white;
            text-decoration: none;
            font-weight: 700;
            position: relative;
            padding-bottom: 6px;
        }

        .menu-item-active::after {
            content: "";
            position: absolute;
            left: 0;
            bottom: 0;
            height: 3px;
            width: 100%;
            background-color: #1DB954;
        }
        </style>
    """, unsafe_allow_html=True)

    html = '<div class="menu-container">'

    tabs = {
        "overview": "Overview",
        "library": "Library",
        "reports": "Reports",
        "weekly": "Weekly"
    }

    for key, label in tabs.items():
        if key == active_page:
            html += f'<a class="menu-item-active" href="?page={key}" target="_self" >{label}</a>'
        else:
            html += f'<a class="menu-item" href="?page={key}" target="_self" >{label}</a>'

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


page = st.query_params.get("page", "overview")



# делаем кнопки для переход на другую страницу
#render_sidebar_menu(tabs, page)
render_top_menu(page)


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
elif page == 'weekly':
    weekly.render()
else:
    st.write("Page not found")

# streamlit run router.py