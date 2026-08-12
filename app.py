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

# Проверка според избран лист
if "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    # За трговија со дрога - ги земаме нумеричките колони по индекс за да има графикони
    num_cols = [c for c in df.select_dtypes(include=['number']).columns if 'unnamed' not in str(c).lower()]
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Споредбени податоци - Дел 1**")
        if len(num_cols) >= 2:
            st.bar_chart(df_chart.set_index(sector_col)[num_cols[0:2]])
    with col2:
        st.write("**Споредбени податоци - Дел 2**")
        if len(num_cols) >= 4:
            st.bar_chart(df_chart.set_index(sector_col)[num_cols[2:4]])
else:
    # За Вкупен криминалитет - автоматско пронаоѓање на колоните по клучни зборови за да нема KeyError
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
