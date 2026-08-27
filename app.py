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
          "Промена %": "пет пати ↗",
      },
      {
          "Кривични дела": "Учество во странска војска и полиција",
          "2024 година": 2,
          "2023 година": "-",
          "Промена %": "200% ↗",
      },
      {
          "Кривични дела": "Неовластено навлегување и цртање на воени објекти",
          "2024 година": 2,
          "2023 година": "-",
          "Промена %": "200% ↗",
      },
      {
          "Кривични дела": "Служба во непријателска војска",
          "2024 година": "-",
          "2023 година": 1,
          "Промена %": "-",
      },
      {
          "Кривични дела": "Расна и друга дискриминација",
          "2024 година": 1,
          "2023 година": 1,
          "Промена %": "-",
      },
      {
          "Кривични дела": "Вкупно кривични дела",
          "2024 година": 15,
          "2023 година": 4,
          "Промена %": "три и пол пати ↗",
      },
  ]
  df_display = pd.DataFrame(table_data)

  st.write("**Кривични дела: 2024 vs 2023 година**")
  chart_data = df_display[
      df_display["Кривични дела"] != "Вкупно кривични дела"
  ].copy()
  chart_data["2024 година"] = pd.to_numeric(
      chart_data["2024 година"], errors="coerce"
  ).fillna(0)
  chart_data["2023 година"] = pd.to_numeric(
      chart_data["2023 година"], errors="coerce"
  ).fillna(0)
  cat_order_kd = chart_data["Кривични дела"].tolist()
  melted_kd = chart_data.melt(
      id_vars=["Кривични дела"],
      value_vars=["2024 година", "2023 година"],
      var_name="Година",
      value_name="Број",
  )
  base_kd_state = alt.Chart(melted_kd).encode(
      y=alt.Y(
          "Кривични дела:N",
          sort=cat_order_kd,
          title=None,
          axis=alt.Axis(labelLimit=320),
      ),
      x=alt.X("Број:Q", title="Број", axis=alt.Axis(format="d", tickMinStep=1)),
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

  st.subheader("📋 Детална табела")
  st.dataframe(df_display, use_container_width=True, hide_index=True)

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
        x=alt.X("Промена:Q", axis=alt.Axis(format="%"), title="Промена"),
    )
    text_change = bar_change.mark_text(align="left", dx=3).encode(
        text="Промена текст:N"
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

  valid_rows["Промена КД % текст"] = valid_rows["Промена КД %"].apply(
      lambda x: f"{x*100:.1f}%"
      if pd.notnull(x) and isinstance(x, (int, float))
      else str(x)
  )
  valid_rows["Промена Сторители % текст"] = valid_rows[
      "Промена Сторители %"
  ].apply(
      lambda x: f"{x*100:.1f}%"
      if pd.notnull(x) and isinstance(x, (int, float))
      else str(x)
  )
  valid_rows["zero"] = 0
  sector_order = valid_rows[sector_col].tolist()

  col1, col2 = st.columns(2)
  with col1:
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
            y=alt.Y(f"{sector_col}:N", sort=sector_order),
            x="Број:Q",
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
  with col2:
    st.write("**Недозволена трговија со дрога - Промена на кривични дела (%)**")
    base_kd = alt.Chart(valid_rows).encode(
        x=alt.X(
            f"{sector_col}:N",
            title=None,
            sort=sector_order,
            axis=alt.Axis(labelAngle=270),
        )
    )
    rule_kd = base_kd.mark_rule(color=BLUE_COLOR, strokeWidth=2).encode(
        y=alt.Y(
            "Промена КД %:Q", axis=alt.Axis(format="%"), title="Промена"
        ),
        y2="zero:Q",
    )
    circle_kd = base_kd.mark_circle(size=220, color=BLUE_COLOR).encode(
        y="Промена КД %:Q"
    )
    text_kd_change = base_kd.mark_text(
        align="center", dy=-16, fontSize=11
    ).encode(y="Промена КД %:Q", text="Промена КД % текст:N")
    st.altair_chart(
        (rule_kd + circle_kd + text_kd_change).properties(height=350),
        use_container_width=True,
    )

  col3, col4 = st.columns(2)
  with col3:
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
            y=alt.Y(f"{sector_col}:N", sort=sector_order),
            x="Број:Q",
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
  with col4:
    st.write("**Недозволена трговија со дрога - Промена на сторители (%)**")
    base_stor = alt.Chart(valid_rows).encode(
        x=alt.X(
            f"{sector_col}:N",
            title=None,
            sort=sector_order,
            axis=alt.Axis(labelAngle=270),
        )
    )
    rule_stor = base_stor.mark_rule(color="#d62728", strokeWidth=2).encode(
        y=alt.Y(
            "Промена Сторители %:Q", axis=alt.Axis(format="%"), title="Промена"
        ),
        y2="zero:Q",
    )
    circle_stor = base_stor.mark_circle(size=220, color="#d62728").encode(
        y="Промена Сторители %:Q"
    )
    text_stor_change = base_stor.mark_text(
        align="center", dy=-16, fontSize=11
    ).encode(y="Промена Сторители %:Q", text="Промена Сторители % текст:N")
    st.altair_chart(
        (rule_stor + circle_stor + text_stor_change).properties(height=350),
        use_container_width=True,
    )

  st.subheader("📋 Детална табела")
  st.dataframe(df, use_container_width=True)

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
    st.error("Не можат да се пронајдат заглавијата за оваа табела.")
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
    st.error("Не можат да се пронајдат заглавијата за оваа табела.")
    st.dataframe(df, use_container_width=True)
  else:
    header_row = raw.iloc[header_row_idx]
    year_cols = [
        col
        for col in raw.columns
        if str(header_row[col]).strip() in ["2024 година", "2023 година"]
    ]
    col_2024, col_2023 = year_cols[0], year_cols[1]
    promena_col = next(
        (
            col
            for col in raw.columns
            if "Промена" in str(header_row[col])
        ),
        None,
    )

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

    if promena_col is not None:
      promena_raw = pd.to_numeric(data_rows[promena_col], errors="coerce")
      ubistva_clean["Промена"] = promena_raw.values
    else:
      ubistva_clean["Промена"] = float("nan")

    prev_year = ubistva_clean["2023 година"]
    curr_year = ubistva_clean["2024 година"]
    prev_year_safe = prev_year.replace(0, float("nan"))
    ubistva_clean["Промена"] = (curr_year - prev_year) / prev_year_safe
    ubistva_clean["Промена"] = ubistva_clean["Промена"].fillna(0)

    ubistva_clean["Промена текст"] = ubistva_clean["Промена"].apply(
        lambda x: f"{x*100:.1f}%" if pd.notnull(x) else "-"
    )
    ubistva_clean["Промена (плот)"] = ubistva_clean["Промена"].fillna(0)

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
      rule_u = base_lolli.mark_rule(color=BLUE_COLOR, strokeWidth=2).encode(
          y=alt.Y(
              "Промена (плот):Q", axis=alt.Axis(format="%"), title="Промена"
          ),
          y2="zero:Q",
      )
      circle_u = base_lolli.mark_circle(size=200, color=BLUE_COLOR).encode(
          y="Промена (плот):Q"
      )
      text_lolli = base_lolli.mark_text(
          align="center", dy=-14, fontSize=11
      ).encode(y="Промена (плот):Q", text="Промена текст:N")
      st.altair_chart(
          (rule_u + circle_u + text_lolli).properties(height=380),
          use_container_width=True,
      )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4.6 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА НАСИЛСТВО (СО ВЕРТИКАЛЕН LOLLIPOP ГРАФИК)
elif "Насилство" in selected_sheet:
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
    st.error("Не можат да се пронајдат заглавијата за оваа табела.")
    st.dataframe(df, use_container_width=True)
  else:
    header_row = raw.iloc[header_row_idx]
    year_cols = [
        col
        for col in raw.columns
        if str(header_row[col]).strip() in ["2024 година", "2023 година"]
    ]
    col_2024, col_2023 = year_cols[0], year_cols[1]
    promena_col = next(
        (
            col
            for col in raw.columns
            if "Промена" in str(header_row[col])
        ),
        None,
    )

    data_rows = raw.iloc[header_row_idx + 1 :].copy()
    data_rows = data_rows[data_rows[label_col].notna()]
    data_rows = data_rows[
        ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
    ]

    nasilstvo_clean = pd.DataFrame({
        "СВР": data_rows[label_col].values,
        "2024 година": pd.to_numeric(
            data_rows[col_2024], errors="coerce"
        ).fillna(0),
        "2023 година": pd.to_numeric(
            data_rows[col_2023], errors="coerce"
        ).fillna(0),
    }).dropna(subset=["СВР"])

    if promena_col is not None:
      nasilstvo_clean["Промена"] = (
          pd.to_numeric(data_rows[promena_col], errors="coerce")
          .fillna(0)
          .values
      )
    else:
      nasilstvo_clean["Промена"] = 0.0

    nasilstvo_clean["Промена текст"] = nasilstvo_clean["Промена"].apply(
        lambda x: f"{x*100:.1f}%"
    )
    nasilstvo_clean["Насока"] = nasilstvo_clean["Промена"].apply(
        lambda x: "Пораст" if x >= 0 else "Пад"
    )

    sector_order = nasilstvo_clean["СВР"].tolist()

    col1, col2 = st.columns(2)
    with col1:
      st.write("**Насилство: 2024 vs 2023 година**")
      melted_n = nasilstvo_clean.melt(
          id_vars=["СВР"],
          value_vars=["2024 година", "2023 година"],
          var_name="Година",
          value_name="Број",
      )
      base_n = alt.Chart(melted_n).encode(
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
      st.altair_chart(
          base_n.mark_bar().properties(height=380), use_container_width=True
      )

    with col2:
      st.write("**Насилство - Промена (%) - Вертикален Lollipop**")
      nasilstvo_clean["zero"] = 0
      base_v_lolli = alt.Chart(nasilstvo_clean).encode(
          x=alt.X(
              "СВР:N",
              title=None,
              sort=sector_order,
              axis=alt.Axis(labelAngle=270),
          )
      )
      color_enc = alt.Color(
          "Насока:N",
          scale=alt.Scale(domain=["Пораст", "Пад"], range=["#d62728", "#2ca02c"]),
          legend=alt.Legend(title=None),
      )
      rule_v = base_v_lolli.mark_rule(strokeWidth=2).encode(
          y=alt.Y(
              "Промена:Q", axis=alt.Axis(format="%"), title="Промена (%)"
          ),
          y2="zero:Q",
          color=color_enc,
      )
      circle_v = base_v_lolli.mark_circle(size=200).encode(
          y="Промена:Q", color=color_enc
      )
      text_v_pos = (
          base_v_lolli.transform_filter(alt.datum.Промена >= 0)
          .mark_text(align="center", dy=-12)
          .encode(y="Промена:Q", text="Промена текст:N")
      )
      text_v_neg = (
          base_v_lolli.transform_filter(alt.datum.Промена < 0)
          .mark_text(align="center", dy=15)
          .encode(y="Промена:Q", text="Промена текст:N")
      )
      st.altair_chart(
          (rule_v + circle_v + text_v_pos + text_v_neg).properties(height=380),
          use_container_width=True,
      )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4.6.5 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ТЕШКИ КРАЖБИ (СО DIVERGING BAR CHART - ЦРВЕНА/ЗЕЛЕНА)
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
    st.error("Не можат да се пронајдат заглавијата за оваа табела.")
    st.dataframe(df, use_container_width=True)
  else:
    header_row = raw.iloc[header_row_idx]
    year_cols = [
        col
        for col in raw.columns
        if str(header_row[col]).strip() in ["2024 година", "2023 година"]
    ]
    col_2024, col_2023 = year_cols[0], year_cols[1]
    promena_col = next(
        (
            col
            for col in raw.columns
            if "Промена" in str(header_row[col])
        ),
        None,
    )

    data_rows = raw.iloc[header_row_idx + 1 :].copy()
    data_rows = data_rows[data_rows[label_col].notna()]
    data_rows = data_rows[
        ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
    ]

    teski_clean = pd.DataFrame({
        "СВР": data_rows[label_col].values,
        "2024 година": pd.to_numeric(
            data_rows[col_2024], errors="coerce"
        ).fillna(0),
        "2023 година": pd.to_numeric(
            data_rows[col_2023], errors="coerce"
        ).fillna(0),
    }).dropna(subset=["СВР"])

    if promena_col is not None:
      teski_clean["Промена"] = (
          pd.to_numeric(data_rows[promena_col], errors="coerce")
          .fillna(0)
          .values
      )
    else:
      prev_y = teski_clean["2023 година"].replace(0, float("nan"))
      teski_clean["Промена"] = (
          (teski_clean["2024 година"] - teski_clean["2023 година"]) / prev_y
      ).fillna(0)

    teski_clean["Промена текст"] = teski_clean["Промена"].apply(
        lambda x: f"{x*100:.1f}%"
    )
    teski_clean["Насока"] = teski_clean["Промена"].apply(
        lambda x: "Пораст" if x >= 0 else "Пад"
    )

    sector_order = teski_clean["СВР"].tolist()

    col1, col2 = st.columns(2)
    with col1:
      st.write("**Тешки кражби: 2024 vs 2023 година**")
      melted_t = teski_clean.melt(
          id_vars=["СВР"],
          value_vars=["2024 година", "2023 година"],
          var_name="Година",
          value_name="Број",
      )
      base_t = alt.Chart(melted_t).encode(
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
      st.altair_chart(
          base_t.mark_bar().properties(height=380), use_container_width=True
      )

    with col2:
      st.write("**Тешки кражби - Промена (%) - Diverging Bar Chart**")
      base_div = alt.Chart(teski_clean).encode(
          y=alt.Y(
              "СВР:N",
              sort=sector_order,
              title=None,
              axis=alt.Axis(labelLimit=280),
          )
      )
      color_enc = alt.Color(
          "Насока:N",
          scale=alt.Scale(domain=["Пораст", "Пад"], range=["#d62728", "#2ca02c"]),
          legend=alt.Legend(title=None),
      )
      bars_div = base_div.mark_bar().encode(
          x=alt.X("Промена:Q", axis=alt.Axis(format="%"), title="Промена"),
          color=color_enc,
      )
      text_pos = (
          base_div.transform_filter(alt.datum.Промена >= 0)
          .mark_text(align="left", dx=5)
          .encode(x="Промена:Q", text="Промена текст:N")
      )
      text_neg = (
          base_div.transform_filter(alt.datum.Промена < 0)
          .mark_text(align="right", dx=-5)
          .encode(x="Промена:Q", text="Промена текст:N")
      )
      st.altair_chart(
          (bars_div + text_pos + text_neg).properties(height=380),
          use_container_width=True,
      )

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 4.7 СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА ТРГОВИЈА СО ЛУЃЕ (И ДЕЦА)
elif "трговија" in selected_sheet.lower() and "дрога" not in selected_sheet.lower():
  st.write("### 📊 Анализа за Трговија со луѓе и деца")

  table1_data = [
      {
          "Кривични дела": "Број на акциски контроли",
          "2024 година": 46,
          "2023 година": 38,
          "2022 година": 27,
      },
      {
          "Кривични дела": "Број на угостителски објекти",
          "2024 година": 67,
          "2023 година": 71,
          "2022 година": 38,
      },
      {
          "Кривични дела": "Број на странски државјани",
          "2024 година": 207,
          "2023 година": 185,
          "2022 година": 311,
      },
  ]
  df_table1 = pd.DataFrame(table1_data)

  table2_data = [
      {
          "Кривични дела": "Број на кривични дела",
          "2024 година": 2,
          "2023 година": 8,
          "2022 година": 7,
      },
      {
          "Кривични дела": "Број на сторители",
          "2024 година": 2,
          "2023 година": 31,
          "2022 година": 15,
      },
      {
          "Кривични дела": "Број на жртви",
          "2024 година": 2,
          "2023 година": 4,
          "2022 година": 5,
      },
  ]
  df_table2 = pd.DataFrame(table2_data)

  col1, col2 = st.columns(2)

  with col1:
    st.write("**Трговија со луѓе: 2024 vs 2023 vs 2022 година**")
    melted1 = df_table1.melt(
        id_vars=["Кривични дела"],
        value_vars=["2024 година", "2023 година", "2022 година"],
        var_name="Година",
        value_name="Број",
    )
    base1 = alt.Chart(melted1).encode(
        x=alt.X(
            "Кривични дела:N",
            title=None,
            sort=[
                "Број на акциски контроли",
                "Број на угостителски објекти",
                "Број на странски државјани",
            ],
            axis=alt.Axis(labelAngle=0, labelLimit=200),
        ),
        y=alt.Y("Број:Q", title="Број"),
        color=alt.Color(
            "Година:N",
            scale=alt.Scale(
                domain=["2024 година", "2023 година", "2022 година"],
                range=["#1f77b4", "#6baed6", "#c6dbef"],
            ),
            legend=alt.Legend(title="Година"),
        ),
        xOffset="Година:N",
    )
    bars1 = base1.mark_bar()
    text1 = base1.mark_text(dy=-8).encode(text="Број:Q")
    st.altair_chart(
        (bars1 + text1).properties(height=380), use_container_width=True
    )

  with col2:
    st.write("**Трговија со деца: 2024 vs 2023 vs 2022 година**")
    melted2 = df_table2.melt(
        id_vars=["Кривични дела"],
        value_vars=["2024 година", "2023 година", "2022 година"],
        var_name="Година",
        value_name="Број",
    )
    base2 = alt.Chart(melted2).encode(
        x=alt.X(
            "Кривични дела:N",
            title=None,
            sort=[
                "Број на кривични дела",
                "Број на сторители",
                "Број на жртви",
            ],
            axis=alt.Axis(labelAngle=0, labelLimit=200),
        ),
        y=alt.Y("Број:Q", title="Број"),
        color=alt.Color(
            "Година:N",
            scale=alt.Scale(
                domain=["2024 година", "2023 година", "2022 година"],
                range=["#d62728", "#f4a582", "#fddbc7"],
            ),
            legend=alt.Legend(title="Година"),
        ),
        xOffset="Година:N",
    )
    bars2 = base2.mark_bar()
    text2 = base2.mark_text(dy=-8).encode(text="Број:Q")
    st.altair_chart(
        (bars2 + text2).properties(height=380), use_container_width=True
    )

  st.subheader("📋 Детални табели")
  st.markdown("**Трговија со луѓе**")
  st.dataframe(df_table1, use_container_width=True, hide_index=True)

  st.markdown("**Трговија со деца**")
  st.dataframe(df_table2, use_container_width=True, hide_index=True)

# 5. СТАНДАРДЕН ПРИКАЗ ЗА ДРУГИ ЛИСТОВИ
else:
  st.dataframe(df, use_container_width=True)
