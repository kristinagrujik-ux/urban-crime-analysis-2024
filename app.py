# 4.7 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ТРГОВИЈА СО ЛУЃЕ
elif "Трговија со луѓе" in selected_sheet:
    raw = df.copy()
    label_col = raw.columns[0]

    # Најди ги СИТЕ редови што личат на заглавие (содржат 2024, 2023 и 2022 истовремено)
    header_indices = []
    for i in range(len(raw)):
        row_vals = raw.iloc[i].astype(str)
        if row_vals.str.contains('2024', na=False).any() and row_vals.str.contains('2023', na=False).any() and row_vals.str.contains('2022', na=False).any():
            header_indices.append(i)

    if not header_indices:
        st.error("Не можат да се пронајдат заглавијата за оваа табела.")
        st.dataframe(df, use_container_width=True)
    else:
        blocks = []
        for idx, header_row_idx in enumerate(header_indices):
            header_row = raw.iloc[header_row_idx]
            col_map = {}
            for col in raw.columns:
                val = str(header_row[col]).strip()
                if val in ['2024 година', '2023 година', '2022 година']:
                    col_map[val] = col
            col_2024 = col_map.get('2024 година')
            col_2023 = col_map.get('2023 година')
            col_2022 = col_map.get('2022 година')

            # Блокот трае до следното заглавие (или до крајот на листот)
            end_idx = header_indices[idx + 1] if idx + 1 < len(header_indices) else len(raw)
            data_rows = raw.iloc[header_row_idx + 1:end_idx].copy()
            data_rows = data_rows[data_rows[label_col].notna()]
            data_rows = data_rows[~data_rows[label_col].astype(str).str.contains('Вкупно', na=False)]

            block_df = pd.DataFrame({
                'Категорија': data_rows[label_col].values,
                '2024 година': pd.to_numeric(data_rows[col_2024], errors='coerce').fillna(0),
                '2023 година': pd.to_numeric(data_rows[col_2023], errors='coerce').fillna(0),
                '2022 година': pd.to_numeric(data_rows[col_2022], errors='coerce').fillna(0),
            }).dropna(subset=['Категорија'])

            # Насловот на блокот го земаме од самата ќелија со заглавие (лево)
            raw_title = str(header_row[label_col]).strip()
            if raw_title.lower() in ['nan', 'none', '']:
                raw_title = "Трговија со луѓе" if idx == 0 else "Трговија со деца"
            clean_title = raw_title.replace('„', '').replace('"', '').replace('“', '').replace('Кривични дела', '').strip(' :')
            if not clean_title:
                clean_title = "Трговија со луѓе" if idx == 0 else "Трговија со деца"

            blocks.append((clean_title, block_df))

        # Прикажуваме по еден график во колона за секој пронајден блок (макс. 2 во ред)
        num_cols = min(len(blocks), 2)
        cols = st.columns(num_cols)

        color_palettes = [
            ['#1f77b4', '#6baed6', '#c6dbef'],
            ['#d62728', '#f4a582', '#fddbc7'],
        ]

        for i, (title, block_df) in enumerate(blocks):
            target_col = cols[i % num_cols]
            with target_col:
                st.write(f"**{title}: 2024 vs 2023 vs 2022 година**")
                if not block_df.empty:
                    order = block_df['Категорија'].tolist()
                    melted = block_df.melt(id_vars=['Категорија'], value_vars=['2024 година', '2023 година', '2022 година'], var_name='Година', value_name='Број')
                    palette = color_palettes[i % len(color_palettes)]
                    base = alt.Chart(melted).encode(
                        x=alt.X('Категорија:N', title=None, sort=order, axis=alt.Axis(labelAngle=270, labelLimit=200)),
                        y=alt.Y('Број:Q', title='Број'),
                        color=alt.Color('Година:N', scale=alt.Scale(domain=['2024 година', '2023 година', '2022 година'], range=palette), legend=alt.Legend(title="Година")),
                        xOffset='Година:N'
                    )
                    bars = base.mark_bar()
                    text = base.mark_text(dy=-8).encode(text='Број:Q')
                    st.altair_chart((bars + text).properties(height=380), use_container_width=True)
                else:
                    st.info(f"Нема податоци за {title}.")

        st.subheader("📋 Детална табела")
        for title, block_df in blocks:
            st.write(f"**{title}**")
            display_df = block_df.rename(columns={'Категорија': 'Кривични дела'}).copy()
            for col in ['2024 година', '2023 година', '2022 година']:
                display_df[col] = display_df[col].astype(int)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
