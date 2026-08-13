with col1:
        st.write("**Криумчарење на мигранти (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_mig_bars).mark_bar().encode(
            # labelAngle=0 ги прави имињата хоризонтални
            x=alt.X('Категорија:N', title='Категорија', sort=None, axis=alt.Axis(labelAngle=0)),
            # Ја тргнавме лог-скалата за да се видат сите столбови
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])),
            xOffset='Година:N'
        ).properties(height=400), use_container_width=True)
