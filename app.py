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
BLUE_COLOR = '#1f77b4'

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

# 2. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА КРИУМЧАРЕЊЕ НА МИГРАНТИ
elif "Криумчарење на мигранти" in selected_sheet:
    # Земаме само редовите со категориите (без "Број на ОКГ")
    mig_df = df.iloc[:4, :].copy()

    cat_col = mig_df.columns[0]

    # Наоѓаме ги колоните по име наместо по фиксен индекс (поробусно)
    col_2024 = next(c for c in mig_df.columns if '2024' in str(c))
    col_2023 = next(c for c in mig_df.columns if '2023' in str(c))
    col_change = next(c for c in mig_df.columns if 'Промена' in str(c))

    mig_clean = pd.DataFrame({
        'Категорија': mig_df[cat_col].values,
