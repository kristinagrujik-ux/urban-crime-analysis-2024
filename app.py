elif "Организиран" in selected_sheet:
    # Ги земаме сите редови каде што првата колона не е празна
    valid_rows = df.dropna(subset=[df.columns[0]]).copy()
    
    categories = []
    vals_2024 = []
    vals_2023 = []

    for idx, row in valid_rows.iterrows():
        cat = str(row.iloc[0]).strip()
        # Ги прескокнуваме насловните редови и редот "Вкупно" за да не ја расипува скалата
        if cat and cat.lower() != 'nan' and "област на криминал" not in cat.lower() and "вкупно" not in cat.lower():
            
            # Читање на вредностите: 2024 е во колона индекс 6, 2023 е во колона индекс 8
            val_24 = pd.to_numeric(row.iloc[6], errors='coerce')
            val_23 = pd.to_numeric(row.iloc[8], errors='coerce')
            
            categories.append(cat)
            vals_2024.append(val_24 if pd.notna(val_24) else 0)
            vals_2023.append(val_23 if pd.notna(val_23) else 0)

    df_okg = pd.DataFrame({
        'Категорија': categories,
        '2024': vals_2024,
        '2023': vals_2023
    }).melt('Категорија', var_name='Година', value_name='Број')

    bars = alt.Chart(df_okg).mark_bar().encode(
        y=alt.Y('Категорија:N', title='Категорија', sort=None, axis=alt.Axis(labelLimit=300)),
        x=alt.X('Број:Q', title='Број на случаи', axis=alt.Axis(format='d')),
        color=alt.Color('Година:N', scale=alt.Scale(domain=['2024', '2023'], range=['#1f77b4', '#aec7e8'])),
        yOffset='Година:N',
        tooltip=['Категорија', 'Година', 'Број']
    )

    text = alt.Chart(df_okg).mark_text(align='left', baseline='middle', dx=3).encode(
        y=alt.Y('Категорија:N', sort=None),
        x=alt.X('Број:Q'),
        text='Број:Q',
        yOffset='Година:N'
    )

    chart = (bars + text).properties(title='Споредба на кривични дела (2023 vs 2024)', height=450).interactive()
    st.altair_chart(chart, use_container_width=True)
