import altair as alt
import pandas as pd
import streamlit as st

# Подесување на страницата
st.set_page_config(
    page_title="Urban Crime Analysis 2024", page_icon="📊", layout="wide"
)

st.title("📊 Urban Crime Analysis 2024 vs 2023")

# Вчитување на податоците (прилагодете го името на фајлот доколку е потребно)
@st.cache_data
def load_data():
    # Заменете со вашиот пат до Excel или CSV фајлот
    df = pd.read_excel("KRIMINALITET.xlsx")
    return df


try:
    df = load_data()
except Exception as e:
    st.error(
        f"Грешка при вчитување на податоците: {e}. Проверете дали фајлот е во директориумот."
    )
    st.stop()

# Страничен мени за избор на категорија (пример колона 'Kategorija' или слична)
if "Kategorija" in df.columns:
    categories = df["Kategorija"].unique()
    selected_category = st.sidebar.selectbox("Избери категорија:", categories)
    filtered_df = df[df["Kategorija"] == selected_category]
else:
    filtered_df = df
    st.sidebar.info("Колоната 'Kategorija' не е пронајдена во податоците.")

# Главен наслов на секцијата
st.markdown("## 🗂 Кривични дела против државата")

# Прв графикон: Споредба по кривични дела (2024 vs 2023)
st.subheader("Споредба по кривични дела (2024 vs 2023)")

if (
    not filtered_df.empty
    and "KrivicnoDela" in filtered_df.columns
    and "2024" in filtered_df.columns
    and "2023" in filtered_df.columns
):
    # Трансформација на податоците во погодна форма за Altair (melt)
    df_melted = filtered_df.melt(
        id_vars=["KrivicnoDela"],
        value_vars=["2024", "2023"],
        var_name="Година",
        value_name="Број",
    )

    chart1 = (
        alt.Chart(df_melted)
        .mark_bar()
        .encode(
            x=alt.X("Број:Q", title="Број"),
            y=alt.Y(
                "KrivicnoDela:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelLimit=300),
            ),
            color=alt.Color(
                "Година:N",
                scale=alt.Scale(
                    domain=["2024 година", "2023 година"],
                    range=["#2ca02c", "#98df8a"],
                ),
            ),
            row=alt.Row("Година:N", header=alt.Header(title="Година")),
        )
        .properties(height=250)
    )

    st.altair_chart(chart1, use_container_width=True)
else:
    st.warning(
        "Недостигаат потребните колони за првиот графикон ('KrivicnoDela', '2024', '2023')."
    )

# Втор графикон: Промена (%) - Хоризонтален Lollipop (Поправен дел)
st.subheader("Промена (%) - Хоризонтален Lollipop")

if "promena_procent" not in filtered_df.columns and {
    "2024",
    "2023",
}.issubset(filtered_df.columns):
    # Пресметка на процентна промена доколку не постои
    filtered_df["promena_procent"] = (
        (filtered_df["2024"] - filtered_df["2023"]) / filtered_df["2023"]
    ) * 100

if not filtered_df.empty and "promena_procent" in filtered_df.columns:
    base = alt.Chart(filtered_df).encode(
        y=alt.Y("KrivicnoDela:N", sort="-x", title=None)
    )

    # Lollipop линии
    lines = base.mark_rule().encode(
        x=alt.X("promena_procent:Q", title="Промена (%)"),
        x2=alt.X2(value=0),
    )

    # Lollipop точки
    points = base.mark_circle(size=80).encode(
        x=alt.X("promena_procent:Q"),
        color=alt.condition(
            alt.datum.promena_procent > 0,
            alt.value("#2ca02c"),  # Зелена за позитивна
            alt.value("#d62728"),  # Црвена за негативна
        ),
    )

    # Поправен филтер без AttributeError (замена на .notnull() со валиден синтаксички израз)
    lollipop_chart = (
        (lines + points)
        .properties(width=600, height=350)
        .transform_filter(
            (alt.datum.promena_procent != None)
            & (alt.expr.isValid(alt.datum.promena_procent))
        )
    )

    st.altair_chart(lollipop_chart, use_container_width=True)
else:
    st.warning("Колоната 'promena_procent' не е достапна за вториот графикон.")
