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
    table_data = [
        {"Кривични дела": "Предизвикување омраза и нетрпеливост", "2024 година": 10, "2023 година": 2, "Промена %": "пет пати ↗"},
        {"Кривични дела": "Учество во странска војска и полиција", "2024 година": 2, "2023 година": "-", "Промена %": "200% ↗"},
        {"Кривични дела": "Неовластено навлегување и цртање на воени објекти", "2024 година": 2, "2023 година": "-", "Промена %": "200% ↗"},
        {"Кривични дела": "Служба во непријателска војска", "2024 година": "-", "2023 година": 1, "Промена %": "-"},
        {"Кривични дела": "Расна и друга дискриминација", "2024 година": 1, "2023 година": 1, "Промена %": "-"},
        {"Кривични дела": "Вкупно кривични дела", "2024 година": 15, "2023 година": 4, "Промена %": "три и пол пати ↗"}
    ]
    df_display = pd.DataFrame(table_data)

    st.write("**Кривични дела: 2024 vs 2023 година**")
    chart_data = df_display[df_display["Кривични дела"] != "Вкупно кривични дела"].copy()
    chart_data["2024 година"] = pd.to_numeric(chart_data["2024 година"], errors='coerce').fillna(0)
    chart_data["2023 година"] = pd.to_numeric(chart_data["2023 година"], errors='coerce').fillna(0)
    cat_order_kd = chart_data["Кривични дела"].tolist()
    melted_kd = chart_data.melt(id_vars=["Кривични дела"], value_vars=["2024 година", "2023 година"], var_name='Година', value_name='Број')
    base_kd_state = alt.Chart(melted_kd).encode(
        y=alt.Y('Кривични дела:N', sort=cat_order_kd, title=None, axis=alt.Axis(labelLimit=320)),
        x=alt.X('Број:Q', title='Број', axis=alt.Axis(format='d', tickMinStep=1)),
        color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#228B22', '#50C878']), legend=alt.Legend(title="Година")),
        yOffset='Година:N'
    )
    bars_kd_state = base_kd_state.mark_bar()
    text_kd_state = base_kd_state.mark_text(align='left', dx=3, baseline='middle').encode(text='Број:Q')
    st.altair_chart((bars_kd_state + text_kd_state).properties(height=350), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# 2. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА КРИУМЧАРЕЊЕ НА МИГРАНТИ
elif "Криумчарење на мигранти" in selected_sheet:
    mig_df = df.iloc[:4, :].copy()
    cat_col = mig_df.columns[0]

    col_2024 = next(c for c in mig_df.columns if '2024' in str(c))
    col_2023 = next(c for c in mig_df.columns if '2023' in str(c))
    col_change = next(c for c in mig_df.columns if 'Промена' in str(c))

    mig_clean = pd.DataFrame({
        'Категорија': mig_df[cat_col].values,
        '2024 година': pd.to_numeric(mig_df[col_2024], errors='coerce'),
        '2023 година': pd.to_numeric(mig_df[col_2023], errors='coerce'),
        'Промена': pd.to_numeric(mig_df[col_change], errors='coerce')
    })

    mig_clean['Промена текст'] = mig_clean['Промена'].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x)
    )

    col1, col2 = st.columns(2)
    cat_order = mig_clean['Категорија'].tolist()

    with col1:
        st.write("**Споредба по категории: 2024 vs 2023**")
        melted_mig = mig_clean.melt(id_vars=['Категорија'], value_vars=['2024 година', '2023 година'], var_name='Година', value_name='Број')

        chart_col = alt.Chart(melted_mig).mark_bar().encode(
            x=alt.X('Категорија:N', title=None, sort=cat_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y('Број:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8']), legend=alt.Legend(title="Година")),
            xOffset='Година:N'
        )
        st.altair_chart(chart_col.properties(height=380), use_container_width=True)

    with col2:
        st.write("**Промена (%) според категорија**")
        cat_order_reversed = cat_order[::-1]
        bar_change = alt.Chart(mig_clean).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y('Категорија:N', sort=cat_order_reversed, title=None, axis=alt.Axis(labelLimit=280, labelFontSize=11, labelPadding=10)),
            x=alt.X('Промена:Q', axis=alt.Axis(format='%'), title='Промена')
        )
        text_change = bar_change.mark_text(align='left', dx=3).encode(text='Промена текст:N')
        st.altair_chart(
            (bar_change + text_change).properties(height=380, padding={"left": 20, "top": 5, "right": 20, "bottom": 5}),
            use_container_width=True
        )

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
    valid_rows['zero'] = 0
    sector_order = valid_rows[sector_col].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупни КД: 2024 vs 2023**")
        df_melted_kd = valid_rows.melt(id_vars=[sector_col], value_vars=["2024 година", "2023 година"], var_name='Година', value_name='Број')
        st.altair_chart(
            alt.Chart(df_melted_kd).mark_bar().encode(
                y=alt.Y(f'{sector_col}:N', sort=sector_order),
                x='Број:Q',
                color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8']), legend=alt.Legend(title="Година")),
                yOffset='Година:N'
            ).properties(height=350),
            use_container_width=True
        )
    with col2:
        st.write("**Недозволена трговија со дрога - Промена на кривични дела (%)**")
        base_kd = alt.Chart(valid_rows).encode(x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)))
        rule_kd = base_kd.mark_rule(color=BLUE_COLOR, strokeWidth=2).encode(y=alt.Y('Промена КД %:Q', axis=alt.Axis(format='%'), title='Промена'), y2='zero:Q')
        circle_kd = base_kd.mark_circle(size=220, color=BLUE_COLOR).encode(y='Промена КД %:Q')
        text_kd_change = base_kd.mark_text(align='center', dy=-16, fontSize=11).encode(y='Промена КД %:Q', text='Промена КД % текст:N')
        st.altair_chart((rule_kd + circle_kd + text_kd_change).properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители: 2024 vs 2023**")
        df_melted_stor = valid_rows.melt(id_vars=[sector_col], value_vars=["Сторители 2024", "Сторители 2023"], var_name='Година', value_name='Број')
        st.altair_chart(
            alt.Chart(df_melted_stor).mark_bar().encode(
                y=alt.Y(f'{sector_col}:N', sort=sector_order),
                x='Број:Q',
                color=alt.Color('Година:N', scale=alt.Scale(domain=['Сторители 2024', 'Сторители 2023'], range=['#1f77b4', '#aec7e8']), legend=alt.Legend(title="Година")),
                yOffset='Година:N'
            ).properties(height=350),
            use_container_width=True
        )
    with col4:
        st.write("**Недозволена трговија со дрога - Промена на сторители (%)**")
        base_stor = alt.Chart(valid_rows).encode(x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)))
        rule_stor = base_stor.mark_rule(color='#d62728', strokeWidth=2).encode(y=alt.Y('Промена Сторители %:Q', axis=alt.Axis(format='%'), title='Промена'), y2='zero:Q')
        circle_stor = base_stor.mark_circle(size=220, color='#d62728').encode(y='Промена Сторители %:Q')
        text_stor_change = base_stor.mark_text(align='center', dy=-16, fontSize=11).encode(y='Промена Сторители %:Q', text='Промена Сторители % текст:N')
        st.altair_chart((rule_stor + circle_stor + text_stor_change).properties(height=350), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3.5 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ОРГАНИЗИРАН КРИМИНАЛ
elif "Организиран" in selected_sheet:
    raw = df.copy()
    label_col = raw.columns[0]

    header_row_idx = None
    for i in range(min(5, len(raw))):
        row_vals = raw.iloc[i].astype(str)
        if row_vals.str.contains('2024', na=False).any() and row_vals.str.contains('2023', na=False).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        st.error("Не можат да се пронајдат заглавијата за оваа табела.")
        st.dataframe(df, use_container_width=True)
    else:
        header_row = raw.iloc[header_row_idx]
        year_cols = [col for col in raw.columns if str(header_row[col]).strip() in ['2024 година', '2023 година']]

        okg_2024_col, okg_2023_col = year_cols[0], year_cols[1]
        mem_2024_col, mem_2023_col = year_cols[2], year_cols[3]

        data_rows = raw.iloc[header_row_idx + 1:].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[~data_rows[label_col].astype(str).str.contains('Вкупно', na=False)]

        org_clean = pd.DataFrame({
            'Категорија': data_rows[label_col].values,
            'ОКГ 2024': pd.to_numeric(data_rows[okg_2024_col], errors='coerce').fillna(0),
            'ОКГ 2023': pd.to_numeric(data_rows[okg_2023_col], errors='coerce').fillna(0),
            'Членови 2024': pd.to_numeric(data_rows[mem_2024_col], errors='coerce').fillna(0),
            'Членови 2023': pd.to_numeric(data_rows[mem_2023_col], errors='coerce').fillna(0),
        }).dropna(subset=['Категорија'])

        cat_order = org_clean['Категорија'].tolist()
        col1, col2 = st.columns(2)

        with col1:
            st.write("**ОКГ: 2024 vs 2023 година**")
            melted_okg = org_clean.rename(columns={'ОКГ 2024': '2024 година', 'ОКГ 2023': '2023 година'}).melt(id_vars=['Категорија'], value_vars=['2024 година', '2023 година'], var_name='Година', value_name='Број')
            base_okg = alt.Chart(melted_okg).encode(
                y=alt.Y('Категорија:N', sort=cat_order, title=None, axis=alt.Axis(labelLimit=280)),
                x=alt.X('Број:Q', title='Број'),
                color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8']), legend=alt.Legend(title="Година")),
                yOffset='Година:N'
            )
            bars_okg = base_okg.mark_bar()
            text_okg = base_okg.mark_text(align='left', dx=3).encode(text='Број:Q')
            st.altair_chart((bars_okg + text_okg).properties(height=400), use_container_width=True)

        with col2:
            st.write("**Членови на криминални групи: 2024 vs 2023 година**")
            melted_mem = org_clean.rename(columns={'Членови 2024': '2024 година', 'Членови 2023': '2023 година'}).melt(id_vars=['Категорија'], value_vars=['2024 година', '2023 година'], var_name='Година', value_name='Број')
            base_mem = alt.Chart(melted_mem).encode(
                y=alt.Y('Категорија:N', sort=cat_order, title=None, axis=alt.Axis(labelLimit=280)),
                x=alt.X('Број:Q', title='Број', scale=alt.Scale(domain=[0, 80])),
                color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#2ca02c', '#a8dba8']), legend=alt.Legend(title="Година")),
                yOffset='Година:N'
            )
            bars_mem = base_mem.mark_bar()
            text_mem = base_mem.mark_text(align='left', dx=3).encode(text='Број:Q')
            st.altair_chart((bars_mem + text_mem).properties(height=400), use_container_width=True)

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)

