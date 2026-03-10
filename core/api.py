import requests
import streamlit as st
import pandas as pd

BASE_REL = "https://report.idsecure.com.br:5000"

def get_headers():
    token = st.session_state.get("token")

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

@st.cache_data(show_spinner=True)
def fetch_logs(dt_start, dt_end, page_size=50000):

    headers = get_headers()

    link = (
        f"{BASE_REL}/api/v1/accesslog/logs?"
        f"pageSize={page_size}&pageNumber=1&sortOrder=desc&sortField=Time"
        f"&dtStart={dt_start}&dtEnd={dt_end}"
    )

    response = requests.get(link, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()["data"]["data"]

    return pd.DataFrame(data)