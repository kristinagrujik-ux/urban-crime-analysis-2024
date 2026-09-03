import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide"
)

file_path = "KRIMINALITET.xlsx"


@st.cache_data
def get_sheets():
    return pd.ExcelFile(file_path).sheet_names


selected_sheet = st.sidebar.selectbox("Избери категорија:", get_sheets())
st.title(f"📊 {selected_sheet}")


@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)


df = load_data(selected_sheet)
BLUE_COLOR = "#1f77b4"

# 1. СПЕЦИЈАЛЕН СЛУЧАЈ: Табела за Кривични дела против државата
if "Кривични дела против државата" in selected_sheet:
    table_data = [
        {
            "Кривични дела": "Предизвикување омраза и нетрпеливост",
            "2024 година": 10,
            "2023 година": 2,
            "Промена %": 4.0,
            "Промена текст": "пет пати ↗",
        },
        {
            "Кривични дела": "Учество во странска војска и полиција",
            "2024 година": 2,
            "2023 година": 0,
            "Промена %": 2.0,
            "Промена текст": "200%",
        },
        {
            "Кривични дела": "Неовластено навлегување и цртање на воени објекти",
            "2024 година": 2,
            "2023 година": 0,
            "Промена %": 2.0,
            "Промена текст": "200%",
        },
        {
            "Кривични дела": "Служба во непријателска војска",
            "2024 година": 0,
            "2023 година": 1,
            "Промена %": 0.0,
            "Промена текст": "0",
        },
        {
            "Кривични дела": "Расна и друга дискриминација",
            "2024 година": 1,
            "2023 година": 1,
            "Промена %": 0.0,
            "Промена текст": "0",
        },
        {
            "Кривични дела": "Вкупно кривични дела",
            "2024 година": 15,
            "2023 година": 4,
            "Промена %": 2.75,
            "Промена текст": "три и пол пати ↗",
        },
    ]
    df_display = pd.DataFrame(table_data)

    chart_data = df_display[
        df_display["Кривични дела"] != "Вкупно кривични дела"
    ].copy()
    chart_data["2024 година"] = pd.to_numeric(
        chart_data["2024 година"], errors="coerce"
    ).fillna(0)
    chart_data["2023 година"] = pd.to_numeric(
        chart_data["2023 година"], errors="coerce"
    ).fillna(0)
    chart_data = chart_data.rename(columns={"Промена %": "promena_procent"})
    cat_order_kd = chart_data["Кривични дела"].tolist()

    melted_kd = chart_data.melt(
        id_vars=["Кривични дела"],
        value_vars=["2024 година", "2023 година"],
        var_name="Година",
        value_name="Број",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Споредба по кривични дела (2024 vs 2023)**")
        base_kd_state = alt.Chart(melted_kd).encode(
            y=alt.Y(
                "Кривични дела:N",
                sort=cat_order_kd,
                title=None,
                axis=alt.Axis(labelLimit=320),
            ),
            x=alt.X(
                "Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)
            ),
            color=alt.Color(
                "Година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#228B22", "#50C878"],
                ),
                legend=alt.Legend(title="Година"),
            ),
            yOffset="Година:N",
        )
        bars_kd_state = base_kd_state.mark_bar()
        text_kd_state = base_kd_state.mark_text(
            align="left", dx=3, baseline="middle"
        ).encode(text="Број:Q")
        st.altair_chart(
            (bars_kd_state + text_kd_state).properties(height=350),
            use_container_width=True,
        )

    with col2:
        st.write("**Промена (%) - Хоризонтален Column Chart**")
        base_horiz = alt.Chart(chart_data).encode(
            y=alt.Y(
                "Кривични дела:N",
                sort=cat_order_kd,
                title=None,
                axis=alt.Axis(labelLimit=320, labelFontSize=11),
            ),
            x=alt.X(
                "promena_procent:Q",
                title="Промена (%)",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domain=[-0.2, 8.0], zero=True),
            ),
        )
        bars_horiz = base_horiz.mark_bar(color=BLUE_COLOR)
        text_horiz = base_horiz.mark_text(
            align="left", baseline="middle", dx=5, fontSize=11, fontWeight="bold"
        ).encode(text="Промена текст:N")
        chart_horizontal = (
            (bars_horiz + text_horiz)
            .properties(height=350)
            .configure_axis(gridColor="white", gridOpacity=0.8)
            .configure_view(fill="#eef0f2", stroke=None)
        )
        st.altair_chart(chart_horizontal, use_container_width=True)

    st.subheader("📋 Детална табела")
    df_table_show = df_display.copy()
    df_table_show["Промена %"] = [
        "пет пати ↗",
        "200%",
        "200%",
        "0",
        "0",
        "три и пол пати ↗",
    ]
    df_table_show = df_table_show.drop(columns=["Промена текст"])
    st.dataframe(df_table_show, use_container_width=True, hide_index=True)

