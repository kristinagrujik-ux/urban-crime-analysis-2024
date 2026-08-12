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

if "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    max_col = len(valid_rows.columns)
    
    df_kd = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 3], '2023': valid_rows.iloc[:, 4]}).melt('Сектор', var_name='Година', value_name='Вредност')
    df_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 7], '2023': valid_rows.iloc[:, 8]}).melt('Сектор', var_name='Година', value_name='Вредност')

    # Прв ред: Кривични дела (Столпчест + Пит со реални проценти)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_kd).mark_bar().encode(x='Сектор:N', xOffset='Година:N', y='Вредност:Q', color='Година:N').properties(height=350), use_container_width=True)
    with col2:
        if max_col > 5:
            st.write("**Кривични дела (Пит - Промена %)**")
            raw_val = valid_rows.iloc[:, 5].astype(str).str.replace('%', '').str.replace('+', '').str.strip()
            df_pie = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Промена': pd.to_numeric(raw_val, errors='coerce').abs()}).dropna()
            if not df_pie.empty:
                df_pie['Прoцент'] = (df_pie['Промена'] / df_pie['Промена'].sum() * 100).round(1)
                pie = alt.Chart(df_pie).mark_arc(innerRadius=0).encode(theta='Промена:Q', color='Сектор:N', tooltip=['Сектор', 'Прoцент'])
                text = pie.mark_text(radius=100).encode(text=alt.Text('Прoцент:Q', format='.1f'))
                st.altair_chart(pie + text, use_container_width=True)

    # Втор ред: Сторители (Столпчест + Пит со реални проценти)
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_st).mark_bar().encode(x='Сектор:N', xOffset='Година:N', y='Вредност:Q', color='Година:N').properties(height=350), use_container_width=True)
    with col4:
        if max_col > 9:
            st.write("**Сторители (Пит - Промена %)**")
            raw_val_st = valid_rows.iloc[:, 9].astype(str).str.replace('%', '').str.replace('+', '').str.strip()
            df_pie_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Промена': pd.to_numeric(raw_val_st, errors='coerce').abs()}).dropna()
            if not df_pie_st.empty:
                df_pie_st['Прoцент'] = (df_pie_st['Промена'] / df_pie_st['Промена'].sum() * 100).round(1)
                pie_st = alt.Chart(df_pie_st).mark_arc(innerRadius=0).encode(theta='Промена:Q', color='Сектор:N', tooltip=['Сектор', 'Прoцент'])
                text_st = pie_st.mark_text(radius=100).encode(text=alt.Text('Прoцент:Q', format='.1f'))
                st.altair_chart(pie_st + text_st, use_container_width=True)
else:
    st.dataframe(df)
