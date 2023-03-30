import pandas as pd
import streamlit as st
import pandas_profiling
import numpy as np
from streamlit_pandas_profiling import st_profile_report


# Create a wider layout
st.set_page_config(page_title="Rating Analysis", layout="centered")

st.title("Active Chess Players Above 2300 Elo")
st.markdown("Based on data scraped at website 2700chess.com")

# Load your DataFrame
@st.cache_data
def load_data():
    data = pd.read_csv('2700_data.csv')
    data.drop_duplicates(inplace=True)
    return data

# Load data
data = load_data()
data['Age'] = data['Age'].apply(lambda x: int(x))

# Create a sidebar for filters
st.sidebar.title("Filters")

titlesList = list(data.dropna().Title.unique())
titlesList.append('All')
titleFilter = st.sidebar.selectbox("Select Title", np.sort(titlesList))
if titleFilter != "All":
    data = data[data['Title'] == titleFilter]

#ageFilter = st.sidebar.selectbox("Select Age", np.sort(data.Age.unique()))
#if ageFilter:
#    data = data[data['Age'] == ageFilter]


pr = data.profile_report()

st_profile_report(pr)