# 4. ГРАФИКОНИ ЗА ВКУПЕН КРИМИНАЛИТЕТ
elif "Вкупен" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    for col in valid_rows.columns[1:]: valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')
    sector_order = valid_rows[sector_col].tolist()

    kd_col = valid_rows.columns[2]          
    storiteli_col = valid_rows.columns[6]  
    stapka_col = valid_rows.columns[7]     
    efikasnost_col = valid_rows.columns[8]  

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет за 2024 година по СВР**")
        st.altair_chart(
            alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
                x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)),
                y=alt.Y(f'{kd_col}:Q', title='Кривични дела')
            ).properties(height=350),
            use_container_width=True
        )
    with col2:
        st.write("**Сторители**")
        st.altair_chart(
            alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
                y=alt.Y(f'{sector_col}:N', sort=sector_order, title=None),
                x=alt.X(f'{storiteli_col}:Q', title='Сторители')
            ).properties(height=350),
            use_container_width=True
        )

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапка на криминалитет**")
        base_stapka = alt.Chart(valid_rows).encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)),
            y=alt.Y(f'{stapka_col}:Q', title='Стапка на криминал')
        )
        line_stapka = base_stapka.mark_line(color=BLUE_COLOR, point=alt.OverlayMarkDef(color=BLUE_COLOR))
        st.altair_chart(line_stapka.properties(height=350), use_container_width=True)
    with col4:
        st.write("**Вкупна ефикасност 2024 година**")
        st.altair_chart(
            alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
                y=alt.Y(f'{sector_col}:N', sort=sector_order, title=None),
                x=alt.X(f'{efikasnost_col}:Q', title='Ефикасност')
            ).properties(height=350),
            use_container_width=True
        )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4.5 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА УБИСТВА (ХОРИЗОНТАЛЕН ГРАФИК + LOLLIPOP ЗА ПРОМЕНА %)
