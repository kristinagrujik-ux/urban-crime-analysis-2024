import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

# Дефинирање на патеката до фајлот
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

# 2. ОСТАНАТИ СЛУЧАИ: Графикони и табели за другите листови
else:
    st.subheader("📈 Графикони")

    if "Криумчарење" in selected_sheet or "мигранти" in selected_sheet.lower():
        mig_rows = df.dropna(subset=[df.columns[0]]).copy()
        valid_mig = mig_rows[mig_rows.iloc[:, 0].astype(str).str.contains("Откриени|кривични|сторители|мигранти", case=False, na=False)].copy()
        kategorii = valid_mig.iloc[:, 0].astype(str)
        
        df_mig_bars = pd.DataFrame({
            'Категорија': kategorii,
            '2024': pd.to_numeric(valid_mig.iloc[:, 5], errors='coerce'),
            '2023': pd.to_numeric(valid_mig.iloc[:, 8], errors='coerce')
        }).melt('Категорија', var_name='Година', value_name='Вредност')
        
        df_mig_pct = pd.DataFrame({
            'Категорија': kategorii,
            'Процент': round(pd.to_numeric(valid_mig.iloc[:, 11], errors='coerce') * 100, 1)
        })
        df_mig_pct['Пр_Текст'] = df_mig_pct['Процент'].astype(str) + '%'

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Криумчарење на мигранти (2024 vs 2023)**")
            st.altair_chart(alt.Chart(df_mig_bars).mark_bar().encode(
                x=alt.X('Категорија:N', title=None, axis=alt.Axis(labelAngle=270, labelLimit=600)),
                y=alt.Y('Вредност:Q', title='Број'),
                color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])),
                xOffset='Година:N'
            ).properties(height=420), use_container_width=True)

        with col2:
            st.write("**Процент на промена по категории**")
            df_mig_pct_sorted = df_mig_pct.sort_values(by='Процент', ascending=True).reset_index(drop=True)
            sorted_cats = df_mig_pct_sorted['Категорија'].tolist()
            bar_chart = alt.Chart(df_mig_pct_sorted).mark_bar(color='#d62728', size=26).encode(
                y=alt.Y('Категорија:N', title=None, sort=sorted_cats),
                x=alt.X('Процент:Q', title='Процент (%)')
            )
            text_chart = alt.Chart(df_mig_pct_sorted).mark_text(align='left', dx=8, color='black', fontWeight='bold').encode(
                y=alt.Y('Категорија:N', sort=sorted_cats), x=alt.X('Процент:Q'), text='Пр_Текст:N'
            )
            st.altair_chart((bar_chart + text_chart).properties(width=550, height=380), use_container_width=True)

    elif "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
        valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
        
        # Поедноставена логика за наркотици
        st.dataframe(df, use_container_width=True)

    elif "Организиран" in selected_sheet:
        st.dataframe(df, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True)
