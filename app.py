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
    
    # Ги филтрираме само редовите со податоци (претпоставувајќи дека податоците почнуваат од соодветен ред)
    # Подеси ги индексот на колоните (iloc) според твојот Excel фајл
    state_rows = df.dropna(subset=[df.columns[0]]).copy()
    
    table_data = []
    for idx, row in state_rows.iterrows():
        kriminal = str(row.iloc[0]).strip()
        # Проверка дали редот е валиден (не е наслов или празен ред)
        if kriminal and kriminal.lower() != 'nan' and "кривични дела" not in kriminal.lower():
            table_data.append({
                "Кривични дела": kriminal,
                "2024 година": row.iloc[8], # Прилагоди според позицијата во Excel
                "2023 година": row.iloc[11],
                "Промена %": row.iloc[14]
            })
            
    df_display = pd.DataFrame(table_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# 2. ОСТАНАТИ СЛУЧАИ: Графикони
else:
    st.subheader("📈 Графикони")

    if "Криумчарење" in selected_sheet or "мигранти" in selected_sheet.lower():
        # ... (твојот постоечки код за графикони за мигранти)
        st.write("Графикони за криумчарење...")

    elif "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
        # ... (твојот постоечки код за графикони за дрога)
        st.write("Графикони за дрога...")

    elif "Организиран" in selected_sheet:
        # ... (твојот постоечки код за графикони за организиран криминал)
        st.write("Графикони за организиран криминал...")

    else:
        st.write("Нема дефинирани графикони за овој лист.")

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)
