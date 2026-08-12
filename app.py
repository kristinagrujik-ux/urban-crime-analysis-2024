import streamlit as st
import pandas as pd
import altair as alt

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

st.subheader("📈 Графикони")

if "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    
    # Дефинирање на податоци за графиконите
    df_kd = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 3], '2023': valid_rows.iloc[:, 4]}).melt('Сектор', var_name='Година', value_name='Вредност')
    df_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 7], '2023': valid_rows.iloc[:, 8]}).melt('Сектор', var_name='Година', value_name='Вредност')
    
    # 1. Ред: Кривични дела (Бар + Пита)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_kd).mark_bar().encode(
            x=alt.X('Сектор:N', sort=None), y=alt.Y('Вредност:Q'), color='Година:N'
        ).properties(height=300), use_container_width=True)
    with col2:
        st.write("**Пита: Кривични дела (%)**")
        df_p1 = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Вредност': pd.to_numeric(valid_rows.iloc[:, 5], errors='coerce').abs()}).dropna()
        st.altair_chart(alt.Chart(df_p1).mark_arc().encode(theta='Вредност:Q', color='Сектор:N'), use_container_width=True)

    # 2. Ред: Сторители (Бар + Пита)
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_st).mark_bar().encode(
            x=alt.X('Сектор:N', sort=None), y=alt.Y('Вредност:Q'), color='Година:N'
        ).properties(height=300), use_container_width=True)
    with col4:
        st.write("**Пита: Сторители (%)**")
        df_p2 = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Вредност': pd.to_numeric(valid_rows.iloc[:, 9], errors='coerce').abs()}).dropna()
        st.altair_chart(alt.Chart(df_p2).mark_arc().encode(theta='Вредност:Q', color='Сектор:N'), use_container_width=True)

else:
    # Останати листови: 4 графикони (Криминал, Сторители, Стапка, Ефикасност)
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    # Логика за автоматско мапирање на колони
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Вкупни кривични дела**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(x=alt.X(f'{valid_rows.columns[0]}:N', sort=None), y=f'{valid_rows.columns[2]}:Q'), use_container_width=True)
    with c2:
        st.write("**Сторители**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(x=alt.X(f'{valid_rows.columns[0]}:N', sort=None), y=f'{valid_rows.columns[-1]}:Q'), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.write("**Стапка на криминал 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_line(point=True).encode(x=f'{valid_rows.columns[0]}:N', y=f'{valid_rows.columns[8]}:Q'), use_container_width=True)
    with c4:
        st.write("**Вкупна ефикасност 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(x=f'{valid_rows.columns[0]}:N', y=f'{valid_rows.columns[9]}:Q'), use_container_width=True)

st.subheader("📋 Детална табела")
st.dataframe(df)
