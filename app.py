import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

st.title("📊 Национален Извештај за Урбан Криминалитет 2024")
st.markdown("Интерактивен дашборд со визуелизации по СВР сектори.")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def load_data():
    return pd.read_excel(file_path)

df = load_data()

# Филтер за СВР сектори
sectors = df.iloc[:, 0].dropna().tolist()
selected_sector = st.sidebar.selectbox("Избери СВР Сектор:", sectors)

# Приказ на податоци за избраниот сектор
st.subheader(f"Анализа за: {selected_sector}")
sector_data = df[df.iloc[:, 0] == selected_sector]
st.dataframe(sector_data)

# Интерактивен графикон со столбчиња (Вкупна ефикасност по сектори)
st.subheader("📈 Споредба на Ефикасност по СВР сектори")
chart_data = df.set_index(df.columns[0])['Вкупна ефикасност 2024']
st.bar_chart(chart_data)

st.subheader("📊 Распределба на Кривични Дела")
st.bar_chart(df.set_index(df.columns[0])['Кривични дела'])
