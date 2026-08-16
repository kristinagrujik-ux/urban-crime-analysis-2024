import streamlit as st
import pandas as pd
import altair as alt

# Поставување на страната
st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def get_sheets():
    return pd.ExcelFile(file_path).sheet_names

# Сидбар за избор на категорија
selected_sheet = st.sidebar.selectbox("Избери категорија:", get_sheets())
st.title(f"📊 {selected_sheet}")

@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)

df = load_data(selected_sheet)
BLUE_COLOR = '#1f77b4'

# --- 1. Кривични дела против државата ---
if "Кривични дела против државата" in selected_sheet:
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# --- 2. Организиран криминал ---
elif "Организиран" in selected_sheet or "организиран" in selected_sheet:
    st.dataframe(df, use_container_width=True)

# --- 3. Криумчарење на мигранти ---
elif "Криумчарење на мигранти" in selected_sheet:
    st.dataframe(df, use_container_width=True)

# --- 4. Недозволена трговија со дрога ---
elif "трговија" in selected_sheet or "Трговија" in selected_sheet:
    st.dataframe(df, use_container_width=True)

# --- 5. Вкупен криминалитет (Главни графикони) ---
elif "Вкупен криминалитет" in selected_sheet or "вкупен криминалитет" in selected_sheet:
    # Филтрирање на редовите каде што втората колона содржи СВР или ОСОСК
    clean_df = df[df.iloc[:, 1].astype(str).str.contains("СВР|ОСОСК", na=False)].dropna(subset=[df.columns[1]]).copy()
    
    sector_col = clean_df.columns[1]     # СВР Скопје, Битола итн.
    col_kriminal = clean_df.columns[3]   # Кривични дела
    col_storiteli = clean_df.columns[8]  # Сторители
    col_stapka = clean_df.columns[9]     # Стапка на криминал
    col_efikasnost = clean_df.columns[10]# Вкупна ефикасност
    
    # Чистење и конверзија во броеви (отстранување празни места доколку ги има)
    clean_df['Sector_Name'] = clean_df[sector_col].astype(str).str.strip()
    clean_df['Kriminal_Val'] = pd.to_numeric(clean_df[col_kriminal].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    clean_df['Storiteli_Val'] = pd.to_numeric(clean_df[col_storiteli].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    clean_df['Stapka_Val'] = pd.to_numeric(clean_df[col_stapka].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    clean_df['Efikasnost_Val'] = pd.to_numeric(clean_df[col_efikasnost].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    
    sector_order = clean_df['Sector_Name'].tolist()
    
    # Распоред на графикони
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Вкупен криминалитет за 2024 година по СВР**")
        chart1 = alt.Chart(clean_df).mark_bar(color=BLUE_COLOR).encode(
            x=alt.X('Sector_Name:N', sort=sector_order, title=None, axis=alt.Axis(labelAngle=-45)), 
            y=alt.Y('Kriminal_Val:Q', title="Кривични дела")
        ).properties(height=300)
        st.altair_chart(chart1, use_container_width=True)
        
    with col2:
        st.write("**Сторители**")
        chart2 = alt.Chart(clean_df).mark_bar(color='#b22222').encode(
            x=alt.X('Storiteli_Val:Q', title="Сторители"),
            y=alt.Y('Sector_Name:N', sort=sector_order, title=None)
        ).properties(height=300)
        text2 = chart2.mark_text(align='left', baseline='middle', dx=3).encode(text='Storiteli_Val:Q')
        st.altair_chart(chart2 + text2, use_container_width=True)

    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Стапка на криминалитет**")
        base_line = alt.Chart(clean_df).encode(
            x=alt.X('Sector_Name:N', sort=sector_order, title=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Stapka_Val:Q', title="Стапка")
        )
        line = base_line.mark_line(color=BLUE_COLOR, point=True, strokeWidth=3)
        text_line = base_line.mark_text(dy=-15).encode(text='Stapka_Val:Q')
        st.altair_chart((line + text_line).properties(height=300), use_container_width=True)
        
    with col4:
        st.write("**Вкупна ефикасност 2024 година**")
        chart4 = alt.Chart(clean_df).mark_bar(color=BLUE_COLOR).encode(
            x=alt.X('Efikasnost_Val:Q', title="Ефикасност (%)"),
            y=alt.Y('Sector_Name:N', sort=sector_order, title=None)
        ).properties(height=300)
        text4 = chart4.mark_text(align='left', baseline='middle', dx=3).encode(text='Efikasnost_Val:Q')
        st.altair_chart(chart4 + text4, use_container_width=True)
        
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

else:
    st.dataframe(df, use_container_width=True)
