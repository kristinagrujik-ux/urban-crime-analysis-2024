import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

file_path = 'KRIMINALITET.xlsx'

# Директно ги дефинираме листовите од вашиот Excel фајл
sheet_names = ["Вкупен криминалитет", "Недозволена трговија со дрога"]
selected_sheet = st.sidebar.selectbox("Избери категорија на извештај:", sheet_names)

st.title(f"📊 Извештај: {selected_sheet}")

@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)

df = load_data(selected_sheet)

if not df.empty:
    df_chart = df[~df.iloc[:, 0].astype(str).str.contains("Вкупно", case=False, na=False)]
    sector_col = df.columns[0]
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
