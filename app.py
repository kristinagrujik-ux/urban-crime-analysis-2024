import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def get_sheets():
    return pd.ExcelFile(file_path).sheet_names

selected_sheet = st.sidebar.selectbox("Избери категорија:", get_sheets())
st.title(f"📊 {selected_sheet}")

@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)

df = load_data(selected_sheet)
sector_col = df.columns[0]
df_chart = df[~df.iloc[:, 0].astype(str).str.contains("Вкупно", case=False, na=False)]

st.subheader("📈 Графикони")

# Логика за приказ:
# Ако е лист за Трговија со дрога, прикажи споредба (2024 vs 2023)
if "Недозволена" in selected_sheet:
    cols = df.select_dtypes(include=['number']).columns
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        st.bar_chart(df_chart.set_index(sector_col)[cols[0:2]])
    with col2:
        st.write("**Сторители (2024 vs 2023)**")
        st.bar_chart(df_chart.set_index(sector_col)[cols[3:5]])

# Инаку, прикажи ги стандардните графикони за Вкупен криминалитет
else:
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела**")
        st.bar_chart(df_chart.set_index(sector_col)["Кривични дела"])
    with col2:
        st.write("**Сторители**")
        st.bar_chart(df_chart.set_index(sector_col)["Сторители"])
        
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапка на криминал**")
        st.line_chart(df_chart.set_index(sector_col)["Стапка на криминал"])
    with col4:
        st.write("**Вкупна ефикасност 2024**")
        st.bar_chart(df_chart.set_index(sector_col)["Вкупна ефикасност 2024"])

st.subheader("📋 Детална табела")
st.dataframe(df)
