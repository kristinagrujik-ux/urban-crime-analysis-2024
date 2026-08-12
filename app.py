import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

st.title("📊 Национален Извештај за Урбан Криминалитет 2024")
file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def load_data():
    return pd.read_excel(file_path)

df = load_data()

# Клучни метрики
metrics = ["Кривични дела", "Сторители", "Стапка на криминал"]

st.subheader("📈 Споредбена анализа по СВР сектори")

# Креирање на три колони за графикони
col1, col2, col3 = st.columns(3)

with col1:
    st.write(f"**{metrics[0]}**")
    st.bar_chart(df.set_index(df.columns[0])[metrics[0]])

with col2:
    st.write(f"**{metrics[1]}**")
    st.bar_chart(df.set_index(df.columns[0])[metrics[1]])

with col3:
    st.write(f"**{metrics[2]}**")
    # Овде користиме line_chart за третата метрика
    st.line_chart(df.set_index(df.columns[0])[metrics[2]])

st.subheader("📋 Детална табела со сите податоци")
st.dataframe(df)
