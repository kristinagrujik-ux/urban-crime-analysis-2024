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

# Наоѓање на колоните автоматски за да нема грешки
sector_col = df.columns[0]
efficiency_col = [col for col in df.columns if 'ефикасност' in str(col).lower()][0]
crime_col = [col for col in df.columns if 'кривични дела' in str(col).lower()][0]

# Интерактивни графикони
st.subheader("📈 Споредба на Ефикасност по СВР сектори")
st.bar_chart(df.set_index(sector_col)[efficiency_col])

st.subheader("📊 Распределба на Кривични Дела")
st.bar_chart(df.set_index(sector_col)[crime_col])
