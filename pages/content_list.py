from bson import ObjectId
import hanlp.pretrained
import pandas as pd
import streamlit as st
import hanlp
import cleaner
import nlp

from pymongo.collection import Collection

from components import get_database_client, platform_options
from models import ArticleMongoModel, CommentMongoModel, article_from_mongo_model

st.title("MongoDB 資料總覽")

selected_platform = st.sidebar.selectbox("選擇平台", platform_options())
st.session_state["selected_platform"] = selected_platform

client = get_database_client()
db = client[selected_platform]
articles: Collection[ArticleMongoModel] = db["articles"]

total_articles = articles.count_documents({})

# Pagination controls
items_per_page = st.sidebar.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=0)
total_pages = (total_articles + items_per_page - 1) // items_per_page
current_page = st.sidebar.number_input(
    "頁數", min_value=1, max_value=total_pages, value=1, step=1
)

# Calculate skip value for pagination
skip = (current_page - 1) * items_per_page

found_articles_db = articles.find().skip(skip).limit(items_per_page).to_list()
found_articles_df = pd.DataFrame(
    [article_from_mongo_model(article) for article in found_articles_db]
)
found_articles_df.set_index("_id", inplace=True)
found_articles_df = found_articles_df[["title", "created_at", "article_id"]]

with st.expander("文章列表", expanded=True):
    # Display paginated results
    df_state = st.dataframe(
        found_articles_df,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Display pagination info
    st.caption(
        f"顯示第 {skip + 1} 至 {min(skip + items_per_page, total_articles)} 筆，共 {total_articles} 筆"
    )

selection = df_state.get("selection")
if selection and "rows" in selection and len(selection["rows"]) > 0:
    id = selection["rows"][0]
    article_id = found_articles_df.index[id]

    st.session_state["article_id"] = found_articles_df.loc[article_id]["article_id"]

    article = articles.find_one({"_id": ObjectId(article_id)})
    if article is None:
        st.error("找不到文章")
        st.stop()

    comments_collection: Collection[CommentMongoModel] = db["comments"]

    assert "_id" in article
    total_count_comments = comments_collection.count_documents(
        {"article_id": article["_id"]}
    )

    st.write(f"## {article['title']}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="發布時間", value=article["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        )
    with col2:
        st.metric(label="留言數", value=total_count_comments)

    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        st.link_button("查看原文", article["url"])
    with col2:
        if st.button("留言探勘"):
            st.switch_page("pages/comments_mining.py")

    with st.expander("文章內容", expanded=False):
        st.text(article["content"])

    # 斷詞 + 文字雲
    st.sidebar.divider()
    show_word_cloud = st.sidebar.checkbox("顯示文字雲")

    if show_word_cloud:
        with st.expander("文字雲", expanded=False):
            nlp_instance = nlp.Nlp()
            word_counts = nlp_instance.word_count(article["content"])
            word_cloud = nlp_instance.word_cloud(word_counts)
            st.image(word_cloud)
