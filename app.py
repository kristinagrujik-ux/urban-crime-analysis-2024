import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def load_excel():
    # Ги читаме сите листови од Excel фајлот
    xls = pd.ExcelFile(file_path)
    return xls

xls = load_excel()

# Достапни листови во менито од страна
sheet_names = xls.sheet_names
selected_sheet = st.sidebar.selectbox("Избери категорија на извештај:", sheet_names)

st.title(f"📊 Извештај: {selected_sheet}")

# Читање на избраниот лист
df = pd.read_excel(file_path, sheet_name=selected_sheet)

# Проверка дали листот има податоци и прикажување графикони
if not df.empty:
    # Филтрирање без редот "Вкупно" за графиконите
    df_chart = df[~df.iloc[:, 0].astype(str).str.contains("Вкупно", case=False, na=False)]
    
    sector_col = df.columns[0]
    
    # Земање на првите неколку нумерички колони за графикони
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        st.subheader("📈 Споредбена анализа по СВР сектори")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{numeric_cols[0]}**")
            st.bar_chart(df_chart.set_index(sector_col)[numeric_cols[0]])
            
        with col2:
            st.write(f"**{numeric_cols[1]}**")
            st.bar_chart(df_chart.set_index(sector_col)[numeric_cols[1]])
            
        if len(numeric_cols) >= 3:
            col3, col4 = st.columns(2)
            with col3:
                st.write(f"**{numeric_cols[2]}**")
                st.line_chart(df_chart.set_index(sector_col)[numeric_cols[2]])
            if len(numeric_cols) >= 4:
                with col4:
                    st.write(f"**{numeric_cols[3]}**")
                    st.bar_chart(df_chart.set_index(sector_col)[numeric_cols[3]])

    st.subheader("📋 Детална табела со податоци")
    st.dataframe(df)
else:
    st.warning("Избраниот лист е празен.")
