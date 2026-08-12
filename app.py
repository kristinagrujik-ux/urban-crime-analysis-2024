import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def get_sheet_names():
    xls = pd.ExcelFile(file_path)
    return xls.sheet_names

sheet_names = get_sheet_names()
selected_sheet = st.sidebar.selectbox("Избери категорија на извештај:", sheet_names)

st.title(f"📊 Извештај: {selected_sheet}")

@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)

df = load_data(selected_sheet)

if not df.empty:
    df_chart = df[~df.iloc[:, 0].astype(str).str.contains("Вкупно", case=False, na=False)]
    sector_col = df.columns[0]
    
    st.subheader("📈 Споредбена анализа по СВР сектори")
    
    # Ред 1: Кривични дела и Вкупна ефикасност 2024
    col1, col2 = st.columns(2)
    with col1:
        if "Кривични дела" in df.columns:
            st.write("**Кривични дела**")
            st.bar_chart(df_chart.set_index(sector_col)["Кривични дела"])
            
    with col2:
        # Бараме колона што содржи "ефикасност" во името
        efikasnost_col = next((col for col in df.columns if 'ефикасност' in str(col).lower()), None)
        if efikasnost_col:
            st.write(f"**{efikasnost_col}**")
            st.bar_chart(df_chart.set_index(sector_col)[efikasnost_col])

    # Ред 2: Стапка на криминал (линиски) и Сторители
    col3, col4 = st.columns(2)
    with col3:
        # Бараме колона што содржи "стапка" во името
        stapka_col = next((col for col in df.columns if 'стапка' in str(col).lower()), None)
        if stapka_col:
            st.write(f"**{stapka_col}**")
            st.line_chart(df_chart.set_index(sector_col)[stapka_col])
            
    with col4:
        if "Сторители" in df.columns:
            st.write("**Сторители**")
            st.bar_chart(df_chart.set_index(sector_col)["Сторители"])

    st.subheader("📋 Детална табела со податоци")
    st.dataframe(df)
else:
    st.warning("Избраниот лист е празен.")
