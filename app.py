import streamlit as st
import pandas as pd

st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

st.title("📊 Национален Извештај за Урбан Криминалитет 2024")
st.markdown("Интерактивен дашборд за анализа на стапката на криминалитет и безбедносни метрики по СВР сектори во Северна Македонија.")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        return None

df = load_data()

if df is not None:
    st.success("Податоците се успешно вчитани!")
    st.subheader("📋 Преглед на сурови податоци")
    st.dataframe(df)
    st.subheader("📈 Брзи Статистики")
    st.write(df.describe())
else:
    st.error("Грешка: Фајлот KRIMINALITET.xlsx не е пронајден или не може да се вчита.")
