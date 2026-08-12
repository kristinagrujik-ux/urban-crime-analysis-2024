import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

st.title("📊 Национален Извештај за Урбан Криминалитет 2024")
file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def load_data():
    return pd.read_excel(file_path)

df = load_data()

# Подготовка на податоци без редот "Вкупно"
df_chart = df[~df.iloc[:, 0].astype(str).str.contains("Вкупно", case=False, na=False)]

# Автоматско наоѓање на имињата на колоните за да нема грешки
sector_col = df.columns[0]
crime_col = [col for col in df.columns if 'кривични дела' in str(col).lower()][0]
storiteli_col = [col for col in df.columns if 'сторители' in str(col).lower()][0]
stapka_col = [col for col in df.columns if 'стапка' in str(col).lower()][0]
efikasnost_col = [col for col in df.columns if 'ефикасност' in str(col).lower()][0]

st.subheader("📈 Споредбена анализа по СВР сектори")

# Прв ред со два графикона
col1, col2 = st.columns(2)

with col1:
    st.write("**Кривични дела**")
    st.bar_chart(df_chart.set_index(sector_col)[crime_col])

with col2:
    st.write("**Сторители**")
    st.bar_chart(df_chart.set_index(sector_col)[storiteli_col])

# Втор ред со два графикона
col3, col4 = st.columns(2)

with col3:
    st.write("**Стапка на криминал**")
    st.line_chart(df_chart.set_index(sector_col)[stapka_col])

with col4:
    st.write("**Вкупна ефикасност 2024**")
    st.bar_chart(df_chart.set_index(sector_col)[efikasnost_col])

st.subheader("📋 Детална табела со сите податоци")
st.dataframe(df)

