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
    target_categories = ["Откриени случаи", "Број на кривични дела", "Број на сторители", "Број на криумчарени мигранти"]
    mig_df = df[df.iloc[:, 0].isin(target_categories)].copy()
    
    cat_col = mig_df.columns[0]
    col_2024 = mig_df.columns[5]
    col_2023 = mig_df.columns[10]
    col_change = mig_df.columns[11]

    mig_clean = pd.DataFrame({
        'Категорија': mig_df[cat_col].values,
        '2024': pd.to_numeric(mig_df[col_2024], errors='coerce'),
        '2023': pd.to_numeric(mig_df[col_2023], errors='coerce'),
        'Промена': pd.to_numeric(mig_df[col_change], errors='coerce')
    })
    mig_clean['Промена текст'] = mig_clean['Промена'].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x)
    )

    col1, col2 = st.columns(2)
    cat_order = ["Откриени случаи", "Број на кривични дела", "Број на сторители", "Број на криумчарени мигранти"]

    # Прв график: Column chart БЕЗ data labels
    with col1:
        st.write("**Споредба по категории: 2024 vs 2023**")
        melted_mig = mig_clean.melt(id_vars=['Категорија'], value_vars=['2024', '2023'], var_name='Година', value_name='Број')
        base_col = alt.Chart(melted_mig).encode(
            x=alt.X('Категорија:N', title=None, sort=cat_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y('Број:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8']), legend=alt.Legend(title="Година")),
            xOffset='Година:N'
        )
        st.altair_chart(base_col.mark_bar().properties(height=380), use_container_width=True)

    # Втор график: Хоризонтален Bar chart за Промена (%) со Data Labels
    with col2:
        st.write("**Промена (%) според категорија**")
        base_bar = alt.Chart(mig_clean).encode(
            y=alt.Y('Категорија:N', title=None, sort=cat_order, axis=alt.Axis(labelLimit=250)),
            x=alt.X('Промена:Q', title='Промена (%)', axis=alt.Axis(format='%'))
        )
        h_bars = base_bar.mark_bar(color='#d62728')
        text_bar = base_bar.mark_text(align='left', baseline='middle', dx=5).encode(text=alt.Text('Промена текст:N'))
        st.altair_chart((h_bars + text_bar).properties(height=380), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА НЕДОЗВОЛЕНА ТРГОВИЈА СО ДРОГА
elif "трговија" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    col_2024, col_2023 = valid_rows.columns[3], valid_rows.columns[4]
    col_change_kd = valid_rows.columns[5]
    col_stor_2024, col_stor_2023 = valid_rows.columns[6], valid_rows.columns[7]
    col_change_stor = valid_rows.columns[8]

    valid_rows = valid_rows.rename(columns={col_2024: "2024 година", col_2023: "2023 година", col_change_kd: "Промена КД %", col_stor_2024: "Сторители 2024", col_stor_2023: "Сторители 2023", col_change_stor: "Промена Сторители %"})
    for col in ["2024 година", "2023 година", "Сторители 2024", "Сторители 2023"]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    valid_rows['Промена КД % текст'] = valid_rows['Промена КД %'].apply(lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
    valid_rows['Промена Сторители % текст'] = valid_rows['Промена Сторители %'].apply(lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
    sector_order = valid_rows[sector_col].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупни КД: 2024 vs 2023**")
        df_melted_kd = valid_rows.melt(id_vars=[sector_col], value_vars=["2024 година", "2023 година"], var_name='Година', value_name='Број')
        st.altair_chart(alt.Chart(df_melted_kd).mark_bar().encode(y=alt.Y(f'{sector_col}:N', sort=sector_order), x='Број:Q', color='Година:N', yOffset='Година:N').properties(height=350), use_container_width=True)
    with col2:
        st.write("**Промена на кривични дела (%)**")
        base_n = alt.Chart(valid_rows).encode(x=alt.X(f'{sector_col}:N', sort=sector_order), y=alt.Y('Промена КД %:Q', axis=alt.Axis(format='%')))
        st.altair_chart((base_n.mark_rule(color=BLUE_COLOR) + base_n.mark_circle(size=80, color=BLUE_COLOR) + base_n.mark_text(dy=-10).encode(text='Промена КД % текст:N')).properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители: 2024 vs 2023**")
        df_melted_stor = valid_rows.melt(id_vars=[sector_col], value_vars=["Сторители 2024", "Сторители 2023"], var_name='Година', value_name='Број')
        st.altair_chart(alt.Chart(df_melted_stor).mark_bar().encode(y=alt.Y(f'{sector_col}:N', sort=sector_order), x='Број:Q', color='Година:N', yOffset='Година:N').properties(height=350), use_container_width=True)
    with col4:
        st.write("**Промена на сторители (%)**")
        base_23 = alt.Chart(valid_rows).encode(x=alt.X(f'{sector_col}:N', sort=sector_order), y=alt.Y('Промена Сторители %:Q', axis=alt.Axis(format='%')))
        st.altair_chart((base_23.mark_rule(color='#d62728') + base_23.mark_circle(size=80, color='#d62728') + base_23.mark_text(dy=-10).encode(text='Промена Сторители % текст:N')).properties(height=350), use_container_width=True)
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4. ГРАФИКОНИ ЗА ВКУПЕН КРИМИНАЛИТЕТ
elif "Вкупен" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    for col in valid_rows.columns[1:]: valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')
    sector_order = valid_rows[sector_col].tolist()
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(x=alt.X(f'{sector_col}:N', sort=sector_order), y=alt.Y(f'{valid_rows.columns[2]}:Q')).properties(height=350), use_container_width=True)
    with col2:
        st.write("**Сторители**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(y=alt.Y(f'{sector_col}:N', sort=sector_order), x=alt.X(f'{valid_rows.columns[7]}:Q')).properties(height=350), use_container_width=True)
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 5. СТАНДАРДЕН ПРИКАЗ ЗА ДРУГИ ЛИСТОВИ
else:
    st.dataframe(df, use_container_width=True)
