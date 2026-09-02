import altair as alt
import pandas as pd
import streamlit as st

# Подесување на страницата
st.set_page_config(
    page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide"
)

# Наслов на апликацијата
st.sidebar.title("Мени")
file_path = "KRIMINALITET.xlsx"  # Пат до вашиот Excel фајл

# Список на листови (категории) врз основа на Excel фајлот
sheets = [
    "Кривични дела против државата",
    "Убиства",
    "Насилство",
    "Трговија со луѓе",
    "Тешки кражби",
    "Корупција",
]

selected_sheet = st.sidebar.selectbox("Избери категорија:", sheets)

st.title(f"📊 Анализа на криминалитет: {selected_sheet}")

# СПЕЦИЈАЛИЗИРАН ПРИКАЗ ЗА КОРУПЦИЈА
if "Корупција" in selected_sheet:

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
        "Промена %": pd.to_numeric(raw_k.iloc[:, 6], errors="coerce").fillna(0),
        "Сторители 2024": pd.to_numeric(raw_k.iloc[:, 7], errors="coerce").fillna(
            0
        ),
        "Сторители 2023": pd.to_numeric(raw_k.iloc[:, 8], errors="coerce").fillna(
            0
        ),
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
            "СВР:N", title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)
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
            "СВР:N", title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)
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

    # 1. Кривични дела и 2. Сторители еден до друг (како што е редоследот)
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

    # 3. Трет графикон: Промена % со точни вредности (Diverging Chart)
    st.write("**3. Корупција - Промена % (Diverging Chart)**")
    base_div = alt.Chart(korupcija_clean).encode(
        x=alt.X(
            "СВР:N", title=None, sort=sector_order, axis=alt.Axis(labelAngle=270)
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

# ОПШТ ПРИКАЗ ЗА ОСТАНАТИТЕ КАТЕГОРИИ
else:

  @st.cache_data
  def load_data(sheet):
    return pd.read_excel(file_path, sheet_name=sheet, header=4)

  try:
    raw_df = load_data(selected_sheet)
    if len(raw_df.columns) > 0:
      raw_df = raw_df.dropna(subset=[raw_df.columns[0]])

    df_clean = pd.DataFrame({
        "СВР": raw_df.iloc[:, 0].values,
        "КД 2024": pd.to_numeric(raw_df.iloc[:, 4], errors="coerce").fillna(0),
        "КД 2023": pd.to_numeric(raw_df.iloc[:, 5], errors="coerce").fillna(0),
        "Промена %": pd.to_numeric(raw_df.iloc[:, 6], errors="coerce").fillna(0),
        "Сторители 2024": pd.to_numeric(raw_df.iloc[:, 7], errors="coerce").fillna(
            0
        ),
        "Сторители 2023": pd.to_numeric(raw_df.iloc[:, 8], errors="coerce").fillna(
            0
        ),
    })

    df_clean = df_clean[
        df_clean["СВР"].astype(str).str.contains("СВР|ОСОСК", na=False)
    ]
    sector_order = df_clean["СВР"].tolist()

    melted_kd = df_clean.melt(
        id_vars=["СВР"],
        value_vars=["КД 2024", "КД 2023"],
        var_name="Година",
        value_name="Број",
    )
    melted_kd["Година"] = melted_kd["Година"].replace(
        {"КД 2024": "2024 година", "КД 2023": "2023 година"}
    )

    melted_stor = df_clean.melt(
        id_vars=["СВР"],
        value_vars=["Сторители 2024", "Сторители 2023"],
        var_name="Година",
        value_name="Број",
    )
    melted_stor["Година"] = melted_stor["Година"].replace(
        {"Сторители 2024": "2024 година", "Сторители 2023": "2023 година"}
    )

    chart_kd = (
        alt.Chart(melted_kd)
        .mark_bar()
        .encode(
            x=alt.X(
                "СВР:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            ),
            y=alt.Y("Број:Q", title="Број"),
            color=alt.Color(
                "Година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#1f77b4", "#aec7e8"],
                ),
            ),
            xOffset="Година:N",
        )
    )

    chart_stor = (
        alt.Chart(melted_stor)
        .mark_bar()
        .encode(
            x=alt.X(
                "СВР:N",
                title=None,
                sort=sector_order,
                axis=alt.Axis(labelAngle=270),
            ),
            y=alt.Y("Број:Q", title="Број"),
            color=alt.Color(
                "Година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#1f77b4", "#aec7e8"],
                ),
            ),
            xOffset="Година:N",
        )
    )

    col1, col2 = st.columns(2)
    with col1:
      st.write(f"**1. {selected_sheet}: Кривични дела (2024 vs 2023)**")
      st.altair_chart(chart_kd.properties(height=350), use_container_width=True)
    with col2:
      st.write(f"**2. {selected_sheet}: Сторители (2024 vs 2023)**")
      st.altair_chart(
          chart_stor.properties(height=350), use_container_width=True
      )

    st.subheader("📋 Детална табела")
    st.dataframe(raw_df, use_container_width=True, hide_index=True)

  except Exception as e:
    st.error(f"Грешка при вчитување на податоците: {e}")
