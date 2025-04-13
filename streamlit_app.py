import streamlit as st

st.set_page_config(
    page_title="Visualization of MongoDB data",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation(
    pages=[
        st.Page("pages/database_overview.py", title="資料庫總覽", icon="📊"),
        st.Page("pages/content_list.py", title="文章瀏覽", icon="🔍"),
        st.Page("pages/comments_mining.py", title="留言探勘", icon="💬"),
    ]
)

pg.run()
