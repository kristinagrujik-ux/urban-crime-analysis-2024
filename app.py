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
    
    # Правилен редослед на годините за да одговараат на легендата
    df_kd = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024 година': valid_rows.iloc[:, 3], '2023 година': valid_rows.iloc[:, 4]}).melt('Сектор', var_name='Година', value_name='Вредност')
    df_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024 година': valid_rows.iloc[:, 7], '2023 година': valid_rows.iloc[:, 8]}).melt('Сектор', var_name='Година', value_name='Вредност')

    color_scale = alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8'])

    # Прв ред: Кривични дела (Столпчест + Пит)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        chart_kd = alt.Chart(df_kd).mark_bar().encode(
            x=alt.X('Сектор:N', title='Сектор', sort=None),
            xOffset=alt.XOffset('Година:N'),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=color_scale)
        ).properties(height=350)
        st.altair_chart(chart_kd, use_container_width=True)
        
    with col2:
        if max_col > 5:
            st.write("**Кривични дела (Пит - Промена %)**")
            raw_val = valid_rows.iloc[:, 5].astype(str).str.replace('%', '').str.replace('+', '').str.strip()
            df_pie = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Промена': pd.to_numeric(raw_val, errors='coerce').abs()}).dropna()
            if not df_pie.empty:
                df_pie['Процент'] = (df_pie['Промена'] / df_pie['Промена'].sum() * 100).round(1)
                pie_kd = alt.Chart(df_pie).mark_arc(innerRadius=0).encode(
                    theta=alt.Theta('Промена:Q'),
                    color=alt.Color('Сектор:N', legend=alt.Legend(title="Сектор")),
                    tooltip=['Сектор', 'Процент']
                ).properties(height=350)
                st.altair_chart(pie_kd, use_container_width=True)

    # Втор ред: Сторители (Столпчест + Пит)
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители (2024 vs 2023)**")
        chart_st = alt.Chart(df_st).mark_bar().encode(
            x=alt.X('Сектор:N', title='Сектор', sort=None),
            xOffset=alt.XOffset('Година:N'),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=color_scale)
        ).properties(height=350)
        st.altair_chart(chart_st, use_container_width=True)

    with col4:
        if max_col > 9:
            st.write("**Сторители (Пит - Промена %)**")
            raw_val_st = valid_rows.iloc[:, 9].astype(str).str.replace('%', '').str.replace('+', '').str.strip()
            df_pie_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], 'Промена': pd.to_numeric(raw_val_st, errors='coerce').abs()}).dropna()
            if not df_pie_st.empty:
                df_pie_st['Процент'] = (df_pie_st['Промена'] / df_pie_st['Промена'].sum() * 100).round(1)
                pie_st = alt.Chart(df_pie_st).mark_arc(innerRadius=0).encode(
                    theta=alt.Theta('Промена:Q'),
                    color=alt.Color('Сектор:N', legend=alt.Legend(title="Сектор")),
                    tooltip=['Сектор', 'Процент']
                ).properties(height=350)
                st.altair_chart(pie_st, use_container_width=True)
else:
    st.dataframe(df)