# 2. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА КРИУМЧАРЕЊЕ НА МИГРАНТИ
elif "Криумчарење на мигранти" in selected_sheet:
    mig_df = df.iloc[:4, :].copy()
    cat_col = mig_df.columns[0]
    col_2024 = next(c for c in mig_df.columns if "2024" in str(c))
    col_2023 = next(c for c in mig_df.columns if "2023" in str(c))
    col_change = next(c for c in mig_df.columns if "Промена" in str(c))

    mig_clean = pd.DataFrame({
        "Категорија": mig_df[cat_col].values,
        "2024 година": pd.to_numeric(mig_df[col_2024], errors="coerce"),
        "2023 година": pd.to_numeric(mig_df[col_2023], errors="coerce"),
        "Промена": pd.to_numeric(mig_df[col_change], errors="coerce"),
    })
    mig_clean["Промена текст"] = mig_clean["Промена"].apply(
        lambda x: f"{x*100:.1f}%"
        if pd.notnull(x) and isinstance(x, (int, float))
        else str(x)
    )

    col1, col2 = st.columns(2)
    cat_order = mig_clean["Категорија"].tolist()

    with col1:
        st.write("**Споредба по категории: 2024 vs 2023**")
        melted_mig = mig_clean.melt(
            id_vars=["Категорија"],
            value_vars=["2024 година", "2023 година"],
            var_name="Година",
            value_name="Број",
        )
        chart_col = (
            alt.Chart(melted_mig)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Категорија:N",
                    title=None,
                    sort=cat_order,
                    axis=alt.Axis(labelAngle=270, labelLimit=200),
                ),
                y=alt.Y("Број:Q", title="Број"),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                xOffset="Година:N",
            )
        )
        st.altair_chart(chart_col.properties(height=380), use_container_width=True)

    with col2:
        st.write("**Промена (%) според категорија**")
        cat_order_reversed = cat_order[::-1]
        bar_change = alt.Chart(mig_clean).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(
                "Категорија:N",
                sort=cat_order_reversed,
                title=None,
                axis=alt.Axis(labelLimit=280, labelFontSize=11, labelPadding=10),
            ),
            x=alt.X(
                "Промена:Q",
                axis=alt.Axis(format="%", values=[-0.8, -0.6, -0.4, -0.2, 0]),
                title="Промена",
                scale=alt.Scale(domain=[-0.75, 0.05], zero=False),
            ),
        )
        text_change = bar_change.mark_text(align="left", dx=5).encode(
            x="Промена:Q", text="Промена текст:N"
        )
        st.altair_chart(
            (bar_change + text_change).properties(
                height=380, padding={"left": 20, "top": 5, "right": 20, "bottom": 5}
            ),
            use_container_width=True,
        )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3. СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА НЕДОЗВОЛЕНА ТРГОВИЈА СО ДРОГА
