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

if "Криумчарење" in selected_sheet or "мигранти" in selected_sheet.lower():
    mig_rows = df.dropna(subset=[df.columns[0]]).copy()
    valid_mig = mig_rows[mig_rows.iloc[:, 0].astype(str).str.contains("Откриени|кривични|сторители|мигранти", case=False, na=False)].copy()
    
    kategorii = valid_mig.iloc[:, 0].astype(str)
    
    df_mig_bars = pd.DataFrame({
        'Категорија': kategorii,
        '2024': pd.to_numeric(valid_mig.iloc[:, 5], errors='coerce'),
        '2023': pd.to_numeric(valid_mig.iloc[:, 8], errors='coerce')
    }).melt('Категорија', var_name='Година', value_name='Вредност')
    
    df_mig_pct = pd.DataFrame({
        'Категорија': kategorii,
        'Процент': round(pd.to_numeric(valid_mig.iloc[:, 11], errors='coerce') * 100, 1)
    })
    df_mig_pct['Пр_Текст'] = df_mig_pct['Процент'].astype(str) + '%'

    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Криумчарење на мигранти (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_mig_bars).mark_bar().encode(
            x=alt.X('Категорија:N', title='Категорија', sort=None, axis=alt.Axis(labelAngle=270, labelLimit=600)),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])),
            xOffset='Година:N'
        ).properties(height=420), use_container_width=True)

    with col2:
        st.write("**Процент на промена по категории**")
        
        df_mig_pct_sorted = df_mig_pct.sort_values(by='Процент', ascending=True).reset_index(drop=True)
        sorted_cats = df_mig_pct_sorted['Категорија'].tolist()

        bar_chart = alt.Chart(df_mig_pct_sorted).mark_bar(color='#d62728').encode(
            y=alt.Y('Категорија:N', title='Категорија', sort=sorted_cats, axis=alt.Axis(labelAngle=0, labelLimit=300)),
            x=alt.X('Процент:Q', title='Процент (%)')
        )
        text_chart = alt.Chart(df_mig_pct_sorted).mark_text(align='left', dx=5).encode(
            y=alt.Y('Категорија:N', sort=sorted_cats),
            x=alt.X('Процент:Q'),
            text='Пр_Текст:N'
        )
        st.altair_chart((bar_chart + text_chart).properties(height=420), use_container_width=True)

elif "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    
    df_kd = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 3], '2023': valid_rows.iloc[:, 4]}).melt('Сектор', var_name='Година', value_name='Вредност')
    df_st = pd.DataFrame({'Сектор': valid_rows.iloc[:, 0], '2024': valid_rows.iloc[:, 6], '2023': valid_rows.iloc[:, 7]}).melt('Сектор', var_name='Година', value_name='Вредност')
    
    color_scale = alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])

    def prep_lollipop(data, val_col):
        val = round(pd.to_numeric(data.iloc[:, val_col], errors='coerce') * 100, 1)
        df_lp = pd.DataFrame({
            'Сектор': data.iloc[:, 0], 
            'Процент': val,
            'Пр_Текст': val.astype(str) + '%'
        })
        df_lp['zero'] = 0
        return df_lp

    df_lp1 = prep_lollipop(valid_rows, 5)
    df_lp2 = prep_lollipop(valid_rows, 8)

    def draw_lollipop(data, title):
        base = alt.Chart(data).encode(x=alt.X('Сектор:N', sort=None, title='Сектор'))
        rule = base.mark_rule(color='#e45756', strokeWidth=2).encode(y='zero:Q', y2='Процент:Q')
        points = base.mark_circle(size=120, color='#e45756').encode(y=alt.Y('Процент:Q', title='Процент (%)'))
        text = base.mark_text(align='center', baseline='bottom', dy=-10).encode(
            y=alt.Y('Процент:Q'),
            text='Пр_Текст:N'
        )
        return (rule + points + text).properties(title=title, height=350)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_kd).mark_bar().encode(
            y=alt.Y('Сектор:N', sort=None, title='Сектор'),
            yOffset=alt.YOffset('Година:N'),
            x=alt.X('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=color_scale)
        ).properties(height=350), use_container_width=True)
    with col2:
        st.write("**Lollipop Chart: Промена % - Кривични дела**")
        st.altair_chart(draw_lollipop(df_lp1, "Процент на промена кај кривични дела"), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_st).mark_bar().encode(
            y=alt.Y('Сектор:N', sort=None, title='Сектор'),
            yOffset=alt.YOffset('Година:N'),
            x=alt.X('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=color_scale)
        ).properties(height=350), use_container_width=True)
    with col4:
        st.write("**Lollipop Chart: Промена % - Сторители**")
        st.altair_chart(draw_lollipop(df_lp2, "Процент на промена кај сторители"), use_container_width=True)

else:
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    sector_col = valid_rows.columns[0]
    
    for col in valid_rows.columns[1:]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors='coerce')

    c_col = valid_rows.columns[2] if len(valid_rows.columns) > 2 else valid_rows.columns[1]
    
    col_names = list(valid_rows.columns)
    s_col = next((c for c in col_names if 'сторители' in str(c).lower()), col_names[7] if len(col_names) > 7 else col_names[-1])
    st_col = next((c for c in col_names if 'стапка' in str(c).lower() and 'кримин' in str(c).lower()), col_names[8] if len(col_names) > 8 else s_col)
    ef_col = next((c for c in col_names if 'ефикасност' in str(c).lower()), col_names[9] if len(col_names) > 9 else s_col)

    BLUE_COLOR = '#1f77b4'

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет за 2024 година по СВР**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y(f'{c_col}:Q', title='Број', axis=alt.Axis(format='d'))
        ).properties(height=320), use_container_width=True)

    with col2:
        st.write("**Сторители**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', title='Сектор', sort=None),
            x=alt.X(f'{s_col}:Q', title='Број', axis=alt.Axis(format='d'))
        ).properties(height=320), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапката на криминалитетот**")
        st.altair_chart(alt.Chart(valid_rows).mark_line(color=BLUE_COLOR, point=True).encode(
            x=alt.X(f'{sector_col}:N', title='Сектор', sort=None),
            y=alt.Y(f'{st_col}:Q', title='Стапка')
        ).properties(height=320), use_container_width=True)

    with col4:
        st.write("**Вкупна ефикасност 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', title='Сектор', sort=None),
            x=alt.X(f'{ef_col}:Q', title='Процент')
        ).properties(height=320), use_container_width=True)

st.subheader("📋 Детална табела")
st.dataframe(df, use_container_width=True)