elif "Убиства" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    col_2024 = valid_rows.columns[3]
    col_2023 = valid_rows.columns[4]
    col_change = valid_rows.columns[6]

    ubistva_clean = pd.DataFrame({
        'СВР': valid_rows[sector_col].values,
        '2024 година': pd.to_numeric(valid_rows[col_2024], errors='coerce').fillna(0),
        '2023 година': pd.to_numeric(valid_rows[col_2023], errors='coerce').fillna(0),
        'Промена': pd.to_numeric(valid_rows[col_change], errors='coerce')
    })

    ubistva_clean['Промена текст'] = ubistva_clean['Промена'].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) and isinstance(x, (int, float)) else str(x)
    )
    ubistva_clean['zero'] = 0
    sector_order = ubistva_clean['СВР'].tolist()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Убиства: 2024 vs 2023 година**")
        melted_u = ubistva_clean.melt(id_vars=['СВР'], value_vars=['2024 година', '2023 година'], var_name='Година', value_name='Број')
        
        base_u = alt.Chart(melted_u).encode(
            y=alt.Y('СВР:N', title=None, sort=sector_order, axis=alt.Axis(labelLimit=280)),
            x=alt.X('Број:Q', title='Број', axis=alt.Axis(format='d', tickMinStep=1)),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#aec7e8']), legend=alt.Legend(title="Година")),
            yOffset='Година:N'
        )
        bars_u = base_u.mark_bar()
        text_u = base_u.mark_text(align='left', dx=3, baseline='middle').encode(text='Број:Q')
        st.altair_chart((bars_u + text_u).properties(height=380), use_container_width=True)

    with col2:
        st.write("**Промена на убиства (%) - Lollipop Chart**")
        base_loll = alt.Chart(ubistva_clean).encode(
            x=alt.X('СВР:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=280))
        )
        rule_loll = base_loll.mark_rule(color=BLUE_COLOR, strokeWidth=2).encode(
            y=alt.Y('Промена:Q', axis=alt.Axis(format='%'), title='Промена (%)'),
            y2='zero:Q'
        )
        circle_loll = base_loll.mark_circle(size=220, color=BLUE_COLOR).encode(
            y=alt.Y('Промена:Q', axis=alt.Axis(format='%'))
        )
        text_loll = base_loll.mark_text(align='center', dy=-16, fontSize=11).encode(
            y=alt.Y('Промена:Q'),
            text='Промена текст:N'
        )
        st.altair_chart((rule_loll + circle_loll + text_loll).properties(height=380), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 5. СТАНДАРДЕН ПРИКАЗ ЗА ДРУГИ ЛИСТОВИ
else:
    st.dataframe(df, use_container_width=True)