elif "трговија со дрога" in selected_sheet.lower():
    valid_rows = df[
        df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)
    ].copy()
    sector_col = valid_rows.columns[0]

    col_2024, col_2023 = valid_rows.columns[3], valid_rows.columns[4]
    col_change_kd = valid_rows.columns[5]
    col_stor_2024, col_stor_2023 = valid_rows.columns[6], valid_rows.columns[7]
    col_change_stor = valid_rows.columns[8]

    valid_rows = valid_rows.rename(
        columns={
            col_2024: "2024 година",
            col_2023: "2023 година",
            col_change_kd: "Промена КД %",
            col_stor_2024: "Сторители 2024",
            col_stor_2023: "Сторители 2023",
            col_change_stor: "Промена Сторители %",
        }
    )
    for col in [
        "2024 година",
        "2023 година",
        "Сторители 2024",
        "Сторители 2023",
    ]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors="coerce")

    valid_rows["Промена КД %"] = pd.to_numeric(
        valid_rows["Промена КД %"], errors="coerce"
    ).fillna(0)
    valid_rows["Промена Сторители %"] = pd.to_numeric(
        valid_rows["Промена Сторители %"], errors="coerce"
    ).fillna(0)

    valid_rows["Промена КД % текст"] = valid_rows["Промена КД %"].apply(
        lambda x: f"{x*100:.1f}%"
    )
    valid_rows["Промена Сторители % текст"] = valid_rows[
        "Промена Сторители %"
    ].apply(lambda x: f"{x*100:.1f}%")

    valid_rows["Насока КД"] = valid_rows["Промена КД %"].apply(
        lambda x: "Пораст" if x >= 0 else "Пад"
    )
    valid_rows["Насока Сторители"] = valid_rows["Промена Сторители %"].apply(
        lambda x: "Пораст" if x >= 0 else "Пад"
    )
    valid_rows["zero"] = 0
    sector_order = valid_rows[sector_col].tolist()

    c1, c2 = st.columns(2)
    with c1:
        st.write("**Вкупни КД: 2024 vs 2023**")
        df_melted_kd = valid_rows.melt(
            id_vars=[sector_col],
            value_vars=["2024 година", "2023 година"],
            var_name="Година",
            value_name="Број",
        )
        st.altair_chart(
            alt.Chart(df_melted_kd)
            .mark_bar()
            .encode(
                y=alt.Y(f"{sector_col}:N", sort=sector_order, title=None),
                x=alt.X("Број:Q", title="Број"),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                yOffset="Година:N",
            )
            .properties(height=350),
            use_container_width=True,
        )

    with c2:
        st.write("**Недозволена трговија со дрога - Промена на кривични дела (%)**")
        base_kd = alt.Chart(valid_rows).encode(
            x=alt.X(
                f"{sector_col}:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            )
        )
        color_enc_kd = alt.Color(
            "Насока КД:N",
            scale=alt.Scale(domain=["Пораст", "Пад"], range=["#2ca02c", "#d62728"]),
            legend=alt.Legend(title=None),
        )
        rule_kd = base_kd.mark_rule(strokeWidth=2).encode(
            y=alt.Y(
                "Промена КД %:Q",
                axis=alt.Axis(format="%"),
                title="Промена",
                scale=alt.Scale(zero=True),
            ),
            y2="zero:Q",
            color=color_enc_kd,
        )
        circle_kd = base_kd.mark_circle(size=220).encode(
            y="Промена КД %:Q", color=color_enc_kd
        )
        text_kd_pos = (
            base_kd.transform_filter(alt.datum["Промена КД %"] >= 0)
            .mark_text(align="center", dy=-16, fontSize=11)
            .encode(y="Промена КД %:Q", text="Промена КД % текст:N")
        )
        text_kd_neg = (
            base_kd.transform_filter(alt.datum["Промена КД %"] < 0)
            .mark_text(align="center", dy=18, fontSize=11)
            .encode(y="Промена КД %:Q", text="Промена КД % текст:N")
        )
        st.altair_chart(
            (rule_kd + circle_kd + text_kd_pos + text_kd_neg).properties(
                height=350
            ),
            use_container_width=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        st.write("**Сторители: 2024 vs 2023**")
        df_melted_stor = valid_rows.melt(
            id_vars=[sector_col],
            value_vars=["Сторители 2024", "Сторители 2023"],
            var_name="Година",
            value_name="Број",
        )
        st.altair_chart(
            alt.Chart(df_melted_stor)
            .mark_bar()
            .encode(
                y=alt.Y(f"{sector_col}:N", sort=sector_order, title=None),
                x=alt.X("Број:Q", title="Број"),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["Сторители 2024", "Сторители 2023"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                yOffset="Година:N",
            )
            .properties(height=350),
            use_container_width=True,
        )

    with c4:
        st.write("**Недозволена трговија со дрога - Промена на сторители (%)**")
        base_stor = alt.Chart(valid_rows).encode(
            x=alt.X(
                f"{sector_col}:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            )
        )
        color_enc_stor = alt.Color(
            "Насока Сторители:N",
            scale=alt.Scale(domain=["Пораст", "Пад"], range=["#2ca02c", "#d62728"]),
            legend=alt.Legend(title=None),
        )
        rule_stor = base_stor.mark_rule(strokeWidth=2).encode(
            y=alt.Y(
                "Промена Сторители %:Q",
                axis=alt.Axis(format="%"),
                title="Промена",
                scale=alt.Scale(zero=True),
            ),
            y2="zero:Q",
            color=color_enc_stor,
        )
        circle_stor = base_stor.mark_circle(size=220).encode(
            y="Промена Сторители %:Q", color=color_enc_stor
        )
        text_stor_pos = (
            base_stor.transform_filter(alt.datum["Промена Сторители %"] >= 0)
            .mark_text(align="center", dy=-16, fontSize=11)
            .encode(y="Промена Сторители %:Q", text="Промена Сторители % текст:N")
        )
        text_stor_neg = (
            base_stor.transform_filter(alt.datum["Промена Сторители %"] < 0)
            .mark_text(align="center", dy=18, fontSize=11)
            .encode(y="Промена Сторители %:Q", text="Промена Сторители % текст:N")
        )
        st.altair_chart(
            (rule_stor + circle_stor + text_stor_pos + text_stor_neg).properties(
                height=350
            ),
            use_container_width=True,
        )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3.4 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА КОРУПЦИЈА (Подесен со колони за да не биде премногу широк)
elif "Корупција" in selected_sheet:

    @st.cache_data
    def load_korupcija(sheet):
        return pd.read_excel(file_path, sheet_name=sheet, header=4)

    try:
        raw_k = load_korupcija(selected_sheet)
        if len(raw_k.columns) > 0:
            raw_k = raw_k.dropna(subset=[raw_k.columns[0]])

        korupcija_clean = pd.DataFrame({
            "СВР": raw_k.iloc[:, 0].values,
            "КД 2024": pd.to_numeric(raw_k.iloc[:, 4], errors="coerce").fillna(0),
            "КД 2023": pd.to_numeric(raw_k.iloc[:, 5], errors="coerce").fillna(0),
            "Промена %": pd.to_numeric(raw_k.iloc[:, 6], errors="coerce").fillna(0) / 100.0,
            "Сторители 2024": pd.to_numeric(raw_k.iloc[:, 7], errors="coerce").fillna(0),
            "Сторители 2023": pd.to_numeric(raw_k.iloc[:, 8], errors="coerce").fillna(0),
        })

        korupcija_clean = korupcija_clean[
            korupcija_clean["СВР"].astype(str).str.contains("СВР|ОСОСК", na=False)
        ]
        
        sector_order = korupcija_clean["СВР"].tolist()
        
        korupcija_clean["Промена % текст"] = korupcija_clean["Промена %"].apply(
            lambda x: f"{x*100:.1f}%"
        )
        korupcija_clean["Насока"] = korupcija_clean["Промена %"].apply(
            lambda x: "Пораст" if x >= 0 else "Пад"
        )
        korupcija_clean["zero"] = 0

        melted_kd_k = korupcija_clean.melt(
            id_vars=["СВР"],
            value_vars=["КД 2024", "КД 2023"],
            var_name="Година",
            value_name="Број",
        )
        melted_kd_k["Година"] = melted_kd_k["Година"].replace(
            {"КД 2024": "2024 година", "КД 2023": "2023 година"}
        )

        melted_stor_k = korupcija_clean.melt(
            id_vars=["СВР"],
            value_vars=["Сторители 2024", "Сторители 2023"],
            var_name="Година",
            value_name="Број",
        )
        melted_stor_k["Година"] = melted_stor_k["Година"].replace(
            {"Сторители 2024": "2024 година", "Сторители 2023": "2023 година"}
        )

        base_kd_k = alt.Chart(melted_kd_k).encode(
            x=alt.X(
                "СВР:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            ),
            y=alt.Y(
                "Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)
            ),
            color=alt.Color(
                "Година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#1f77b4", "#aec7e8"],
                ),
                legend=alt.Legend(title="Година"),
            ),
            xOffset="Година:N",
        )
        bars_kd_k = base_kd_k.mark_bar()

        base_stor_k = alt.Chart(melted_stor_k).encode(
            x=alt.X(
                "СВР:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            ),
            y=alt.Y(
                "Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)
            ),
            color=alt.Color(
                "Година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#1f77b4", "#aec7e8"],
                ),
                legend=alt.Legend(title="Година"),
            ),
            xOffset="Година:N",
        )
        bars_stor_k = base_stor_k.mark_bar()

        # Поставување на првиот и третиот графикон еден до друг за да не бидат премногу широки
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.write("**1. Корупција: 2024 vs 2023 година (Кривични дела)**")
            st.altair_chart(
                bars_kd_k.properties(height=350), use_container_width=True
            )
        with col_k2:
            st.write("**2. Сторители: 2024 vs 2023 година**")
            st.altair_chart(
                bars_stor_k.properties(height=350), use_container_width=True
            )

        st.write("**3. Корупција - Промена % (Diverging Chart)**")
        base_div = alt.Chart(korupcija_clean).encode(
            x=alt.X(
                "СВР:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            )
        )
        color_enc_div = alt.Color(
            "Насока:N",
            scale=alt.Scale(domain=["Пораст", "Пад"], range=["#2ca02c", "#d62728"]),
            legend=alt.Legend(title=None),
        )
        rule_div = base_div.mark_rule(strokeWidth=2).encode(
            y=alt.Y(
                "Промена %:Q",
                axis=alt.Axis(format="%"),
                title="Промена",
                scale=alt.Scale(zero=True),
            ),
            y2="zero:Q",
            color=color_enc_div,
        )
        circle_div = base_div.mark_circle(size=200).encode(
            y="Промена %:Q", color=color_enc_div
        )
        text_div_pos = (
            base_div.transform_filter(alt.datum["Промена %"] >= 0)
            .mark_text(align="center", dy=-15, fontSize=10)
            .encode(y="Промена %:Q", text="Промена % текст:N")
        )
        text_div_neg = (
            base_div.transform_filter(alt.datum["Промена %"] < 0)
            .mark_text(align="center", dy=15, fontSize=10)
            .encode(y="Промена %:Q", text="Промена % текст:N")
        )
        st.altair_chart(
            (rule_div + circle_div + text_div_pos + text_div_neg).properties(
                height=350
            ),
            use_container_width=True,
        )

        st.subheader("📋 Детална табела")
        st.dataframe(raw_k, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Грешка при обработка на податоците за корупција: {e}")

# 3.5 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ОРГАНИЗИРАН КРИМИНАЛ
elif "Организиран" in selected_sheet:
    raw = df.copy()
    label_col = raw.columns[0]
    header_row_idx = None
    for i in range(min(5, len(raw))):
        row_vals = raw.iloc[i].astype(str)
        if row_vals.str.contains("2024", na=False).any() and row_vals.str.contains(
            "2023", na=False
        ).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        st.dataframe(df, use_container_width=True)
    else:
        header_row = raw.iloc[header_row_idx]
        year_cols = [
            col
            for col in raw.columns
            if str(header_row[col]).strip() in ["2024 година", "2023 година"]
        ]
        okg_2024_col, okg_2023_col = year_cols[0], year_cols[1]
        mem_2024_col, mem_2023_col = year_cols[2], year_cols[3]

        data_rows = raw.iloc[header_row_idx + 1 :].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[
            ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
        ]

        org_clean = pd.DataFrame({
            "Категорија": data_rows[label_col].values,
            "ОКГ 2024": pd.to_numeric(
                data_rows[okg_2024_col], errors="coerce"
            ).fillna(0),
            "ОКГ 2023": pd.to_numeric(
                data_rows[okg_2023_col], errors="coerce"
            ).fillna(0),
            "Членови 2024": pd.to_numeric(
                data_rows[mem_2024_col], errors="coerce"
            ).fillna(0),
            "Членови 2023": pd.to_numeric(
                data_rows[mem_2023_col], errors="coerce"
            ).fillna(0),
        }).dropna(subset=["Категорија"])

        cat_order = org_clean["Категорија"].tolist()
        col1, col2 = st.columns(2)
        with col1:
            st.write("**ОКГ: 2024 vs 2023 година**")
            melted_okg = (
                org_clean.rename(
                    columns={"ОКГ 2024": "2024 година", "ОКГ 2023": "2023 година"}
                )
                .melt(
                    id_vars=["Категорија"],
                    value_vars=["2024 година", "2023 година"],
                    var_name="Година",
                    value_name="Број",
                )
            )
            base_okg = alt.Chart(melted_okg).encode(
                y=alt.Y(
                    "Категорија:N",
                    sort=cat_order,
                    title=None,
                    axis=alt.Axis(labelLimit=280),
                ),
                x=alt.X("Број:Q", title="Број"),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                yOffset="Година:N",
            )
            bars_okg = base_okg.mark_bar()
            text_okg = base_okg.mark_text(align="left", dx=3).encode(text="Број:Q")
            st.altair_chart(
                (bars_okg + text_okg).properties(height=400),
                use_container_width=True,
            )

        with col2:
            st.write("**Членови на криминални групи: 2024 vs 2023 година**")
            melted_mem = (
                org_clean.rename(
                    columns={
                        "Членови 2024": "2024 година",
                        "Членови 2023": "2023 година",
                    }
                )
                .melt(
                    id_vars=["Категорија"],
                    value_vars=["2024 година", "2023 година"],
                    var_name="Година",
                    value_name="Број",
                )
            )
            base_mem = alt.Chart(melted_mem).encode(
                y=alt.Y(
                    "Категорија:N",
                    sort=cat_order,
                    title=None,
                    axis=alt.Axis(labelLimit=280),
                ),
                x=alt.X("Број:Q", title="Број", scale=alt.Scale(domain=[0, 80])),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#2ca02c", "#a8dba8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                yOffset="Година:N",
            )
            bars_mem = base_mem.mark_bar()
            text_mem = base_mem.mark_text(align="left", dx=3).encode(text="Број:Q")
            st.altair_chart(
                (bars_mem + text_mem).properties(height=400),
                use_container_width=True,
            )

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)

# 4. ГРАФИКОНИ ЗА ВКУПЕН КРИМИНАЛИТЕТ
elif "Вкупен" in selected_sheet:
    valid_rows = df[
        df.iloc[:, 0].astype(str).str.contains("СВР|ОСОСК", na=False)
    ].copy()
    sector_col = valid_rows.columns[0]
    for col in valid_rows.columns[1:]:
        valid_rows[col] = pd.to_numeric(valid_rows[col], errors="coerce")
    sector_order = valid_rows[sector_col].tolist()

    kd_col = valid_rows.columns[2]
    storiteli_col = valid_rows.columns[6]
    stapka_col = valid_rows.columns[7]
    efikasnost_col = valid_rows.columns[8]

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Вкупен криминалитет за 2024 година по СВР**")
        st.altair_chart(
            alt.Chart(valid_rows)
            .mark_bar(color=BLUE_COLOR)
            .encode(
                x=alt.X(
                    f"{sector_col}:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                ),
                y=alt.Y(f"{kd_col}:Q", title="Кривични дела"),
            )
            .properties(height=350),
            use_container_width=True,
        )
    with col2:
        st.write("**Сторители**")
        st.altair_chart(
            alt.Chart(valid_rows)
            .mark_bar(color=BLUE_COLOR)
            .encode(
                y=alt.Y(f"{sector_col}:N", sort=sector_order, title=None),
                x=alt.X(f"{storiteli_col}:Q", title="Сторители"),
            )
            .properties(height=350),
            use_container_width=True,
        )

    col3, col4 = st.columns(2)
    with col3:
        st.write("**Стапка на криминалитет**")
        base_stapka = alt.Chart(valid_rows).encode(
            x=alt.X(
                f"{sector_col}:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            ),
            y=alt.Y(f"{stapka_col}:Q", title="Стапка на криминал"),
        )
        line_stapka = base_stapka.mark_line(
            color=BLUE_COLOR, point=alt.OverlayMarkDef(color=BLUE_COLOR)
        )
        st.altair_chart(line_stapka.properties(height=350), use_container_width=True)
    with col4:
        st.write("**Вкупна ефикасност 2024 година**")
        st.altair_chart(
            alt.Chart(valid_rows)
            .mark_bar(color=BLUE_COLOR)
            .encode(
                y=alt.Y(f"{sector_col}:N", sort=sector_order, title=None),
                x=alt.X(f"{efikasnost_col}:Q", title="Ефикасност"),
            )
            .properties(height=350),
            use_container_width=True,
        )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4.5 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА УБИСТВА
elif "Убиства" in selected_sheet:
    raw = df.copy()
    label_col = raw.columns[0]
    header_row_idx = None
    for i in range(min(5, len(raw))):
        row_vals = raw.iloc[i].astype(str)
        if row_vals.str.contains("2024", na=False).any() and row_vals.str.contains(
            "2023", na=False
        ).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        st.dataframe(df, use_container_width=True)
    else:
        header_row = raw.iloc[header_row_idx]
        year_cols = [
            col
            for col in raw.columns
            if str(header_row[col]).strip() in ["2024 година", "2023 година"]
        ]
        col_2024, col_2023 = year_cols[0], year_cols[1]
        data_rows = raw.iloc[header_row_idx + 1 :].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[
            ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
        ]

        ubistva_clean = pd.DataFrame({
            "СВР": data_rows[label_col].values,
            "2024 година": pd.to_numeric(
                data_rows[col_2024], errors="coerce"
            ).fillna(0),
            "2023 година": pd.to_numeric(
                data_rows[col_2023], errors="coerce"
            ).fillna(0),
        }).dropna(subset=["СВР"])

        prev_year = ubistva_clean["2023 година"]
        curr_year = ubistva_clean["2024 година"]
        prev_year_safe = prev_year.replace(0, float("nan"))
        ubistva_clean["Промена"] = (
            (curr_year - prev_year) / prev_year_safe
        ).fillna(0)
        ubistva_clean["Промена текст"] = ubistva_clean["Промена"].apply(
            lambda x: f"{x*100:.1f}%"
        )
        ubistva_clean["Насока"] = ubistva_clean["Промена"].apply(
            lambda x: "Пораст" if x >= 0 else "Пад"
        )
        sector_order = ubistva_clean["СВР"].tolist()

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Убиства: 2024 vs 2023 година**")
            melted_u = ubistva_clean.melt(
                id_vars=["СВР"],
                value_vars=["2024 година", "2023 година"],
                var_name="Година",
                value_name="Број",
            )
            base_u = alt.Chart(melted_u).encode(
                x=alt.X(
                    "СВР:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                ),
                y=alt.Y(
                    "Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)
                ),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                xOffset="Година:N",
            )
            bars_u = base_u.mark_bar()
            text_u = base_u.mark_text(align="center", dy=-8).encode(text="Број:Q")
            st.altair_chart(
                (bars_u + text_u).properties(height=380), use_container_width=True
            )

        with col2:
            st.write("**Убиства - Промена (%) - Lollipop Chart**")
            ubistva_clean["zero"] = 0
            base_lolli = alt.Chart(ubistva_clean).encode(
                x=alt.X(
                    "СВР:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                )
            )
            color_enc_u = alt.Color(
                "Насока:N",
                scale=alt.Scale(domain=["Пораст", "Пад"], range=["#2ca02c", "#d62728"]),
                legend=alt.Legend(title=None),
            )
            rule_u = base_lolli.mark_rule(strokeWidth=2).encode(
                y=alt.Y(
                    "Промена:Q",
                    axis=alt.Axis(format="%"),
                    title="Промена",
                    scale=alt.Scale(zero=True),
                ),
                y2="zero:Q",
                color=color_enc_u,
            )
            circle_u = base_lolli.mark_circle(size=200).encode(
                y="Промена:Q", color=color_enc_u
            )
            text_u_pos = (
                base_lolli.transform_filter(alt.datum["Промена"] >= 0)
                .mark_text(align="center", dy=-16, fontSize=11)
                .encode(y="Промена:Q", text="Промена текст:N")
            )
            text_u_neg = (
                base_lolli.transform_filter(alt.datum["Промена"] < 0)
                .mark_text(align="center", dy=18, fontSize=11)
                .encode(y="Промена:Q", text="Промена текст:N")
            )
            st.altair_chart(
                (rule_u + circle_u + text_u_pos + text_u_neg).properties(
                    height=380
                ),
                use_container_width=True,
            )

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)

# 4.6 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ТЕШКИ КРАЖБИ
elif "Тешки кражби" in selected_sheet:
    raw = df.copy()
    label_col = raw.columns[0]
    header_row_idx = None
    for i in range(min(5, len(raw))):
        row_vals = raw.iloc[i].astype(str)
        if row_vals.str.contains("2024", na=False).any() and row_vals.str.contains(
            "2023", na=False
        ).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        st.dataframe(df, use_container_width=True)
    else:
        header_row = raw.iloc[header_row_idx]
        year_cols = [
            col
            for col in raw.columns
            if str(header_row[col]).strip() in ["2024 година", "2023 година"]
        ]
        col_2024, col_2023 = year_cols[0], year_cols[1] if len(year_cols) > 1 else year_cols[0]
        data_rows = raw.iloc[header_row_idx + 1 :].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[
            ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
        ]

        tk_clean = pd.DataFrame({
            "СВР": data_rows[label_col].values,
            "2024 година": pd.to_numeric(
                data_rows[col_2024], errors="coerce"
            ).fillna(0),
            "2023 година": pd.to_numeric(
                data_rows[col_2023], errors="coerce"
            ).fillna(0),
        }).dropna(subset=["СВР"])

        prev_year = tk_clean["2023 година"]
        curr_year = tk_clean["2024 година"]
        prev_year_safe = prev_year.replace(0, float("nan"))
        tk_clean["Промена"] = ((curr_year - prev_year) / prev_year_safe).fillna(0)
        tk_clean["Промена текст"] = tk_clean["Промена"].apply(
            lambda x: f"{x*100:.1f}%"
        )
        tk_clean["Насока"] = tk_clean["Промена"].apply(
            lambda x: "Пораст" if x >= 0 else "Пад"
        )
        sector_order = tk_clean["СВР"].tolist()

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Тешки кражби: 2024 vs 2023 година**")
            melted_tk = tk_clean.melt(
                id_vars=["СВР"],
                value_vars=["2024 година", "2023 година"],
                var_name="Година",
                value_name="Број",
            )
            base_tk = alt.Chart(melted_tk).encode(
                x=alt.X(
                    "СВР:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                ),
                y=alt.Y(
                    "Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)
                ),
                color=alt.Color(
                    "Година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="Година"),
                ),
                xOffset="Година:N",
            )
            bars_tk = base_tk.mark_bar()
            st.altair_chart(
                bars_tk.properties(height=380), use_container_width=True
            )

        with col2:
            st.write("**Тешки кражби - Промена (%)**")
            tk_clean["zero"] = 0
            base_tk_div = alt.Chart(tk_clean).encode(
                x=alt.X(
                    "СВР:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                )
            )
            color_enc_tk = alt.Color(
                "Насока:N",
                scale=alt.Scale(domain=["Пораст", "Пад"], range=["#2ca02c", "#d62728"]),
                legend=alt.Legend(title=None),
            )
            rule_tk = base_tk_div.mark_rule(strokeWidth=2).encode(
                y=alt.Y(
                    "Промена:Q",
                    axis=alt.Axis(format="%"),
                    title="Промена",
                    scale=alt.Scale(zero=True),
                ),
                y2="zero:Q",
                color=color_enc_tk,
            )
            circle_tk = base_tk_div.mark_circle(size=200).encode(
                y="Промена:Q", color=color_enc_tk
            )
            text_tk_pos = (
                base_tk_div.transform_filter(alt.datum["Промена"] >= 0)
                .mark_text(align="center", dy=-15, fontSize=10)
                .encode(y="Промена:Q", text="Промена текст:N")
            )
            text_tk_bd = (
                base_tk_div.transform_filter(alt.datum["Промена"] < 0)
                .mark_text(align="center", dy=15, fontSize=10)
                .encode(y="Промена:Q", text="Промена текст:N")
            )
            st.altair_chart(
                (rule_tk + circle_tk + text_tk_pos + text_tk_bd).properties(
                    height=380
                ),
                use_container_width=True,
            )

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)

# 4.7 УНИВЕРЗАЛЕН ИНТЕЛИГЕНТЕН ПРИКАЗ ЗА ОСТАНАТИ ЛИСТОВИ И ХЕДЕРИ
else:
    raw = df.copy()
    label_col = raw.columns[0]
    header_row_idx = None
    for i in range(min(5, len(raw))):
        row_vals = raw.iloc[i].astype(str)
        if row_vals.str.contains("2024", na=False).any() and row_vals.str.contains(
            "2023", na=False
        ).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        st.write("**Детална табела за селектираниот лист:**")
        st.dataframe(df, use_container_width=True)
    else:
        header_row = raw.iloc[header_row_idx]
        year_cols = [
            col
            for col in raw.columns
            if str(header_row[col]).strip() in ["2024 година", "2023 година"]
        ]
        
        if len(year_cols) >= 2:
            col_2024, col_2023 = year_cols[0], year_cols[1]
        elif len(year_cols) == 1:
            col_2024, col_2023 = year_cols[0], year_cols[0]
        else:
            col_2024, col_2023 = raw.columns[3] if len(raw.columns) > 3 else raw.columns[0], raw.columns[5] if len(raw.columns) > 5 else raw.columns[0]

        data_rows = raw.iloc[header_row_idx + 1 :].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[
            ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
        ]

        generic_clean = pd.DataFrame({
            "СВР": data_rows[label_col].values,
            "2024 година": pd.to_numeric(
                data_rows[col_2024], errors="coerce"
            ).fillna(0),
            "2023 година": pd.to_numeric(
                data_rows[col_2023], errors="coerce"
            ).fillna(0),
        }).dropna(subset=["СВР"])

        generic_clean = generic_clean[
            generic_clean["СВР"].astype(str).str.contains("СВР|ОСОСК", na=False)
        ]

        if not generic_clean.empty:
            prev_year = generic_clean["2023 година"]
            curr_year = generic_clean["2024 година"]
            prev_year_safe = prev_year.replace(0, float("nan"))
            generic_clean["Промена"] = ((curr_year - prev_year) / prev_year_safe).fillna(0)
            generic_clean["Промена текст"] = generic_clean["Промена"].apply(
                lambda x: f"{x*100:.1f}%"
            )
            generic_clean["Насока"] = generic_clean["Промена"].apply(
                lambda x: "Пораст" if x >= 0 else "Пад"
            )
            sector_order = generic_clean["СВР"].tolist()

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{selected_sheet}: 2024 vs 2023 година**")
                melted_gen = generic_clean.melt(
                    id_vars=["СВР"],
                    value_vars=["2024 година", "2023 година"],
                    var_name="Година",
                    value_name="Број",
                )
                base_gen = alt.Chart(melted_gen).encode(
                    x=alt.X(
                        "СВР:N",
                        title=None,
                        sort=sector_order,
                        axis=alt.Axis(labelAngle=270),
                    ),
                    y=alt.Y(
                        "Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)
                    ),
                    color=alt.Color(
                        "Година:N",
                        scale=alt.Scale(
                            domain=["2024 година", "2023 година"],
                            range=["#1f77b4", "#aec7e8"],
                        ),
                        legend=alt.Legend(title="Година"),
                    ),
                    xOffset="Година:N",
                )
                bars_gen = base_gen.mark_bar()
                st.altair_chart(
                    bars_gen.properties(height=380), use_container_width=True
                )

            with col2:
                st.write(f"**{selected_sheet} - Промена (%)**")
                generic_clean["zero"] = 0
                base_gen_div = alt.Chart(generic_clean).encode(
                    x=alt.X(
                        "СВР:N",
                        title=None,
                        sort=sector_order,
                        axis=alt.Axis(labelAngle=270),
                    )
                )
                color_enc_gen = alt.Color(
                    "Насока:N",
                    scale=alt.Scale(domain=["Пораст", "Пад"], range=["#2ca02c", "#d62728"]),
                    legend=alt.Legend(title=None),
                )
                rule_gen = base_gen_div.mark_rule(strokeWidth=2).encode(
                    y=alt.Y(
                        "Промена:Q",
                        axis=alt.Axis(format="%"),
                        title="Промена",
                        scale=alt.Scale(zero=True),
                    ),
                    y2="zero:Q",
                    color=color_enc_gen,
                )
                circle_gen = base_gen_div.mark_circle(size=200).encode(
                    y="Промена:Q", color=color_enc_gen
                )
                text_gen_pos = (
                    base_gen_div.transform_filter(alt.datum["Промена"] >= 0)
                    .mark_text(align="center", dy=-15, fontSize=10)
                    .encode(y="Промена:Q", text="Промена текст:N")
                )
                text_gen_neg = (
                    base_gen_div.transform_filter(alt.datum["Промена"] < 0)
                    .mark_text(align="center", dy=15, fontSize=10)
                    .encode(y="Промена:Q", text="Промена текст:N")
                )
                st.altair_chart(
                    (rule_gen + circle_gen + text_gen_pos + text_gen_neg).properties(
                        height=380
                    ),
                    use_container_width=True,
                )

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)
