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

# 2. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА НЕДОЗВОЛЕНА ТРГОВИЈА СО ДРОГА
elif "трговија" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    col_2024 = valid_rows.columns[3]
    col_2023 = valid_rows.columns[4]
    
    col_stor_2024 = valid_rows.columns[6]
    col_stor_2023 = valid_rows.columns[7]

    valid_rows = valid_rows.rename(columns={
        col_2024: "2024 година", 
        col_2023: "2023 година", 
        col_stor_2024: "Сторители 2024", 
        col_stor_2023: "Сторители 2023"
    })
    
    c24 = "2024 година"
    c23 = "2023 година"
    c_stor_24 = "Сторители 2024"
    c_stor_23 = "Сторители 2023"

    for col in [c24, c23, c_stor_24, c_stor_23]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    sector_order = valid_rows[sector_col].tolist()

    col1, col2 = st.columns(2)
    
    # 1. Вкупни КД: 2024 vs 2023 (Групиран хоризонтален Bar)
    with col1:
        st.write("**Вкупни КД: 2024 vs 2023**")
        df_melted_kd = valid_rows.melt(id_vars=[sector_col], value_vars=[c24, c23], var_name='Година', value_name='Број')
        bar_v = alt.Chart(df_melted_kd).mark_bar().encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelLimit=200)),
            x=alt.X('Број:Q', title='Број на дела'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=[c24, c23], range=['#1f77b4', '#d62728']), legend=alt.Legend(title="Година")),
            yOffset='Година:N'
        ).properties(height=350)
        st.altair_chart(bar_v, use_container_width=True)

    # 2. Lollipop график (2024 КД)
    with col2:
        st.write("**Недозволена трговија (2024)**")
        base_n = alt.Chart(valid_rows).encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y(f'{c24}:Q', title='Број')
        )
        rule_n = base_n.mark_rule(color=BLUE_COLOR, strokeWidth=2)
        points_n = base_n.mark_circle(size=80, color=BLUE_COLOR)
        text_n = base_n.mark_text(align='center', baseline='bottom', dy=-10).encode(text=alt.Text(f'{c24}:Q'))
        st.altair_chart((rule_n + points_n + text_n).properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    
    # 3. Сторители: 2024 vs 2023 (Групиран хоризонтален Bar)
    with col3:
        st.write("**Сторители: 2024 vs 2023**")
        df_melted_stor = valid_rows.melt(id_vars=[sector_col], value_vars=[c_stor_24, c_stor_23], var_name='Година', value_name='Број')
        df_melted_stor['Година'] = df_melted_stor['Година'].replace({c_stor_24: '2024 година', c_stor_23: '2023 година'})
        
        bar_s = alt.Chart(df_melted_stor).mark_bar().encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelLimit=200)),
            x=alt.X('Број:Q', title='Број на сторители'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година'], range=['#1f77b4', '#d62728']), legend=alt.Legend(title="Година")),
            yOffset='Година:N'
        ).properties(height=350)
        st.altair_chart(bar_s, use_container_width=True)

    # 4. Lollipop график (2023 КД)
    with col4:
        st.write("**Споредба 2023 година**")
        base_23 = alt.Chart(valid_rows).encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y(f'{c23}:Q', title='Број')
        )
        rule_23 = base_23.mark_rule(color='#d62728', strokeWidth=2)
        points_23 = base_23.mark_circle(size=80, color='#d62728')
        text_23 = base_23.mark_text(align='center', baseline='bottom', dy=-10).encode(text=alt.Text(f'{c23}:Q'))
        st.altair_chart((rule_23 + points_23 + text_23).properties(height=350), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3. ГРАФИКОНИ ЗА ВКУПЕН КРИМИНАЛИТЕТ
elif "Вкупен" in selected_sheet:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    for col in valid_rows.columns[1:]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    c_col = valid_rows.columns[2]     
    s_col = valid_rows.columns[7]     
    st_col = valid_rows.columns[8]    
    ef_col = valid_rows.columns[6]    

    sector_order = valid_rows[sector_col].tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет за 2024 година по СВР**")
        bar_c = alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y(f'{c_col}:Q', title='Број')
        )
        st.altair_chart(bar_c.properties(height=350), use_container_width=True)

    with col2:
        st.write("**Сторители**")
        bar_s = alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelLimit=200)),
            x=alt.X(f'{s_col}:Q', title='Број')
        )
        st.altair_chart(bar_s.properties(height=350), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапката на криминалитетот**")
        line_st = alt.Chart(valid_rows).mark_line(color=BLUE_COLOR).encode(
            x=alt.X(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
            y=alt.Y(f'{st_col}:Q', title='Стапка', scale=alt.Scale(zero=False))
        )
        points_st = line_st.mark_circle(size=60, color=BLUE_COLOR)
        st.altair_chart((line_st + points_st).properties(height=350), use_container_width=True)

    with col4:
        st.write("**Вкупна ефикасност 2024**")
        bar_ef = alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', title=None, sort=sector_order, axis=alt.Axis(labelLimit=200)),
            x=alt.X(f'{ef_col}:Q', title='Расветлени КД')
        )
        st.altair_chart(bar_ef.properties(height=350), use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4. СТАНДАРДЕН ПРИКАЗ ЗА ДРУГИ ЛИСТОВИ
else:
    st.dataframe(df, use_container_width=True)
