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
    
    # Правилно земање на податоци за кривични дела и сторители (2024 vs 2023)
    df_kd = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 3], '2023': valid_rows.iloc[:, 4]}).melt('Сектор', var_name='Година', value_name='Вредност')
    df_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 6], '2023': valid_rows.iloc[:, 7]}).melt('Сектор', var_name='Година', value_name='Вредност')
    
    color_scale = alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])

    # 1. Ред: Кривични дела (Столпчиња еден до друг лево + Пита десно)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_kd).mark_bar().encode(
            x=alt.X('Сектор:N', sort=None, title='Сектор'),
            xOffset=alt.XOffset('Година:N'),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=color_scale)
        ).properties(height=300), use_container_width=True)
    with col2:
        st.write("**Пита: Кривични дела (%)**")
        df_p1 = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Вредност': pd.to_numeric(valid_rows.iloc[:, 5], errors='coerce').abs()}).dropna()
        st.altair_chart(alt.Chart(df_p1).mark_arc().encode(theta='Вредност:Q', color='Сектор:N'), use_container_width=True)

    # 2. Ред: Сторители (Столпчиња еден до друг лево + Пита десно)
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_st).mark_bar().encode(
            x=alt.X('Сектор:N', sort=None, title='Сектор'),
            xOffset=alt.XOffset('Година:N'),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=color_scale)
        ).properties(height=300), use_container_width=True)
    with col4:
        st.write("**Пита: Сторители (%)**")
        df_p2 = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Вредност': pd.to_numeric(valid_rows.iloc[:, 8], errors='coerce').abs()}).dropna()
        st.altair_chart(alt.Chart(df_p2).mark_arc().encode(theta='Вредност:Q', color='Сектор:N'), use_container_width=True)

else:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    for col in valid_rows.columns[1:]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    c_col = valid_rows.columns[2] if len(valid_rows.columns) > 2 else valid_rows.columns[1]
    s_col = valid_rows.columns[-1] if len(valid_rows.columns) > 1 else None
    st_col = valid_rows.columns[8] if len(valid_rows.columns) > 8 else s_col
    ef_col = valid_rows.columns[9] if len(valid_rows.columns) > 9 else s_col

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупни кривични дела**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y(f'{c_col}:Q', title='Број', axis=alt.Axis(format='d')),
            color=alt.Color(f'{sector_col}:N', legend=None)
        ).properties(height=300), use_container_width=True)

    with col2:
        if s_col:
            st.write("**Сторители**")
            st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(
                x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
                y=alt.Y(f'{s_col}:Q', title='Број', axis=alt.Axis(format='d')),
                color=alt.Color(f'{sector_col}:N', legend=None)
            ).properties(height=300), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапка на криминал 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_line(point=True).encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y(f'{st_col}:Q', title='Стапка'),
            color=alt.value('#e45756')
        ).properties(height=300), use_container_width=True)

    with col4:
        st.write("**Вкупна ефикасност 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y(f'{ef_col}:Q', title='Процент'),
            color=alt.Color(f'{sector_col}:N', legend=None)
        ).properties(height=300), use_container_width=True)

st.subheader("📋 Детална табела")
st.dataframe(df)
