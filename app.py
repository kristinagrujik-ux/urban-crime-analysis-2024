import streamlit as st
import pandas as pd
import altair as alt

# Подесување на страницата да биде широка
st.set_page_config(page_title="Urban Crime Analysis", layout="wide")

@st.cache_data
def load_data(file_path):
    # Ги вчитува сите листови од Excel фајлот
    xls = pd.ExcelFile(file_path)
    dfs = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
    return dfs

# Промет / Патека до вашиот Excel фајл (ако е во истиот фолдер)
excel_file = "urban_crime_analysis.xlsx" # Заменете со точното име на вашиот фајл доколку е различно

try:
    dfs = load_data(excel_file)
    sheet_names = list(dfs.keys())
except Exception as e:
    st.error(f"Грешка при вчитување на фајлот: {e}")
    st.stop()

# Странично мени за избор на категорија (лист)
st.sidebar.markdown("### Избери категорија:")
selected_sheet = st.sidebar.selectbox("", sheet_names, label_visibility="collapsed")

# Земи го активниот DataFrame според избраниот лист
df = dfs[selected_sheet]

st.title(f"📊 {selected_sheet}")

# 1. ПРИКАЗ ЗА ОПШТИ / ДРУГИ ЛИСТОВИ
if "трговија" not in selected_sheet.lower():
    st.subheader("📋 Податоци од табелата")
    st.dataframe(df, use_container_width=True)

# 2. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ТРГОВИЈА СО ЛУЃЕ И ТРГОВИЈА СО ДЕЦА
elif "трговија" in selected_sheet.lower() and ("луѓе" in selected_sheet.lower() or "луге" in selected_sheet.lower()):
    raw = df.copy()
    
    # Автоматско пронаоѓање на редовите со податоци преку клучни зборови
    luge_indices = []
    deca_indices = []
    
    for idx, row in raw.iterrows():
        row_str = " ".join(str(val) for val in row.values if pd.notnull(val)).lower()
        if any(k in row_str for k in ['акциски', 'угостителски', 'странски']):
            luge_indices.append(idx)
        elif any(k in row_str for k in ['кривични дела', 'сторители', 'жртви']) and idx > 4:
            deca_indices.append(idx)

    # Резервни фиксни индекси доколку автоматското барање не најде совпаѓање
    if len(luge_indices) == 0:
        luge_indices = [1, 3, 5]  
    if len(deca_indices) == 0:
        deca_indices = [10, 11, 12] 

    max_row = len(raw) - 1
    valid_luge = [i for i in luge_indices if i <= max_row]
    
    # Динамичко земање на колоните (колона 0 за име, и колони со броеви)
    # Обично колони 0 (име), а податоците се на секоја 2-ра колона (на пр. 3, 5, 7 или сл.)
    val_cols = [c for c in [3, 5, 7, 9, 2, 4, 6, 8] if c < raw.shape[1]]
    if len(val_cols) >= 3:
        years_cols = val_cols[:3]
    else:
        years_cols = [1, 2, 3] if raw.shape[1] > 3 else [1]

    th_luge_df = raw.iloc[valid_luge, [0] + years_cols].copy() if valid_luge else pd.DataFrame()
    if not th_luge_df.empty:
        # Нагодување на имињата на колоните динамички
        col_names = ['Категорија'] + [str(raw.iloc[0, c]) if pd.notnull(raw.iloc[0, c]) else f'Година {i}' for i, c in enumerate(years_cols)]
        # Ако заглавјата во ред 0 се празни илиUnnamed, стави стандардни години
        th_luge_df.columns = ['Категорија', '2024 година', '2023 година', '2022 година'][:len(th_luge_df.columns)]
        
        for col in th_luge_df.columns[1:]:
            th_luge_df[col] = pd.to_numeric(th_luge_df[col], errors='coerce').fillna(0)
        cat_order_luge = th_luge_df['Категорија'].tolist()

    # Извлекување податоци за Трговија со деца
    valid_deca = [i for i in deca_indices if i <= max_row]
    th_deca_df = raw.iloc[valid_deca, [0] + years_cols].copy() if valid_deca else pd.DataFrame()
    if not th_deca_df.empty:
        th_deca_df.columns = ['Категорија', '2024 година', '2023 година', '2022 година'][:len(th_deca_df.columns)]
        for col in th_deca_df.columns[1:]:
            th_deca_df[col] = pd.to_numeric(th_deca_df[col], errors='coerce').fillna(0)
        cat_order_deca = th_deca_df['Категорија'].tolist()

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Трговија со луѓе")
        if not th_luge_df.empty:
            melted_luge = th_luge_df.melt(id_vars=['Категорија'], value_vars=[c for c in th_luge_df.columns if c != 'Категорија'], var_name='Година', value_name='Број')
            chart_luge = alt.Chart(melted_luge).mark_bar().encode(
                x=alt.X('Категорија:N', title=None, sort=cat_order_luge, axis=alt.Axis(labelAngle=0, labelLimit=200)),
                y=alt.Y('Број:Q', title='Број'),
                color=alt.Color('Година:N', scale=alt.Scale(range=['#7ca651', '#41729f', '#d9822b']), legend=alt.Legend(title="Година")),
                xOffset='Година:N'
            ).properties(height=380)
            st.altair_chart(chart_luge, use_container_width=True)
        else:
            st.info("Нема доволно податоци за Трговија со луѓе.")

    with col2:
        st.markdown("### Трговија со деца")
        if not th_deca_df.empty:
            melted_deca = th_deca_df.melt(id_vars=['Категорија'], value_vars=[c for c in th_deca_df.columns if c != 'Категорија'], var_name='Година', value_name='Број')
            chart_deca = alt.Chart(melted_deca).mark_bar().encode(
                x=alt.X('Категорија:N', title=None, sort=cat_order_deca, axis=alt.Axis(labelAngle=0, labelLimit=200)),
                y=alt.Y('Број:Q', title='Број'),
                color=alt.Color('Година:N', scale=alt.Scale(range=['#7ca651', '#41729f', '#d9822b']), legend=alt.Legend(title="Година")),
                xOffset='Година:N'
            ).properties(height=380)
            st.altair_chart(chart_deca, use_container_width=True)
        else:
            st.info("Нема доволно податоци за Трговија со деца.")

    st.subheader("📋 Детални табели од Excel")
    st.dataframe(raw, use_container_width=True)
