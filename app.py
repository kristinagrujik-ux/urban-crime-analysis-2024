if "Криумчарење" in selected_sheet or "мигранти" in selected_sheet.lower():
    mig_rows = df.dropna(subset=[df.columns[0]]).copy()
    valid_mig = mig_rows[mig_rows.iloc[:, 0].astype(str).str.contains("Откриени|кривични|сторители|мигранти", case=False, na=False)].copy()
    
    df_mig_bars = pd.DataFrame({
        'Категорија': valid_mig.iloc[:, 0],
        '2024': pd.to_numeric(valid_mig.iloc[:, 5], errors='coerce'),
        '2023': pd.to_numeric(valid_mig.iloc[:, 8], errors='coerce')
    }).melt('Категорија', var_name='Година', value_name='Вредност')
    
    df_mig_pct = pd.DataFrame({
        'Категорија': valid_mig.iloc[:, 0],
        'Процент': round(pd.to_numeric(valid_mig.iloc[:, 11], errors='coerce') * 100, 1)
    })
    df_mig_pct['Пр_Текст'] = df_mig_pct['Процент'].astype(str) + '%'

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Криумчарење на мигранти (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_mig_bars).mark_bar().encode(
            x=alt.X('Категорија:N', title='Категорија', sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Вредност:Q', title='Број (Лог скала)', scale=alt.Scale(type='log')),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])),
            xOffset='Година:N'
        ).properties(height=350), use_container_width=True)

    with col2:
        st.write("**Процент на промена по категории**")
        # labelLimit=300 овозможува подолг текст на категориите да биде хоризонтален
        bar_chart = alt.Chart(df_mig_pct).mark_bar(color='#d62728').encode(
            y=alt.Y('Категорија:N', title='Категорија', sort='-x', axis=alt.Axis(labelAngle=0, labelLimit=300)),
            x=alt.X('Процент:Q', title='Процент (%)')
        )
        text_chart = alt.Chart(df_mig_pct).mark_text(align='left', dx=5).encode(
            y=alt.Y('Категорија:N', sort='-x'),
            x=alt.X('Процент:Q'),
            text='Пр_Текст:N'
        )
        st.altair_chart((bar_chart + text_chart).properties(height=350), use_container_width=True)
