from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "duplicate_candidates.csv"
)


st.set_page_config(
    page_title="Duplicate Overlap",
    page_icon="🔗",
    layout="wide"
)


@st.cache_data
def load_overlap_data():

    return pd.read_csv(INPUT_FILE)


df = load_overlap_data()


st.title("Potential Duplicate / Overlap Detection")

st.markdown(
    """
    Projects shown here have similar descriptions and related
    financial or timeline characteristics. These are potential
    overlap signals for human review and do not confirm that
    projects are duplicates.
    """
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Potential Overlap Pairs",
        f"{len(df):,}"
    )


with col2:
    high_overlap = (
        df["Review_Category"]
        .isin(["High", "Critical"])
        .sum()
    )

    st.metric(
        "High / Critical",
        f"{high_overlap:,}"
    )


with col3:
    st.metric(
        "Average Similarity",
        f"{df['Semantic_Similarity'].mean():.2f}"
    )


with col4:
    st.metric(
        "Average Overlap Score",
        f"{df['Overlap_Score'].mean():.2f}"
    )


st.divider()


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.subheader("Filters")

categories = st.multiselect(
    "Review Category",
    options=[
        "Low",
        "Medium",
        "High",
        "Critical",
    ],
    default=[
        "Medium",
        "High",
        "Critical",
    ]
)


filtered_df = df[
    df["Review_Category"].isin(categories)
].copy()


# ---------------------------------------------------------
# Potential overlap pairs
# ---------------------------------------------------------

st.subheader("Potential Overlap Pairs")


display_columns = [
    "Work_ID_A",
    "Work_ID_B",
    "Work_Category",
    "Semantic_Similarity",
    "Cost_Similarity",
    "Date_Similarity",
    "Overlap_Score",
    "Review_Category",
]


display_df = (
    filtered_df[display_columns]
    .sort_values(
        "Overlap_Score",
        ascending=False
    )
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Selected pair details
# ---------------------------------------------------------

st.divider()

st.subheader("Pair Investigation")


if len(filtered_df) > 0:

    pair_options = (
        filtered_df.apply(
            lambda row:
            f"{row['Work_ID_A']}  ↔  {row['Work_ID_B']}",
            axis=1
        )
        .tolist()
    )

    selected_pair = st.selectbox(
        "Select a potential overlap pair",
        options=pair_options
    )

    selected_index = pair_options.index(
        selected_pair
    )

    pair = filtered_df.iloc[selected_index]


    col1, col2 = st.columns(2)


    with col1:

        st.markdown("### Project A")

        st.write(
            f"**Work ID:** {pair['Work_ID_A']}"
        )

        st.write(
            f"**Description:** {pair['Description_A']}"
        )

        st.write(
            f"**Sanction Amount:** "
            f"₹{pair['Sanction_Amount_A']:,.0f}"
        )

        st.write(
            f"**Sanction Date:** "
            f"{pair['Sanction_Date_A']}"
        )


    with col2:

        st.markdown("### Project B")

        st.write(
            f"**Work ID:** {pair['Work_ID_B']}"
        )

        st.write(
            f"**Description:** {pair['Description_B']}"
        )

        st.write(
            f"**Sanction Amount:** "
            f"₹{pair['Sanction_Amount_B']:,.0f}"
        )

        st.write(
            f"**Sanction Date:** "
            f"{pair['Sanction_Date_B']}"
        )


    st.divider()


    score_col1, score_col2, score_col3, score_col4 = (
        st.columns(4)
    )


    with score_col1:

        st.metric(
            "Semantic Similarity",
            f"{pair['Semantic_Similarity']:.4f}"
        )


    with score_col2:

        st.metric(
            "Cost Similarity",
            f"{pair['Cost_Similarity']:.2f}"
        )


    with score_col3:

        st.metric(
            "Date Similarity",
            f"{pair['Date_Similarity']:.2f}"
        )


    with score_col4:

        st.metric(
            "Overlap Score",
            f"{pair['Overlap_Score']:.2f}"
        )


st.caption(
    "Semantic similarity is generated using a pre-trained "
    "sentence-transformer model. Similarity indicates a "
    "screening signal and does not establish that two works "
    "are duplicates."
)
