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


selected_sheet = st.sidebar.selectbox("Изберете категорија:", get_sheets())
st.title(f"📊 {selected_sheet}")


@st.cache_data
def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet)


df = load_data(selected_sheet)
BLUE_COLOR = "#1f77b4"

# 1. Општ преглед: Увид во податоци пред секое бришење
if "општ уред во податоци пред секое бришење" in selected_sheet:
    table_data = [
        {
            "кривично дело": "неовластено производство и пуштање",
            "2024 година": 10,
            "2023 година": 2,
            "промена %": 4.0,
            "промена опис": "раст од 4 пати",
        },
        {
            "кривично дело": "овозможување на употреба наркотици и психотропни",
            "2024 година": 2,
            "2023 година": 0,
            "промена %": 2.0,
            "промена опис": "200%",
        },
        {
            "кривично дело": "неовластено производство и промет на оружје или експлозивни материи",
            "2024 година": 2,
            "2023 година": 0,
            "промена %": 2.0,
            "промена опис": "200%",
        },
        {
            "кривично дело": "грабеж на финансиски институции",
            "2024 година": 0,
            "2023 година": 1,
            "промена %": 0.0,
            "промена опис": "0",
        },
        {
            "кривично дело": "кражба и тешка кражба",
            "2024 година": 1,
            "2023 година": 1,
            "промена %": 0.0,
            "промена опис": "0",
        },
        {
            "кривично дело": "вкупно кривични дела",
            "2024 година": 15,
            "2023 година": 4,
            "промена %": 2.75,
            "промена опис": "раст од речиси 3 пати",
        },
    ]
    df_display = pd.DataFrame(table_data)

    chart_data = df_display[
        df_display["кривично дело"] != "вкупно кривични дела"
    ].copy()
    chart_data["2024 година"] = pd.to_numeric(
        chart_data["2024 година"], errors="coerce"
    ).fillna(0)
    chart_data["2023 година"] = pd.to_numeric(
        chart_data["2023 година"], errors="coerce"
    ).fillna(0)
    chart_data = chart_data.rename(columns={"промена %": "promena_procent"})
    cat_order_kd = chart_data["кривично дело"].tolist()

    melted_kd = chart_data.melt(
        id_vars=["кривично дело"],
        value_vars=["2024 година", "2023 година"],
        var_name="година",
        value_name="збир",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Споредба по кривично дело (2024 vs 2023)**")
        base_kd_state = alt.Chart(melted_kd).encode(
            y=alt.Y(
                "кривично дело:N",
                sort=cat_order_kd,
                title=None,
                axis=alt.Axis(labelLimit=320),
            ),
            x=alt.X(
                "збир:Q", title="збир", axis=alt.Axis(format="d", tickMinStep=1)
            ),
            color=alt.Color(
                "година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#228B22", "#50C878"],
                ),
                legend=alt.Legend(title="година"),
            ),
            yOffset="година:N",
        )
        bars_kd_state = base_kd_state.mark_bar()
        text_kd_state = base_kd_state.mark_text(
            align="left", dx=3, baseline="middle"
        ).encode(text="збир:Q")
        st.altair_chart(
            (bars_kd_state + text_kd_state).properties(height=350),
            use_container_width=True,
        )

    with col2:
        st.write("**Промена (%) - Хоризонтален Column Chart**")
        base_horiz = alt.Chart(chart_data).encode(
            y=alt.Y(
                "кривично дело:N",
                sort=cat_order_kd,
                title=None,
                axis=alt.Axis(labelLimit=320, labelFontSize=11),
            ),
            x=alt.X(
                "promena_procent:Q",
                title="промена (%)",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domain=[-0.2, 8.0], zero=True),
            ),
        )
        bars_horiz = base_horiz.mark_bar(color=BLUE_COLOR)
        text_horiz = base_horiz.mark_text(
            align="left", baseline="middle", dx=5, fontSize=11, fontWeight="bold"
        ).encode(text="промена опис:N")
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
        "раст од 4 пати",
        "200%",
        "200%",
        "0",
        "0",
        "раст од речиси 3 пати",
    ]
    df_table_show = df_table_show.drop(columns=["промена опис"])
    st.dataframe(df_table_show, use_container_width=True, hide_index=True)

# 2. Аналитички приказ за миграцијата на криминалот
elif "миграција на криминалот" in selected_sheet:
    mig_df = df.iloc[:4, :].copy()
    cat_col = mig_df.columns[0]
    col_2024 = next(c for c in mig_df.columns if "2024" in str(c))
    col_2023 = next(c for c in mig_df.columns if "2023" in str(c))
    col_change = next(c for c in mig_df.columns if "промена" in str(c))

    mig_clean = pd.DataFrame({
        "категорија": mig_df[cat_col].values,
        "2024 година": pd.to_numeric(mig_df[col_2024], errors="coerce"),
        "2023 година": pd.to_numeric(mig_df[col_2023], errors="coerce"),
        "промена": pd.to_numeric(mig_df[col_change], errors="coerce"),
    })
    mig_clean["промена опис"] = mig_clean["промена"].apply(
        lambda x: f"{x*100:.1f}%"
        if pd.notnull(x) and isinstance(x, (int, float))
        else str(x)
    )

    col1, col2 = st.columns(2)
    cat_order = mig_clean["категорија"].tolist()

    with col1:
        st.write("**Споредба по миграција: 2024 vs 2023**")
        melted_mig = mig_clean.melt(
            id_vars=["категорија"],
            value_vars=["2024 година", "2023 година"],
            var_name="година",
            value_name="збир",
        )
        chart_col = (
            alt.Chart(melted_mig)
            .mark_bar()
            .encode(
                x=alt.X(
                    "категорија:N",
                    title=None,
                    sort=cat_order,
                    axis=alt.Axis(labelAngle=270, labelLimit=200),
                ),
                y=alt.Y("збир:Q", title="збир"),
                color=alt.Color(
                    "година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="година"),
                ),
                xOffset="година:N",
            )
        )
        st.altair_chart(chart_col.properties(height=380), use_container_width=True)

    with col2:
        st.write("**Промена (%) според категорија**")
        cat_order_reversed = cat_order[::-1]
        bar_change = alt.Chart(mig_clean).mark_bar(color=BLUE_COLOR).encode(
            y=alt.Y(
                "категорија:N",
                sort=cat_order_reversed,
                title=None,
                axis=alt.Axis(labelLimit=280, labelFontSize=11, labelPadding=10),
            ),
            x=alt.X(
                "промена:Q",
                axis=alt.Axis(format="%", values=[-0.8, -0.6, -0.4, -0.2, 0]),
                title="промена",
                scale=alt.Scale(domain=[-0.75, 0.05], zero=False),
            ),
        )
        text_change = bar_change.mark_text(align="left", dx=5).encode(
            x="промена:Q", text="промена опис:N"
        )
        st.altair_chart(
            (bar_change + text_change).properties(
                height=380, padding={"left": 20, "top": 5, "right": 20, "bottom": 5}
            ),
            use_container_width=True,
        )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# НАВЕДЕН ДЕЛ: ТРГОВИЈА СО ЛУЃЕ (НОВ ДОДАДЕН ИНПУТ)
