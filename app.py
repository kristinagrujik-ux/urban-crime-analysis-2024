import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide"
)

file_path = "KRIMINALITET.xlsx"


@st.cache_data
def get_sheets():
  return pd.ExcelFile(file_path).sheet_names


selected_sheet = st.sidebar.selectbox("Izber kategorijata:", get_sheets())
st.title(f"📊 {selected_sheet}")


@st.cache_data
def load_data(sheet):
  return pd.read_excel(file_path, sheet_name=sheet)


df = load_data(selected_sheet)
BLUE_COLOR = "#1f77b4"

# 1. SPECIJALEN SLUČAJ: Tabelata za Krivični dela protiv državata
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

# 1.2 SPECIJALIZIRAN PRIKAZ ZA VKUPEN KRIMINALITET
elif (
    "Вкупен криминалитет" in selected_sheet
    or "вкупен криминалитет" in selected_sheet.lower()
):
  raw = df.copy()

  try:
    vk_df = pd.DataFrame({
        "СВР": raw.iloc[1:, 0].values,
        "Кривични дела": pd.to_numeric(
            raw.iloc[1:, 2], errors="coerce"
        ).fillna(0),
        "Сторители": pd.to_numeric(
            raw.iloc[1:, 8] if raw.shape[1] > 8 else raw.iloc[1:, -1],
            errors="coerce",
        ).fillna(0),
    }).dropna(subset=["СВР"])
  except Exception:
    vk_df = raw.iloc[:, [0, 2, 4]].copy()
    vk_df.columns = ["СВР", "Кривични дела", "Сторители"]
    vk_df["Кривични дела"] = pd.to_numeric(
        vk_df["Кривични дела"], errors="coerce"
    ).fillna(0)
    vk_df["Сторители"] = pd.to_numeric(
        vk_df["Сторители"], errors="coerce"
    ).fillna(0)

  vk_df = vk_df[vk_df["СВР"].astype(str).str.contains("СВР|ОСОСК", na=False)]
  svr_order = vk_df["СВР"].tolist()

  col1, col2 = st.columns(2)

  with col1:
    st.write("**Вкупен криминалитет - Кривични дела по СВР**")
    base_vk_kd = alt.Chart(vk_df).encode(
        x=alt.X(
            "СВР:N",
            title=None,
            sort=svr_order,
            axis=alt.Axis(labelAngle=270),
        ),
        y=alt.Y(
            "Кривични дела:Q",
            title="Број на кривични дела",
            axis=alt.Axis(format="d", tickMinStep=1),
        ),
    )
    bars_vk_kd = base_vk_kd.mark_bar(color=BLUE_COLOR)
    text_vk_kd = base_vk_kd.mark_text(
        align="center", dy=-8, fontSize=10
    ).encode(text="Кривични дела:Q")
    st.altair_chart(
        (bars_vk_kd + text_vk_kd).properties(height=380), use_container_width=True
    )

  with col2:
    st.write("**Вкупен криминалитет - Сторители по СВР**")
    base_vk_st = alt.Chart(vk_df).encode(
        x=alt.X(
            "СВР:N",
            title=None,
            sort=svr_order,
            axis=alt.Axis(labelAngle=270),
        ),
        y=alt.Y(
            "Сторители:Q",
            title="Број на сторители",
            axis=alt.Axis(format="d", tickMinStep=1),
        ),
    )
    bars_vk_st = base_vk_st.mark_bar(color="#2ca02c")
    text_vk_st = base_vk_st.mark_text(
        align="center", dy=-8, fontSize=10
    ).encode(text="Сторители:Q")
    st.altair_chart(
        (bars_vk_st + text_vk_st).properties(height=380), use_container_width=True
    )

  st.subheader("📋 Детална табела")
  st.dataframe(df, use_container_width=True)

