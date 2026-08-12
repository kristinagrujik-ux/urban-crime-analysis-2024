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

# Издвојување на податоци за СВР/ОСОСК
valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
sector_col = valid_rows.columns[0]

# Конверзија на колоните во нумерички (ако постојат)
for col in valid_rows.columns[1:]:
    valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

if "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    # Задржи ја логиката за дрога (со 2 пит графикони)
    pass 
else:
    # Распоред за останатите категории: 2 реда по 2 графикони
    # 1. Вкупни кривични дела, 2. Сторители, 3. Стапка (линија), 4. Ефикасност (бар)
    col1, col2 = st.columns(2)
    
    # 1. Вкупни кривични дела (без запирки во Y оската)
    with col1:
        st.write("**Вкупни кривични дела**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y('Кривични дела:Q', title='Број', axis=alt.Axis(format='d')), # 'd' за цели броеви без запирки
            color=alt.Color(f'{sector_col}:N', legend=None)
        ).properties(height=300), use_container_width=True)

    # 2. Сторители
    with col2:
        st.write("**Сторители**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y('Сторители:Q', title='Број', axis=alt.Axis(format='d')),
            color=alt.Color(f'{sector_col}:N', legend=None)
        ).properties(height=300), use_container_width=True)

    col3, col4 = st.columns(2)
    
    # 3. Стапка на криминал 2024 (Линиски)
    with col3:
        st.write("**Стапка на криминал 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_line(point=True).encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y('Стапка:Q', title='Стапка'),
            color=alt.value('#e45756')
        ).properties(height=300), use_container_width=True)

    # 4. Вкупна ефикасност 2024 (Бар)
    with col4:
        st.write("**Вкупна ефикасност 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar().encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y('Ефикасност:Q', title='Процент'),
            color=alt.Color(f'{sector_col}:N', legend=None)
        ).properties(height=300), use_container_width=True)

st.subheader("📋 Детална табела")
st.dataframe(df)
