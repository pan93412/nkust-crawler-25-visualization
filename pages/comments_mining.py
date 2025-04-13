import pandas as pd
import streamlit as st

from pymongo.collection import Collection

from components import get_database_client, platform_options
from models import ArticleMongoModel, CommentMongoModel, comment_from_mongo_model
import nlp

st.title("留言探勘")

current_selected_platform_id = 0
current_article_id: str | None = None

if "selected_platform" in st.session_state:
    current_selected_platform = st.session_state["selected_platform"]
    current_selected_platform_id = platform_options().index(current_selected_platform)

if "article_id" in st.session_state:
    current_article_id = st.session_state["article_id"]

selected_platform = st.sidebar.selectbox("選擇平台", platform_options(), index=current_selected_platform_id)
article_id = st.sidebar.text_input("文章 ID", value=current_article_id)

client = get_database_client()
db = client[selected_platform]
article_collection: Collection[ArticleMongoModel] = db["articles"]
comments_collection: Collection[CommentMongoModel] = db["comments"]

if not article_id or article_id == "":
    st.error("請輸入文章 ID！")
    st.stop()

article = article_collection.find_one({"article_id": article_id})

if not article:
    st.error(f"找不到 ID 為 {article_id} 的文章！")
    st.stop()

st.write(f"### {article['title']}")
assert "_id" in article, "article 必須包含 _id 欄位"

total_comments_count = comments_collection.count_documents({"article_id": article["_id"]})
positive_comments_count = comments_collection.count_documents({"article_id": article["_id"], "reaction_type": "+1"})
negative_comments_count = comments_collection.count_documents({"article_id": article["_id"], "reaction_type": "-1"})

if total_comments_count == 0:
    st.warning("此篇文章沒有任何留言！")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="留言數", value=comments_collection.count_documents({"article_id": article["_id"]}))
with col2:
    ratio = positive_comments_count / total_comments_count
    st.metric(label="推文比例", value=f"{ratio:.2%}")
with col3:
    ratio = negative_comments_count / total_comments_count
    st.metric(label="噓文比例", value=f"{ratio:.2%}")

# Pagination controls
items_per_page = st.sidebar.selectbox("每頁顯示筆數", [10, 20, 50, 100], index=0)
total_pages = (total_comments_count + items_per_page - 1) // items_per_page
current_page = st.sidebar.number_input("頁數", min_value=1, max_value=total_pages, value=1, step=1)

# Calculate skip value for pagination
skip = (current_page - 1) * items_per_page

comments = comments_collection.find({"article_id": article["_id"]}).skip(skip).limit(items_per_page)
comments_df = pd.DataFrame([comment_from_mongo_model(comment) for comment in comments])

comments_display_df = comments_df[["reaction_type", "content", "author", "likes", "dislikes", "created_at"]]

st.dataframe(comments_display_df)
st.caption(f"顯示第 {skip + 1} 至 {min(skip + items_per_page, total_comments_count)} 筆，共 {total_comments_count} 筆")

st.divider()

with st.expander("這一頁留言的關鍵字"):
    nlp_instance = nlp.Nlp()

    # 將所有留言彙整成一個很大的字串
    all_comments_content = " ".join(comments_df["content"].tolist())
    word_counts = nlp_instance.word_count(all_comments_content)
    word_cloud = nlp_instance.word_cloud(word_counts)

    st.image(word_cloud)
