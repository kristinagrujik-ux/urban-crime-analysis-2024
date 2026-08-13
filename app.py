import streamlit as st
import pandas as pd
import altair as alt

# ... (претходниот дел од кодот со set_page_config и load_data останува ист)

if "Недозволена" in selected_sheet or "дрога" in selected_sheet.lower():
    valid_rows = df[df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)].copy()
    
    # Подготовка на податоци за Lollipop (Пресметување на разлика за Diverging ефект)
    def prep_lollipop(data, val_2024, val_2023):
        df_lp = pd.DataFrame({'Сектор': data.iloc[:, 0], '2024': data.iloc[:, val_2024], '2023': data.iloc[:, val_2023]})
        df_lp['Разлика'] = df_lp['2024'] - df_lp['2023']
        return df_lp

    df_lp1 = prep_lollipop(valid_rows, 3, 4)
    df_lp2 = prep_lollipop(valid_rows, 6, 7)

    def draw_lollipop(data, title):
        # Линија (Rule)
        base = alt.Chart(data).encode(y=alt.Y('Сектор:N', sort='-x'))
        rule = base.mark_rule(color='gray').encode(x='min(2023, 2024)', x2='max(2023, 2024)')
        # Точки (Circle)
        points = base.mark_circle(size=100).encode(
            x='Разлика:Q', 
            color=alt.condition(alt.datum.Разлика > 0, alt.value('red'), alt.value('blue'))
        )
        return (rule + points).properties(title=title, height=300)

    # 1. Ред: Кривични дела (Бар лево + Lollipop десно)
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Кривични дела (2024 vs 2023)**")
        # Оставаме бар графикон како што беше претходно
        st.altair_chart(alt.Chart(df_lp1.melt('Сектор', ['2024', '2023'])).mark_bar().encode(
            y=alt.Y('Сектор:N'), yOffset='variable:N', x='value:Q', color='variable:N'
        ), use_container_width=True)
    with col2:
        st.write("**Diverging Lollipop: Кривични дела**")
        st.altair_chart(draw_lollipop(df_lp1, "Разлика 2024-2023"), use_container_width=True)

    # 2. Ред: Сторители (Бар лево + Lollipop десно)
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Сторители (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_lp2.melt('Сектор', ['2024', '2023'])).mark_bar().encode(
            y=alt.Y('Сектор:N'), yOffset='variable:N', x='value:Q', color='variable:N'
        ), use_container_width=True)
    with col4:
        st.write("**Diverging Lollipop: Сторители**")
        st.altair_chart(draw_lollipop(df_lp2, "Разлика 2024-2023"), use_container_width=True)

# ... (остатокот од кодот за else и табелата)
