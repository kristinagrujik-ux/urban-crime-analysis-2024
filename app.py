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
st.title(f"📁 {selected_sheet}")


@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)


df = load_data(selected_sheet)
BLUE_COLOR = "#1f77b4"

# 1. ВКУПЕН КРИМИНАЛ: Анализа на кривични дела против јавниот ред и мир
if "Вкупен криминалитет" in selected_sheet:
    table_data = [
        {
            "кривичен дел": "Консумирање дрога и овозможување",
            "2024 година": 10,
            "2023 година": 2,
            "промена %": 4.0,
            "промена износ": "Тоа беше !",
        },
        {
            "кривичен дел": "Олакшување на употреба дрога и овозмож",
            "2024 година": 2,
            "2023 година": 0,
            "промена %": 2.0,
            "промена износ": "200%",
        },
        {
            "кривичен дел": "Неовластено производство и пуштање во промет наркотик",
            "2024 година": 2,
            "2023 година": 0,
            "промена %": 2.0,
            "промена износ": "200%",
        },
        {
            "кривичен дел": "Недозвола на неовластено производство",
            "2024 година": 0,
            "2023 година": 1,
            "промена %": 0.0,
            "промена износ": "0",
        },
        {
            "кривичен дел": "Опште и јавна опасниост",
            "2024 година": 1,
            "2023 година": 1,
            "промена %": 0.0,
            "промена износ": "0",
        },
        {
            "кривичен дел": "Вкупно кривични дела",
            "2024 година": 15,
            "2023 година": 4,
            "промена %": 2.75,
            "промена износ": "Тоа е тоа беше !",
        },
    ]
    df_display = pd.DataFrame(table_data)

    chart_data = df_display[
        df_display["кривичен дел"] != "Вкупно кривични дела"
    ].copy()
    chart_data["2024 година"] = pd.to_numeric(
        chart_data["2024 година"], errors="coerce"
    ).fillna(0)
    chart_data["2023 година"] = pd.to_numeric(
        chart_data["2023 година"], errors="coerce"
    ).fillna(0)
    chart_data = chart_data.rename(columns={"промена %": "promena_procent"})
    cat_order_kd = chart_data["кривичен дел"].tolist()

    melted_kd = chart_data.melt(
        id_vars=["кривичен дел"],
        value_vars=["2024 година", "2023 година"],
        var_name="Година",
        value_name="Вредност",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Споредба по кривичен дел (2024 vs 2023)**")
        base_kd_state = alt.Chart(melted_kd).encode(
            y=alt.Y(
                "кривичен дел:N",
                sort=cat_order_kd,
                title=None,
                axis=alt.Axis(labelLimit=320),
            ),
            x=alt.X(
                "Вредност:Q",
                title="Вредност",
                axis=alt.Axis(format="d", tickMinStep=1),
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
        ).encode(text="Вредност:Q")
        st.altair_chart(
            (bars_kd_state + text_kd_state).properties(height=350),
            use_container_width=True,
        )

    with col2:
        st.write("**Промена (%) - Хоризонтален Column Chart**")
        base_horiz = alt.Chart(chart_data).encode(
            y=alt.Y(
                "кривичен дел:N",
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
        ).encode(text="промена износ:N")
        chart_horizontal = (
            (bars_horiz + text_horiz)
            .properties(height=350)
            .configure_axis(gridColor="white", gridOpacity=0.8)
            .configure_view(fill="#eef0f2", stroke=None)
        )
        st.altair_chart(chart_horizontal, use_container_width=True)

    st.subheader("📋 Детална табела")
    df_table_show = df_display.copy()
    df_table_show["промена %"] = [
        "Тоа беше !",
        "200%",
        "200%",
        "0",
        "0",
        "Тоа е тоа беше !",
    ]
    df_table_show = df_table_show.drop(columns=["промена износ"])
    st.dataframe(df_table_show, use_container_width=True, hide_index=True)

# 2. МИГРАНТИ / КРИУМЧАРЕЊЕ НА МИГРАНТИ
elif "Криумчарење на мигранти" in selected_sheet:
    mig_df = df.iloc[:4, :].copy()
    cat_col = mig_df.columns[0]
    col_2024 = next(c for c in mig_df.columns if "2024" in str(c))
    col_2023 = next(c for c in mig_df.columns if "2023" in str(c))
    col_change = next(c for c in mig_df.columns if "промена" in str(c))

    mig_clean = pd.DataFrame({
        "Категорија": mig_df[cat_col].values,
        "2024 година": pd.to_numeric(mig_df[col_2024], errors="coerce"),
        "2023 година": pd.to_numeric(mig_df[col_2023], errors="coerce"),
        "Промена": pd.to_numeric(mig_df[col_change], errors="coerce"),
    })
    mig_clean["Промена износ"] = mig_clean["Промена"].apply(
        lambda x: f"{x*100:.1f}%"
        if pd.notnull(x) and isinstance(x, (int, float))
        else str(x)
    )

    col1, col2 = st.columns(2)
    cat_order = mig_clean["Категорија"].tolist()

    with col1:
        st.write("**Споредба по мигранти: 2024 vs 2023**")
        melted_mig = mig_clean.melt(
            id_vars=["Категорија"],
            value_vars=["2024 година", "2023 година"],
            var_name="Година",
            value_name="Вредност",
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
                y=alt.Y("Вредност:Q", title="Вредност"),
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
        st.write("**Промена (%) според категории**")
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
            x="Промена:Q", text="Промена износ:N"
        )
        st.altair_chart(
            (bar_change + text_change).properties(
                height=380, padding={"left": 20, "top": 5, "right": 20, "bottom": 5}
            ),
            use_container_width=True,
        )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 3. ОРГАНИЗИРАН КРИМИНАЛ
elif "Организиран криминал" in selected_sheet:

    @st.cache_data
    def load_org_krim(sheet):
        return pd.read_excel(file_path, sheet_name=sheet, header=3)

    try:
        raw_org = load_org_krim(selected_sheet)
        org_clean = raw_org.iloc[:7, :5].copy()
        org_clean.columns = [
            "Област",
            "2024_дела",
            "2023_дела",
            "2024_членови",
            "2023_членови",
        ]
        org_clean = org_clean.dropna(subset=["Област"])

        for col in [
            "2024_дела",
            "2023_дела",
            "2024_членови",
            "2023_членови",
        ]:
            org_clean[col] = pd.to_numeric(
                org_clean[col].astype(str).str.replace("-", "0"),
                errors="coerce",
            ).fillna(0)

        sector_order_org = org_clean["Област"].tolist()

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Организиран криминал - Дела (2024 vs 2023)**")
            melted_org_d = org_clean.melt(
                id_vars=["Област"],
                value_vars=["2024_дела", "2023_дела"],
                var_name="Година",
                value_name="Вредност",
            )
            melted_org_d["Година"] = melted_org_d["Година"].replace(
                {"2024_дела": "2024 година", "2023_дела": "2023 година"}
            )
            chart_org_d = (
                alt.Chart(melted_org_d)
                .mark_bar()
                .encode(
                    y=alt.Y(
                        "Област:N",
                        sort=sector_order_org,
                        title=None,
                        axis=alt.Axis(labelLimit=300),
                    ),
                    x=alt.X(
                        "Вредност:Q",
                        title="Број на дела",
                        axis=alt.Axis(format="d", tickMinStep=1),
                    ),
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
                .properties(height=380)
            )
            st.altair_chart(chart_org_d, use_container_width=True)

        with col2:
            st.write(
                "**Организиран криминал - Членови на криминални групи (2024 vs 2023)**"
            )
            melted_org_c = org_clean.melt(
                id_vars=["Област"],
                value_vars=["2024_членови", "2023_членови"],
                var_name="Година",
                value_name="Вредност",
            )
            melted_org_c["Година"] = melted_org_c["Година"].replace(
                {
                    "2024_членови": "2024 година",
                    "2023_членови": "2023 година",
                }
            )
            chart_org_c = (
                alt.Chart(melted_org_c)
                .mark_bar()
                .encode(
                    y=alt.Y(
                        "Област:N",
                        sort=sector_order_org,
                        title=None,
                        axis=alt.Axis(labelLimit=300),
                    ),
                    x=alt.X(
                        "Вредност:Q",
                        title="Број на членови",
                        axis=alt.Axis(format="d", tickMinStep=1),
                    ),
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
                .properties(height=380)
            )
            st.altair_chart(chart_org_c, use_container_width=True)

        st.subheader("📋 Детална табела")
        st.dataframe(raw_org, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Грешка при вчитување на податоците за организиран криминал: {e}")

# 4. Останати листови / Генерички прикази
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
        st.write(f"**Општи податоци за {selected_sheet}:**")
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
            col_2024, col_2023 = (
                raw.columns[3] if len(raw.columns) > 3 else raw.columns[0],
                raw.columns[5] if len(raw.columns) > 5 else raw.columns[0],
            )

        data_rows = raw.iloc[header_row_idx + 1 :].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[
            ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
        ]

        generic_clean = pd.DataFrame({
            "Име": data_rows[label_col].values,
            "2024 година": pd.to_numeric(
                data_rows[col_2024], errors="coerce"
            ).fillna(0),
            "2023 година": pd.to_numeric(
                data_rows[col_2023], errors="coerce"
            ).fillna(0),
        }).dropna(subset=["Име"])

        if not generic_clean.empty:
            prev_year = generic_clean["2023 година"]
            curr_year = generic_clean["2024 година"]
            prev_year_safe = prev_year.replace(0, float("nan"))
            generic_clean["промена"] = (
                (curr_year - prev_year) / prev_year_safe
            ).fillna(0)
            generic_clean["промена износ"] = generic_clean["промена"].apply(
                lambda x: f"{x*100:.1f}%"
            )
            sector_order = generic_clean["Име"].tolist()

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{selected_sheet}: 2024 vs 2023 година**")
                melted_gen = generic_clean.melt(
                    id_vars=["Име"],
                    value_vars=["2024 година", "2023 година"],
                    var_name="Година",
                    value_name="Вредност",
                )
                base_gen = alt.Chart(melted_gen).encode(
                    x=alt.X(
                        "Име:N",
                        title=None,
                        sort=sector_order,
                        axis=alt.Axis(labelAngle=270),
                    ),
                    y=alt.Y(
                        "Вредност:Q",
                        title="Вредност",
                        axis=alt.Axis(format="d", tickMinStep=1),
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
                        "Име:N",
                        title=None,
                        sort=sector_order,
                        axis=alt.Axis(labelAngle=270),
                    )
                )
                color_enc_gen = alt.Color(
                    "промена:Q",
                    scale=alt.Scale(domain=[0, 0.00001], range=["#d62728", "#2ca02c"]),
                    legend=None,
                )
                rule_gen = base_gen_div.mark_rule(strokeWidth=2).encode(
                    y=alt.Y(
                        "промена:Q",
                        axis=alt.Axis(format="%"),
                        title="Промена",
                        scale=alt.Scale(zero=True),
                    ),
                    y2="zero:Q",
                    color=alt.Color(
                        "промена:Q",
                        scale=alt.Scale(domain=[0, 0.01], range=["#d62728", "#2ca02c"]),
                        legend=None,
                    ),
                )
                circle_gen = base_gen_div.mark_circle(size=200).encode(
                    y="промена:Q", color=color_enc_gen
                )
                text_gen_pos = (
                    base_gen_div.transform_filter(alt.datum["промена"] >= 0)
                    .mark_text(align="center", dy=-15, fontSize=10)
                    .encode(y="промена:Q", text="промена износ:N")
                )
                text_gen_neg = (
                    base_gen_div.transform_filter(alt.datum["промена"] < 0)
                    .mark_text(align="center", dy=15, fontSize=10)
                    .encode(y="промена:Q", text="промена износ:N")
                )
                st.altair_chart(
                    (rule_gen + circle_gen + text_gen_pos + text_gen_neg).properties(
                        height=380
                    ),
                    use_container_width=True,
                )

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)



