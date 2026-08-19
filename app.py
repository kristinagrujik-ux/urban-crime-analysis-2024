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
GREEN_COLOR = '#2ca02c'

# --- 1. Кривични дела против државата ---
if "Кривични дела против државата" in selected_sheet:
    st.subheader("Кривични дела: 2024 vs 2023 година")
    
    # Подготовка на податоците со точни вредности за секоја година
    chart_data = pd.DataFrame([
        {"Кривични дела": "Предизвикување омраза и нетрпеливост", "2024 година": 10, "2023 година": 2},
        {"Кривични дела": "Учество во странска војска и полиција", "2024 година": 2, "2023 година": 0},
        {"Кривични дела": "Неовластено навлегување и цртање на воени објекти", "2024 година": 2, "2023 година": 0},
        {"Кривични дела": "Служба во непријателска војска", "2024 година": 0, "2023 година": 1},
        {"Кривични дела": "Расна и друга дискриминација", "2024 година": 1, "2023 година": 1}
    ])
    
    # Претворање во формат за Altair (melt)
    melted_data = chart_data.melt(id_vars=['Кривични дела'], value_vars=['2024 година', '2023 година'], var_name='Година', value_name='Број')
    
    cat_order = chart_data['Кривични дела'].tolist()
    
    # Базичен графикон со столбови (дефинирање на редоследот и боите експлицитно)
    base_chart = alt.Chart(melted_data).encode(
        y=alt.Y('Кривични дела:N', title=None, sort=cat_order, axis=alt.Axis(labelLimit=300)),
        x=alt.X('Број:Q', title='Број'),
        color=alt.Color(
            'Година:N', 
            scale=alt.Scale(domain=['2024 година', '2023 година'], range=[GREEN_COLOR, BLUE_COLOR]), 
            legend=alt.Legend(title="Година")
        ),
        yOffset='Година:N'
    )
    
    bars = base_chart.mark_bar()
    
    # Додавање на data labels (броевите) врз столбовите
    text_labels = base_chart.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text=alt.Text('Број:Q')
    )
    
    final_chart = (bars + text_labels).properties(height=350).configure_view(stroke=None)
    st.altair_chart(final_chart, use_container_width=True)

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
    clean_df = df[df.iloc[:, 1].astype(str).str.contains("СВР|ОСОСК", na=False)].dropna(subset=[df.columns[1]]).copy()
    
    sector_col = clean_df.columns[1]
    col_kriminal = clean_df.columns[3]
    col_storiteli = clean_df.columns[-3]
    col_stapka = clean_df.columns[-2]
    col_efikasnost = clean_df.columns[-1]
    
    clean_df['Sector_Name'] = clean_df[sector_col].astype(str).str.strip()
    clean_df['Kriminal_Val'] = pd.to_numeric(clean_df[col_kriminal].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    clean_df['Storiteli_Val'] = pd.to_numeric(clean_df[col_storiteli].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    clean_df['Stapka_Val'] = pd.to_numeric(clean_df[col_stapka].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    clean_df['Efikasnost_Val'] = pd.to_numeric(clean_df[col_efikasnost].astype(str).str.replace(r'\s+', '', regex=True), errors='coerce')
    
    sector_order = clean_df['Sector_Name'].tolist()
    
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
        st.altair_chart(chart2, use_container_width=True)

    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Стапка на криминалитет**")
        line_chart = alt.Chart(clean_df).mark_line(color=BLUE_COLOR, point=True, strokeWidth=3).encode(
            x=alt.X('Sector_Name:N', sort=sector_order, title=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Stapka_Val:Q', title="Стапка")
        ).properties(height=300)
        st.altair_chart(line_chart, use_container_width=True)
        
    with col4:
        st.write("**Вкупна ефикасност 2024 година**")
        chart4 = alt.Chart(clean_df).mark_bar(color='green').encode(
            x=alt.X('Efikasnost_Val:Q', title="Ефикасност (%)"),
            y=alt.Y('Sector_Name:N', sort=sector_order, title=None)
        ).properties(height=300)
        st.altair_chart(chart4, use_container_width=True)
        
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

else:
    st.dataframe(df, use_container_width=True)
