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

# 1. СПЕЦИЈАЛЕН СЛУЧАЈ: Табела за Кривични дела против државата
if "Кривични дела против државата" in selected_sheet:
    st.subheader("📋 Детална табела")
    
    table_data = [
        {"Кривични дела": "Предизвикување омраза и нетрпеливост", "2024 година": 10, "2023 година": 2, "Промена %": "пет пати ↗"},
        {"Кривични дела": "Учество во странска војска и полиција", "2024 година": 2, "2023 година": "-", "Промена %": "200% ↗"},
        {"Кривични дела": "Неовластено навлегување и цртање на воени објекти", "2024 година": 2, "2023 година": "-", "Промена %": "200% ↗"},
        {"Кривични дела": "Служба во непријателска војска", "2024 година": "-", "2023 година": 1, "Промена %": "-"},
        {"Кривични дела": "Расна и друга дискриминација", "2024 година": 1, "2023 година": 1, "Промена %": "-"},
        {"Кривични дела": "Вкупно кривични дела", "2024 година": 15, "2023 година": 4, "Промена %": "три и пол пати ↗"}
    ]
            
    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# 2. ГРАФИКОНИ ЗА ВКУПЕН КРИМИНАЛИТЕТ
elif "Вкупен" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    for col in valid_rows.columns[1:]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    c_col = valid_rows.columns[2]     # Кривични дела
    s_col = valid_rows.columns[7]     # Сторители
    st_col = valid_rows.columns[8]    # Стапка
    ef_col = valid_rows.columns[6]    # Расветлени КД (ефикасност)

    sector_order = valid_rows[sector_col].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет за 2024 година по СВР**")
        bar_c = alt.Chart(valid_rows).mark_bar(color='#a64d28').encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y(f'{c_col}:Q', title='Број')
        )
        text_c = bar_c.mark_text(align='center', baseline='bottom', dy=-5).encode(text=f'{c_col}:Q')
        st.altair_chart((bar_c + text_c).properties(height=350), use_container_width=True)

    with col2:
        st.write("**Сторители**")
        bar_s = alt.Chart(valid_rows).mark_bar(color='#c00000').encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort=sector_order[::-1], axis=alt.Axis(labelLimit=200)),
            x=alt.X(f'{s_col}:Q', title='Број')
        )
        text_s = bar_s.mark_text(align='left', dx=5).encode(text=f'{s_col}:Q')
        st.altair_chart((bar_s + text_s).properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапката на криминалитетот**")
        line_st = alt.Chart(valid_rows).mark_line(color='#1f77b4').encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y(f'{st_col}:Q', title='Стапка', scale=alt.Scale(zero=False))
        )
        points_st = line_st.mark_circle(size=60, color='#1f77b4')
        text_st = line_st.mark_text(align='center', baseline='bottom', dy=-10).encode(text=f'{st_col}:Q')
        st.altair_chart((line_st + points_st + text_st).properties(height=350), use_container_width=True)

    with col4:
        st.write("**Вкупна ефикасност 2024**")
        bar_ef = alt.Chart(valid_rows).mark_bar(color='#1f77b4').encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort=sector_order[::-1], axis=alt.Axis(labelLimit=200)),
            x=alt.X(f'{ef_col}:Q', title='Расветлени КД')
        )
        text_ef = bar_ef.mark_text(align='left', dx=5).encode(text=f'{ef_col}:Q')
        st.altair_chart((bar_ef + text_ef).properties(height=350), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3. СТАНДАРДЕН ПРИКАЗ ЗА ДРУГИ ЛИСТОВИ
else:
    st.dataframe(df, use_container_width=True)