elif "трговија со луѓе" in selected_sheet.lower():
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
        col_2024 = year_cols[0] if len(year_cols) > 0 else raw.columns[3]
        col_2023 = (
            year_cols[1]
            if len(year_cols) > 1
            else (year_cols[0] if len(year_cols) > 0 else raw.columns[5])
        )

        data_rows = raw.iloc[header_row_idx + 1 :].copy()
        data_rows = data_rows[data_rows[label_col].notna()]
        data_rows = data_rows[
            ~data_rows[label_col].astype(str).str.contains("вкупно", na=False)
        ]

        tr_clean = pd.DataFrame({
            "име": data_rows[label_col].values,
            "2024 година": pd.to_numeric(
                data_rows[col_2024], errors="coerce"
            ).fillna(0),
            "2023 година": pd.to_numeric(
                data_rows[col_2023], errors="coerce"
            ).fillna(0),
        }).dropna(subset=["име"])

        prev_year = tr_clean["2023 година"]
        curr_year = tr_clean["2024 година"]
        prev_year_safe = prev_year.replace(0, float("nan"))
        tr_clean["промена"] = ((curr_year - prev_year) / prev_year_safe).fillna(
            0
        )
        tr_clean["промена опис"] = tr_clean["промена"].apply(
            lambda x: f"{x*100:.1f}%"
        )
        tr_clean["тренд"] = tr_clean["промена"].apply(
            lambda x: "пораст" if x >= 0 else "пад"
        )
        sector_order = tr_clean["име"].tolist()

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Трговија со луѓе: 2024 vs 2023 година**")
            melted_tr = tr_clean.melt(
                id_vars=["име"],
                value_vars=["2024 година", "2023 година"],
                var_name="година",
                value_name="збир",
            )
            base_tr = alt.Chart(melted_tr).encode(
                x=alt.X(
                    "име:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                ),
                y=alt.Y(
                    "збир:Q", title="збир", axis=alt.Axis(format="d", tickMinStep=1)
                ),
                color=alt.Color(
                    "година:N",
                    scale=alt.Scale(
                        domain=["2024 година", "2023 година"],
                        range=["#1f77b4", "#aec7e8"],
                    ),
                    legend=alt.Legend(title="година"),
                ),
                xOffset="година:N",
            )
            bars_tr = base_tr.mark_bar()
            st.altair_chart(
                bars_tr.properties(height=380), use_container_width=True
            )

        with col2:
            st.write("**Трговија со луѓе - Промена (%)**")
            tr_clean["zero"] = 0
            base_tr_div = alt.Chart(tr_clean).encode(
                x=alt.X(
                    "име:N",
                    title=None,
                    sort=sector_order,
                    axis=alt.Axis(labelAngle=270),
                )
            )
            color_enc_tr = alt.Color(
                "тренд:N",
                scale=alt.Scale(domain=["пораст", "пад"], range=["#2ca02c", "#d62728"]),
                legend=alt.Legend(title=None),
            )
            rule_tr = base_tr_div.mark_rule(strokeWidth=2).encode(
                y=alt.Y(
                    "промена:Q",
                    axis=alt.Axis(format="%"),
                    title="промена",
                    scale=alt.Scale(zero=True),
                ),
                y2="zero:Q",
                color=color_enc_tr,
            )
            circle_tr = base_tr_div.mark_circle(size=200).encode(
                y="промена:Q", color=color_enc_tr
            )
            text_tr_pos = (
                base_tr_div.transform_filter(alt.datum["промена"] >= 0)
                .mark_text(align="center", dy=-15, fontSize=10)
                .encode(y="промена:Q", text="промена опис:N")
            )
            text_tr_neg = (
                base_tr_div.transform_filter(alt.datum["промена"] < 0)
                .mark_text(align="center", dy=15, fontSize=10)
                .encode(y="промена:Q", text="промена опис:N")
            )
            st.altair_chart(
                (rule_tr + circle_tr + text_tr_pos + text_tr_neg).properties(
                    height=380
                ),
                use_container_width=True,
            )

        st.subheader("📋 Детална табела")
        st.dataframe(df, use_container_width=True)

# 3. Останати делови од вашата апликација (пример: корупција, убиства, итн.)
else:
    st.write(f"**Приказ за листот: {selected_sheet}**")
    st.dataframe(df, use_container_width=True)
