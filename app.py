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
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР", na=False)].copy()
    
    for col_idx in [3, 4, 7, 8]:
        valid_rows.iloc[:, col_idx] = pd.to_numeric(valid_rows.iloc[:, col_idx], errors='coerce')

    sector_name = valid_rows.columns[0]

    # Подготовка на податоци за Кривични дела (трансформација во долг формат за групирани столпчиња)
    df_kd = pd.DataFrame({
        'Сектор': valid_rows.iloc[:, 0],
        '2024 година': valid_rows.iloc[:, 3],
        '2023 година': valid_rows.iloc[:, 4]
    }).melt('Сектор', var_name='Година', value_name='Вредност')

    # Подготовка на податоци за Сторители
    df_st = pd.DataFrame({
        'Сектор': valid_rows.iloc[:, 0],
        '2024 година': valid_rows.iloc[:, 7],
        '2023 година': valid_rows.iloc[:, 8]
    }).melt('Сектор', var_name='Година', value_name='Вредност')

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        chart_kd = alt.Chart(df_kd).mark_bar().encode(
            x=alt.X('Година:O', title=''),
            xOffset=alt.XOffset('Година:O'),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8']))
        ).properties(height=350)
        st.altair_chart(chart_kd, use_container_width=True)
        
    with col2:
        st.write("**Сторители (2024 vs 2023)**")
        chart_st = alt.Chart(df_st).mark_bar().encode(
            x=alt.X('Година:O', title=''),
            xOffset=alt.XOffset('Година:O'),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8']))
        ).properties(height=350)
        st.altair_chart(chart_st, use_container_width=True)
        
else:
    sector_col = df.columns[0]
    df_chart = df[~df.iloc[:, 0].astype(str).str.contains("Вкупно", case=False, na=False)]
    
    c_kol = next((c for c in df.columns if 'кривични дела' in str(c).lower()), df.columns[1] if len(df.columns) > 1 else None)
    s_kol = next((c for c in df.columns if 'сторители' in str(c).lower()), df.columns[7] if len(df.columns) > 7 else None)
    st_kol = next((c for c in df.columns if 'стапка' in str(c).lower()), df.columns[8] if len(df.columns) > 8 else None)
    ef_kol = next((c for c in df.columns if 'ефикасност' in str(c).lower()), df.columns[9] if len(df.columns) > 9 else None)

    col1, col2 = st.columns(2)
    with col1:
        if c_kol:
            st.write(f"**{c_kol}**")
            st.bar_chart(df_chart.set_index(sector_col)[c_kol])
    with col2:
        if s_kol:
            st.write(f"**{s_kol}**")
            st.bar_chart(df_chart.set_index(sector_col)[s_kol])
        
    col3, col4 = st.columns(2)
    with col3:
        if st_kol:
            st.write(f"**{st_kol}**")
            st.line_chart(df_chart.set_index(sector_col)[st_kol])
    with col4:
        if ef_kol:
            st.write(f"**{ef_kol}**")
            st.bar_chart(df_chart.set_index(sector_col)[ef_kol])

st.subheader("📋 Детална табела")
st.dataframe(df)
