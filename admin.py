# admin_dashboard.py

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🗂️ Voting Admin Dashboard")

VOTES_CSV = "Votes.csv"

if os.path.exists(VOTES_CSV):
    df = pd.read_csv(VOTES_CSV)

    st.subheader("📋 Vote Records")
    st.dataframe(df, use_container_width=True)

    total_votes = df['VOTE'].value_counts().reset_index()
    total_votes.columns = ['Party', 'Votes']
    st.bar_chart(total_votes.set_index('Party'))

    st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="Votes_Export.csv", mime="text/csv")
else:
    st.warning("No votes have been recorded yet.")
