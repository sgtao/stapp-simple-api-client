import streamlit as st

"""
# Welcome to Streamlit!

Edit `/src` and `/tests` to customize this app to your heart's desire :heart:.
"""

# サイドバーのページに移動
# st.page_link("pages/example_app.py", label="Go to Example App")
st.page_link(
    "pages/11_simple_api_client.py",
    label="Go to simple_api_client App",
    icon="🚀",
)
# ログ表示ページへのリンク
st.page_link("pages/21_logs_viewer.py", label="View Logs", icon="📄")
