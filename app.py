# Втор ред: Лево е Стапката на криминалитетот (линиски), Десно е Вкупна ефикасност (хоризонтален бар)
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапката на криминалитетот**")
        # Со промена на x и y, линијата сега ќе биде вертикална (ориентирана како во Excel)
        st.altair_chart(alt.Chart(valid_rows).mark_line(color=BLUE_COLOR, point=True).encode(
            y=alt.Y(f'{sector_col}:N', title='Сектор', sort=None),
            x=alt.X(f'{st_col}:Q', title='Стапка')
        ).properties(height=320), use_container_width=True)

    with col4:
        st.write("**Вкупна ефикасност 2024**")
        st.altair_chart(alt.Chart(valid_rows).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(f'{sector_col}:N', title='Сектор', sort=None),
            x=alt.X(f'{ef_col}:Q', title='Процент')
        ).properties(height=320), use_container_width=True)
