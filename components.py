import streamlit as st
from pymongo import MongoClient
import os

@st.cache_resource
def get_database_client() -> MongoClient:
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        return client
    except Exception as e:
        st.error(f"連線到 MongoDB 時發生錯誤: {e}")
        st.stop()



def platform_options() -> list[str]:
    return ["dcard", "ptt", "yahoo"]
