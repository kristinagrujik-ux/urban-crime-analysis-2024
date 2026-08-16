import streamlit as st
import pandas as pd
import altair as alt

# Поставување на конфигурација на страната
st.set_page_config(page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide")

file_path = 'KRIMINALITET.xlsx'

@st.cache_data
def get_sheets():
    return pd.ExcelFile(file_path).sheet_names

# Странично мени за избор на категорија (лист)
selected_sheet = st.sidebar.selectbox("Избери категорија:", get_sheets())
st.title(f"📊 {selected_sheet}")

@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)

df = load_data(selected_sheet)
BLUE_COLOR = '#1f77b4'
GREEN_COLOR = '#2ca02c'

# --- 1. СПЕЦИЈАЛЕН СЛУЧАЈ: Кривични дела против државата ---
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
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

# --- 2. СПЕЦИЈАЛИЗИРАН ПРИКАЗ: Организиран криминал ---
elif "Организиран" in selected_sheet or "организиран" in selected_sheet:
    valid_rows = df.iloc[3:9, :].copy() if len(df) > 9 else df.copy()
    
    sector_col = valid_rows.columns[0]
    okg_clean = pd.DataFrame({
        'Област': valid_rows[sector_col].astype(str).values,
        'ОКГ 2024': pd.to_numeric(valid_rows[valid_rows.columns[5]], errors='coerce').fillna(0),
        'ОКГ 2023': pd.to_numeric(valid_rows[valid_rows.columns[7]], errors='coerce').fillna(0),
        'Членови 2024': pd.to_numeric(valid_rows[valid_rows.columns[10]], errors='coerce').fillna(0),
        'Членови 2023': pd.to_numeric(valid_rows[valid_rows.columns[12]], errors='coerce').fillna(0)
    })
    
    sector_order = okg_clean['Област'].tolist()
    col1, col2 = st.columns(2)
    
    def create_okg_chart(data, val_vars):
        melted = data.melt(id_vars=['Област'], value_vars=val_vars, var_name='Година', value_name='Број')
        return alt.Chart(melted).mark_bar().encode(
            x=alt.X('Број:Q', title='Број'),
            y=alt.Y('Година:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
            color=alt.Color('Година:N', scale=alt.Scale(domain=val_vars, range=[BLUE_COLOR, GREEN_COLOR]), legend=alt.Legend(title="Година")),
            row=alt.Row('Област:N', title=None, sort=sector_order, header=alt.Header(labelAngle=0, labelAlign='left'))
        ).properties(height=25).configure_facet(spacing=5).configure_view(stroke=None)

    with col1:
        st.write("**ОКГ: 2024 vs 2023 година**")
        st.altair_chart(create_okg_chart(okg_clean, ['ОКГ 2024', 'ОКГ 2023']), use_container_width=True)
    with col2:
        st.write("**Членови на криминални групи: 2024 vs 2023 година**")
        st.altair_chart(create_okg_chart(okg_clean, ['Членови 2024', 'Членови 2023']), use_container_width=True)
        
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# --- 3. СПЕЦИЈАЛИЗИРАН ПРИКАЗ: Криумчарење на мигранти ---
elif "Криумчарење на мигранти" in selected_sheet:
    mig_df = df.iloc[:4, :].copy()
    cat_col = mig_df.columns[0]
    
    mig_clean = pd.DataFrame({
        'Категорија': mig_df[cat_col].values,
        '2024 година': pd.to_numeric(mig_df[mig_df.columns[5]], errors='coerce'),
        '2023 година': pd.to_numeric(mig_df[mig_df.columns[10]], errors='coerce'),
        'Промена': pd.to_numeric(mig_df[mig_df.columns[11]], errors='coerce')
    })
    
    mig_clean['Промена текст'] = mig_clean['Промена'].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x)
    )
    cat_order = mig_clean['Категорија'].tolist()
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Споредба по категории: 2024 vs 2023**")
        melted_mig = mig_clean.melt(id_vars=['Категорија'], value_vars=['2024 година', '2023 година'], var_name='Година', value_name='Број')
        base_col = alt.Chart(melted_mig).encode(
            x=alt.X('Број:Q', title='Број'),
            y=alt.Y('Година:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=[BLUE_COLOR, GREEN_COLOR]), legend=alt.Legend(title="Година")),
            row=alt.Row('Категорија:N', title=None, sort=cat_order, header=alt.Header(labelAngle=0, labelAlign='left', labelLimit=300))
        )
        st.altair_chart(base_col.mark_bar().properties(height=25).configure_facet(spacing=5).configure_view(stroke=None), use_container_width=True)

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

# --- 4. СПЕЦИЈАЛИЗИРАН ПРИКАЗ: Недозволена трговија со дрога ---
elif "трговија" in selected_sheet or "Трговија" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    col_2024, col_2023 = valid_rows.columns[3], valid_rows.columns[4]
    col_change_kd = valid_rows.columns[5]
    col_stor_2024, col_stor_2023 = valid_rows.columns[6], valid_rows.columns[7]
    col_change_stor = valid_rows.columns[8]

    valid_rows = valid_rows.rename(columns={
        col_2024: "2024 година", col_2023: "2023 година", col_change_kd: "Промена КД %", 
        col_stor_2024: "Сторители 2024", col_stor_2023: "Сторители 2023", col_change_stor: "Промена Сторители %"
    })
    
    for col in ["2024 година", "2023 година", "Сторители 2024", "Сторители 2023"]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    valid_rows['Промена КД % текст'] = valid_rows['Промена КД %'].apply(lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
    valid_rows['Промена Сторители % текст'] = valid_rows['Промена Сторители %'].apply(lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x))
    sector_order = valid_rows[sector_col].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупни КД: 2024 vs 2023**")
        df_melted_kd = valid_rows.melt(id_vars=[sector_col], value_vars=["2024 година", "2023 година"], var_name='Година', value_name='Број')
        chart_kd = alt.Chart(df_melted_kd).mark_bar().encode(
            x=alt.X('Број:Q', title='Број'),
            y=alt.Y('Година:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=[BLUE_COLOR, GREEN_COLOR]), legend=alt.Legend(title="Година")),
            row=alt.Row(f'{sector_col}:N', title=None, sort=sector_order, header=alt.Header(labelAngle=0, labelAlign='left'))
        )
        st.altair_chart(chart_kd.properties(height=20).configure_facet(spacing=5).configure_view(stroke=None), use_container_width=True)
    with col2:
        st.write("**Промена на кривични дела (%)**")
        base_n = alt.Chart(valid_rows).encode(x=alt.X(f'{sector_col}:N', sort=sector_order), y=alt.Y('Промена КД %:Q', axis=alt.Axis(format='%')))
        st.altair_chart((base_n.mark_rule(color=BLUE_COLOR) + base_n.mark_circle(size=80, color=BLUE_COLOR) + base_n.mark_text(dy=-10).encode(text='Промена КД % текст:N')).properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители: 2024 vs 2023**")
        df_melted_stor = valid_rows.melt(id_vars=[sector_col], value_vars=["Сторители 2024", "Сторители 2023"], var_name='Година', value_name='Број')
        chart_stor = alt.Chart(df_melted_stor).mark_bar().encode(
            x=alt.X('Број:Q', title='Број'),
            y=alt.Y('Година:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['Сторители 2024', 'Сторители 2023'], range=[BLUE_COLOR, GREEN_COLOR]), legend=alt.Legend(title="Година")),
            row=alt.Row(f'{sector_col}:N', title=None, sort=sector_order, header=alt.Header(labelAngle=0, labelAlign='left'))
        )
        st.altair_chart(chart_stor.properties(height=20).configure_facet(spacing=5).configure_view(stroke=None), use_container_width=True)
    with col4:
        st.write("**Промена на сторители (%)**")
        base_23 = alt.Chart(valid_rows).encode(x=alt.X(f'{sector_col}:N', sort=sector_order), y=alt.Y('Промена Сторители %:Q', axis=alt.Axis(format='%')))
        st.altair_chart((base_23.mark_rule(color='#d62728') + base_23.mark_circle(size=80, color='#d62728') + base_23.mark_text(dy=-10).encode(text='Промена Сторители % текст:N')).properties(height=350), use_container_width=True)
        
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# --- 5. СПЕЦИЈАЛИЗИРАН ПРИКАЗ: Вкупен криминалитет ---
elif "Вкупен" in selected_sheet or "вкупен" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    for col in valid_rows.columns[1:]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')
    sector_order = valid_rows[sector_col].tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            x=alt.X(f'{sector_col}:N', sort=sector_order), y=alt.Y(f'{valid_rows.columns[2]}:Q')
        ).properties(height=350), use_container_width=True)
    with col2:
        st.write("**Сторители**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', sort=sector_order), x=alt.X(f'{valid_rows.columns[7]}:Q')
        ).properties(height=350), use_container_width=True)
        
    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# --- 6. СТАНДАРДЕН ПРИКАЗ ЗА СИТЕ ОСТАНАТИ ЛИСТОВИ ---
else:
    st.dataframe(df, use_container_width=True)
