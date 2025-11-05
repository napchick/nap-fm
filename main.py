import streamlit as st
from . import overview
from pages import library, reports, test

st.set_page_config(page_title="My Music App", layout="wide")

# ================== СТИЛИ ==================
st.markdown("""
<style>
.navbar {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #121212;
    padding: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.nav-item {
    color: white;
    font-size: 1.1rem;
    text-decoration: none;
    margin: 0 15px;
    padding: 4px 8px;
    border-radius: 6px;
    transition: 0.3s;
}
.nav-item:hover {
    background-color: #1db954;
    color: black;
}
.nav-item.active {
    background-color: #1db954;
    color: black;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ================== НАВИГАЦИЯ ==================
PAGES = {
    "Overview": overview.render,
    "Reports": reports.render,
    "Library": test.render
}

# Определяем текущую страницу из query params
params = st.query_params
current_page = params.get("page", ["Overview"])
if isinstance(current_page, list):
    current_page = current_page[0]
if current_page not in PAGES:
    current_page = "Overview"

# Навигационная панель
def nav_link(name, emoji):
    active_class = "active" if name == current_page else ""
    # href должен обязательно содержать полный query param, иначе Streamlit не обновит страницу
    return f'<a class="nav-item {active_class}" href="/?page={name}" target="_self">{emoji} {name}</a>'

st.markdown(
    f"""
    <div class="navbar">
        {nav_link("Overview", "🏠")}
        |
        {nav_link("Reports", "📈")}
        |
        {nav_link("Library", "🎵")}
    </div>
    """,
    unsafe_allow_html=True
)

# ================== ОТРИСОВКА ТЕКУЩЕЙ СТРАНИЦЫ ==================
page_func = PAGES.get(current_page, overview.render)
page_func()



# streamlit run main.py