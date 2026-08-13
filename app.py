# ... (код пред овој дел останува ист)

if "Криумчарење" in selected_sheet or "мигранти" in selected_sheet.lower():
    # Подготовка на податоци
    mig_rows = df.dropna(subset=[df.columns[0]]).copy()
    valid_mig = mig_rows[mig_rows.iloc[:, 0].astype(str).str.contains("Откриени|кривични|сторители|мигранти", case=False, na=False)].copy()
    
    # 1. Column Chart (Споредба 2024 vs 2023)
    df_mig_bars = pd.DataFrame({
        'Категорија': valid_mig.iloc[:, 0],
        '2024': pd.to_numeric(valid_mig.iloc[:, 3], errors='coerce'),
        '2023': pd.to_numeric(valid_mig.iloc[:, 6], errors='coerce')
    }).melt('Категорија', var_name='Година', value_name='Вредност')
    
    # 2. Horizontal Bar Chart (Процент на промена)
    df_mig_pct = pd.DataFrame({
        'Категорија': valid_mig.iloc[:, 0],
        'Процент': round(pd.to_numeric(valid_mig.iloc[:, 9], errors='coerce') * 100, 1)
    })
    df_mig_pct['Пр_Текст'] = df_mig_pct['Процент'].astype(str) + '%'

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Криумчарење на мигранти (2024 vs 2023)**")
        st.altair_chart(alt.Chart(df_mig_bars).mark_bar().encode(
            x=alt.X('Категорија:N', title='Категорија', sort=None),
            y=alt.Y('Вредност:Q', title='Број'),
            color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])),
            xOffset='Година:N'
        ).properties(height=350), use_container_width=True)

    with col2:
        st.write("**Процент на промена по категории**")
        st.altair_chart(alt.Chart(df_mig_pct).mark_bar(color='#d62728').encode(
            y=alt.Y('Категорија:N', title='Категорија', sort=None),
            x=alt.X('Процент:Q', title='Процент (%)'),
            text=alt.Text('Пр_Текст:N')
        ).mark_bar().encode(
            y=alt.Y('Категорија:N', sort='-x'),
            x=alt.X('Процент:Q')
        ).properties(height=350) + alt.Chart(df_mig_pct).mark_text(align='left', dx=5).encode(
            y=alt.Y('Категорија:N', sort='-x'),
            x=alt.X('Процент:Q'),
            text='Пр_Текст:N'
        ), use_container_width=True)

# ... (остатокот од кодот за другите листови)
