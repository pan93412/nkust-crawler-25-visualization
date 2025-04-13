import streamlit as st

from components import get_database_client, platform_options

st.title("資料庫總覽")

database_client = get_database_client()

for platform_index, platform in enumerate(platform_options()):
    if platform_index > 0:
        st.divider()

    st.subheader(platform)

    db = database_client[platform]

    article_collection = db["articles"]
    comment_collection = db["comments"]
    reply_collection = db["replies"]

    col1, col2, col3 = st.columns(3)

    total_articles = article_collection.count_documents({})
    total_comments = comment_collection.count_documents({})
    total_replies = reply_collection.count_documents({})

    with col1:
        st.metric(label="文章數", value=total_articles)

    with col2:
        st.metric(label="留言數", value=total_comments)

    with col3:
        st.metric(label="回覆數", value=total_replies)

    col1, col2 = st.columns([2, 1])

    with col1:
        oldest_article = article_collection.find_one(sort=[("created_at", 1)])
        assert oldest_article is not None, "找不到文章"
        oldest_date = oldest_article["created_at"]

        newest_article = article_collection.find_one(sort=[("created_at", -1)])
        assert newest_article is not None, "找不到文章"
        newest_date = newest_article["created_at"]

        st.metric(
            label="時間跨度",
            value=f"{oldest_date.strftime('%Y-%m-%d')} ~ {newest_date.strftime('%Y-%m-%d')}",
        )
        st.metric(label="時間跨度天數", value=f"{newest_date - oldest_date}")

    with col2:
        st.metric(label="留言 / 文章比", value=f"{total_comments / total_articles:.2%}")
        st.metric(label="回覆 / 留言比", value=f"{total_replies / total_comments:.2%}")
