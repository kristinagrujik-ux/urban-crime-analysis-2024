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
    if "Недозволена" in sheet or "дрога" in sheet.lower():
        # Го читаме листот со две редови за заглавие како во Excel
        df = pd.read_excel(file_path, sheet_name=sheet, header=[1, 2])
        return df
    else:
        return pd.read_excel(file_path, sheet_name=sheet)

df = load_data(selected_sheet)

st.subheader("📈 Графикони")

if "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    # Чистење и подготовка на податоците за графиконите за дрога
    # Ги земаме секторите од првата колона
    sectors = df.iloc[1:, 0].values
    
    # Креираме чисти табели за цртање
    chart_data_kd = pd.DataFrame({
        '2024 година': pd.to_numeric(df.iloc[1:, 3], errors='coerce'),
        '2023 година': pd.to_numeric(df.iloc[1:, 4], errors='coerce')
    }, index=sectors)
    
    chart_data_st = pd.DataFrame({
        '2024 година': pd.to_numeric(df.iloc[1:, 7], errors='coerce'),
        '2023 година': pd.to_numeric(df.iloc[1:, 8], errors='coerce')
    }, index=sectors)
    
    # Филтрирање да го нема редот "Вкупно" ако постои
    chart_data_kd = chart_data_kd[~chart_data_kd.index.str.contains("Вкупно", case=False, na=False)]
    chart_data_st = chart_data_st[~chart_data_st.index.str.contains("Вкупно", case=False, na=False)]

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Недозволена трговија со дрога - Кривични дела (2024 vs 2023)**")
        st.bar_chart(chart_data_kd)
        
    with col2:
        st.write("**Недозволена трговија со дрога - Сторители (2024 vs 2023)**")
        st.bar_chart(chart_data_st)
        
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