# 1.3 SPECIJALIZIRAN PRIKAZ ZA TEŠKI KRAŽBI
elif "Тешки кражби" in selected_sheet:
  raw = df.copy()

  header_row_idx = None
  for i in range(min(5, len(raw))):
    row_vals = raw.iloc[i].fillna("").astype(str)
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
    label_col = raw.columns[0]

    col_2024 = next(
        col for col in raw.columns if "2024" in str(header_row[col])
    )
    col_2023 = next(
        col for col in raw.columns if "2023" in str(header_row[col])
    )
    promena_col = next(
        (col for col in raw.columns if "Промена" in str(header_row[col])), None
    )

    data_rows = raw.iloc[header_row_idx + 1 :].copy()
    data_rows = data_rows[data_rows[label_col].notna()]
    data_rows_svr = data_rows[
        ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
    ]

    tk_clean = pd.DataFrame({
        "СВР": data_rows_svr[label_col].values,
        "2024 година": pd.to_numeric(
            data_rows_svr[col_2024], errors="coerce"
        ).fillna(0),
        "2023 година": pd.to_numeric(
            data_rows_svr[col_2023], errors="coerce"
        ).fillna(0),
    }).dropna(subset=["СВР"])

    if promena_col is not None:
      tk_clean["Промена"] = (
          pd.to_numeric(data_rows_svr[promena_col], errors="coerce")
          .fillna(0)
          .values
      )
    else:
      prev = tk_clean["2023 година"].replace(0, float("nan"))
      tk_clean["Промена"] = (
          (tk_clean["2024 година"] - tk_clean["2023 година"]) / prev
      ).fillna(0)

    tk_clean["Промена (%)"] = tk_clean["Промена"] * 100
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
      text_tk = base_tk.mark_text(align="center", dy=-8, fontSize=10).encode(
          text="Број:Q"
      )
      st.altair_chart(
          (bars_tk + text_tk).properties(height=380), use_container_width=True
      )

    with col2:
      st.write("**Тешки кражби - Промена (%) - Horizontal Bar Chart**")
      fig_hbar = px.bar(
          tk_clean,
          x="Промена (%)",
          y="СВР",
          orientation="h",
          text=tk_clean["Промена (%)"].apply(lambda x: f"{x:.1f}%"),
          color="Промена (%)",
          color_continuous_scale=["#d62728", "#1f77b4"],
      )
      fig_hbar.update_traces(textposition="outside")
      fig_hbar.update_layout(
          height=380,
          margin=dict(l=10, r=10, t=30, b=10),
          coloraxis_showscale=False,
          yaxis=dict(autorange="reversed", title=None),
          xaxis=dict(title="Промена (%)"),
      )
      st.plotly_chart(fig_hbar, use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 1.4 SPECIJALIZIRAN PRIKAZ ZA NASILSTVO
elif "Насилство" in selected_sheet:
  raw = df.copy()

  header_row_idx = None
  for i in range(min(5, len(raw))):
    row_vals = raw.iloc[i].fillna("").astype(str)
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
    label_col = raw.columns[0]

    col_2024 = next(
        col for col in raw.columns if "2024" in str(header_row[col])
    )
    col_2023 = next(
        col for col in raw.columns if "2023" in str(header_row[col])
    )
    promena_col = next(
        (col for col in raw.columns if "Промена" in str(header_row[col])), None
    )

    data_rows = raw.iloc[header_row_idx + 1 :].copy()
    data_rows = data_rows[data_rows[label_col].notna()]
    data_rows_svr = data_rows[
        ~data_rows[label_col].astype(str).str.contains("Вкупно", na=False)
    ]

    nas_clean = pd.DataFrame({
        "СВР": data_rows_svr[label_col].values,
        "2024 година": pd.to_numeric(
            data_rows_svr[col_2024], errors="coerce"
        ).fillna(0),
        "2023 година": pd.to_numeric(
            data_rows_svr[col_2023], errors="coerce"
        ).fillna(0),
    }).dropna(subset=["СВР"])

    if promena_col is not None:
      nas_clean["Промена"] = (
          pd.to_numeric(data_rows_svr[promena_col], errors="coerce")
          .fillna(0)
          .values
      )
    else:
      prev = nas_clean["2023 година"].replace(0, float("nan"))
      nas_clean["Промена"] = (
          (nas_clean["2024 година"] - nas_clean["2023 година"]) / prev
      ).fillna(0)

    nas_clean["Промена (%)"] = nas_clean["Промена"] * 100
    nas_clean["Промена текст"] = nas_clean["Промена (%)"].apply(
        lambda x: f"{x:.1f}%"
    )
    sector_order = nas_clean["СВР"].tolist()

    col1, col2 = st.columns(2)

    with col1:
      st.write("**Насилство: 2024 vs 2023 година**")
      melted_nas = nas_clean.melt(
          id_vars=["СВР"],
          value_vars=["2024 година", "2023 година"],
          var_name="Година",
          value_name="Број",
      )
      base_nas = alt.Chart(melted_nas).encode(
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
      bars_nas = base_nas.mark_bar()
      text_nas = base_nas.mark_text(align="center", dy=-8, fontSize=10).encode(
          text="Број:Q"
      )
      st.altair_chart(
          (bars_nas + text_nas).properties(height=380), use_container_width=True
      )

    with col2:
      st.write("**Насилство - Промена (%) - Vertical Lollipop Chart**")
      fig_lolly = go.Figure()

      # Додавање на линиите (стебленцата) за вертикалниот lollipop график
      for _, row in nas_clean.iterrows():
        fig_lolly.add_trace(
            go.Scatter(
                x=[row["СВР"], row["СВР"]],
                y=[0, row["Промена (%)"]],
                mode="lines",
                line=dict(
                    color="red" if row["Промена (%)"] >= 0 else "green", width=3
                ),
                showlegend=False,
            )
        )

      # Додавање на круговите (главите) и текстот
      fig_lolly.add_trace(
          go.Scatter(
              x=nas_clean["СВР"],
              y=nas_clean["Промена (%)"],
              mode="markers+text",
              marker=dict(
                  size=12,
                  color=[
                      "red" if val >= 0 else "green"
                      for val in nas_clean["Промена (%)"]
                  ],
              ),
              text=nas_clean["Промена текст"],
              textposition="top center",
              showlegend=False,
          )
      )

      fig_lolly.update_layout(
          height=380,
          margin=dict(l=10, r=10, t=30, b=10),
          xaxis=dict(title=None, tickangle=270),
          yaxis=dict(title="Промена (%)"),
      )
      st.plotly_chart(fig_lolly, use_container_width=True)

    st.subheader("📋 Детална табела")
    st.dataframe(df, use_container_width=True)

# 2. SPECIJALIZIRAN PRIKAZ ZA KRIUMČARENJE NA MIGRANTI
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

# 3. SPECIJALIZIRAN PRIKAZ ZA NEDOZVOLENA TRGOVIJA SO DROGA
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

# 4. DEFAULT PRIKAZ ZA OSTANATITE LISTOVI
else:
  st.subheader("📋 Детална табела")
  st.dataframe(df, use_container_width=True)
