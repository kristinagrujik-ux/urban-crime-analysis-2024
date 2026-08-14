with col2:
        st.write("**Процент на промена по категории**")
        
        # 1. Подредување во pandas од најмал (најнегативен) кон најголем
        df_mig_pct_sorted = df_mig_pct.sort_values(by='Процент', ascending=True).reset_index(drop=True)
        sorted_cats = df_mig_pct_sorted['Категорија'].tolist()

        # 2. Форсирање на доменот во Altair за да ги подреди строго по листата
        bar_chart = alt.Chart(df_mig_pct_sorted).mark_bar(color='#d62728').encode(
            y=alt.Y('Категорија:N', title='Категорија', sort=sorted_cats, axis=alt.Axis(labelAngle=0, labelLimit=300)),
            x=alt.X('Процент:Q', title='Процент (%)')
        )
        text_chart = alt.Chart(df_mig_pct_sorted).mark_text(align='right', dx=-5).encode(
            y=alt.Y('Категорија:N', sort=sorted_cats),
            x=alt.X('Процент:Q'),
            text='Пр_Текст:N'
        )
        st.altair_chart((bar_chart + text_chart).properties(height=420), use_container_width=True)
