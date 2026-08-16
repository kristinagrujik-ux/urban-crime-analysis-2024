import streamlit as st
import pandas as pd
import altair as alt

# Поставување на страната
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
BLUE_COLOR = '#1f77b4'

# СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА НЕДОЗВОЛЕНА ТРГОВИЈА СО ДРОГА
if "трговија" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    # Колони според твојот фајл: 2024(3), 2023(4), Сторители 2024(6)
    col_2024 = valid_rows.columns[3]
    col_2023 = valid_rows.columns[4]
    col_storiteli = valid_rows.columns[6]

    # Подготовка за хоризонтален Bar (2024 vs 2023)
    df_melted = valid_rows.melt(id_vars=[sector_col], value_vars=[col_2024, col_2023], 
                                var_name='Година', value_name='Број')

    col1, col2 = st.columns(2)
    
    # 1. Вкупни КД (2024 vs 2023) - Хоризонтален Bar
    with col1:
        st.write("**Вкупни КД: 2024 vs 2023**")
        bar_v = alt.Chart(df_melted).mark_bar().encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort='-x'),
            x=alt.X('Број:Q', title='Број на дела'),
            color='Година:N'
        ).properties(height=350)
        st.altair_chart(bar_v, use_container_width=True)

    # 2. Линиски график (2024) - СО DATA LABELS
    with col2:
        st.write("**Недозволена трговија (2024)**")
        line_n = alt.Chart(valid_rows).mark_line(color=BLUE_COLOR, point=True).encode(
            x=alt.X(f'{sector_col}:N', title=None, axis=alt.Axis(labelAngle=270)),
            y=alt.Y(f'{col_2024}:Q', title='Број')
        )
        text_n = line_n.mark_text(align='center', baseline='bottom', dy=-10).encode(text=f'{col_2024}:Q')
        st.altair_chart((line_n + text_n).properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    
    # 3. Сторители - Хоризонтален Bar
    with col3:
        st.write("**Сторители (2024)**")
        bar_s = alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort='-x'),
            x=alt.X(f'{col_storiteli}:Q', title='Број на сторители')
        ).properties(height=350)
        st.altair_chart(bar_s, use_container_width=True)

    # 4. Линиски график (2023) - СО DATA LABELS
    with col4:
        st.write("**Споредба 2023 година**")
        line_23 = alt.Chart(valid_rows).mark_line(color=BLUE_COLOR, point=True).encode(
            x=alt.X(f'{sector_col}:N', title=None, axis=alt.Axis(labelAngle=270)),
            y=alt.Y(f'{col_2023}:Q', title='Број')
        )
        text_23 = line_23.mark_text(align='center', baseline='bottom', dy=-10).encode(text=f'{col_2023}:Q')
        st.altair_chart((line_23 + text_23).properties(height=350), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# ОСТАНАТИ ЛИСТОВИ
else:
    st.dataframe(df, use_container_width=True)
