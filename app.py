import pandas as pd
import pydeck as pdk
import streamlit as st

# principal page configuration
st.set_page_config(
    page_title="Australian Languages Explorer", layout="wide"
)

# CSS style
st.markdown(
    """
    <style>
    @import url('https://googleapis.com/css2?family=Federo&family=Lora:ital,wght@0,400..700;1,400..700&family=Noto+Sans:ital,wght@0,100..900;1,100..900&family=Platypi:ital,wght@0,300..800;1,300..800&display=swap" rel="stylesheet');

    /* Appliquer la police */
    html, body, [class*="css"] {
        font-family: 'Platypi', sans-serif !important;
    }

    /* Fond général de l'application */
    .stApp {
        background-color: #f8fafc !important;
    }
    
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 24px;
        font-weight: 600;
        color: #334155;
        border: 1px solid #cbd5e1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d9488 !important;
        color: #ffffff !important;
        font-weight: 700;
        border-color: #0f766e !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# loading the data
@st.cache_data
def load_data():
    return pd.read_csv("language_learning_data.csv")


df = load_data()

# HEADER
st.title("Australian Languages Explorer & Learning Tool🐨💬")
st.markdown(
    "Explore the cultural richness and diversity of Aboriginal and Torres Strait Islander languages."
)
st.markdown("---")

# views creation
tab_explorer, tab_quiz, tab_stats = st.tabs([
    "📖 Language Explorer",
    "🧠 Quiz & Learning",
    "📊 Analytics & Map",
])

#------------------------------------------------------------------------------
# VIEW 1 : language cards
with tab_explorer:
    st.header("Language Explorer by Region")
    st.write(
        "Click on one of the regions below to filter the corresponding languages:"
    )

    # Initialisation of the filter
    if "selected_region" not in st.session_state:
        st.session_state.selected_region = "Toutes"

    regions = ["Toutes", "WA", "QLD", "NT", "NSW", "VIC", "SA", "TAS", "TSI"]

    # region filter buttons
    st.markdown("##### 🌍 Quick geographic filters")
    cols_regions = st.columns(len(regions))
    for i, reg in enumerate(regions):
        with cols_regions[i]:
            btn_type = (
                "primary" if st.session_state.selected_region == reg else "secondary"
            )
            
            if st.button(reg, use_container_width=True, type=btn_type):
                st.session_state.selected_region = reg
                st.rerun()  # reload trigger

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        available_statuses = ["Tous"] + sorted(df["statut"].dropna().unique())
        status_filter = st.selectbox(
            "Filter by Documentation Status:", available_statuses
        )
    with col2:
        text_search = st.text_input(
            "Search by language name or AUSTLANG code:"
        )

    # cumulated filters
    filtered_df = df.copy()
    if st.session_state.selected_region != "Toutes":
        filtered_df = filtered_df[
            filtered_df["territoire"] == st.session_state.selected_region
        ]
    if status_filter != "Tous":
        filtered_df = filtered_df[filtered_df["statut"] == status_filter]
    if text_search:
        filtered_df = filtered_df[
            filtered_df["nom_langue"]
            .str.contains(text_search, case=False, na=False)
            | filtered_df["code"]
            .str.contains(text_search, case=False, na=False)
        ]

    st.info(
        f"✨ Displaying for region: **{st.session_state.selected_region}** —"
        f" **{len(filtered_df)}** languages found."
    )

    # create columns for the card
    cols_per_row = 3
    rows = [
        filtered_df.iloc[i : i + cols_per_row]
        for i in range(0, len(filtered_df), cols_per_row)
    ]

    # create a grid for the cards
    st.markdown("##### 📚 Matching languages list")
    for row_df in rows:
        cols = st.columns(cols_per_row)
        for idx, (_, row) in enumerate(row_df.iterrows()):
            with cols[idx]:
                # st.container(border=True) isolate each element in a box
                with st.container(border=True):
                    badge_color = "🟢" if row["statut"] == "Confirmed" else "🟠"
                    st.markdown(f"### 🗣️ {row['nom_langue']}")
                    st.caption(
                        f"**Code:** `{row['code']}` | **Region:** `{row['territoire']}`"
                    )
                    st.markdown(f"**Status:** {badge_color} `{row['statut']}`")

                    desc = str(row["description"])
                    if len(desc) > 130:
                        desc = desc[:130] + "..."
                    st.write(desc)

                    # st.expander create an expandable box to see more details
                    with st.expander("View more details"):
                        st.markdown(f"**Location:** {row['localisation']}")
                        st.markdown(f"**Full description:** {row['description']}")

#--------------------------------------------------------------------
# VIEW 2 : Quiz
with tab_quiz:
    st.header("Quiz Mode: Test Your Knowledge!")
    st.write(
        "Test your geographic understanding by selecting the correct"
        " region for each proposed language."
    )

    # quiz initialisation
    if "quiz_language" not in st.session_state:
        st.session_state.quiz_language = df.sample(1).iloc[0]
        st.session_state.score = 0
        st.session_state.feedback = None

    current_language = st.session_state.quiz_language

    with st.container(border=True):
        st.markdown(f"### 🎯 Language to identify: **{current_language['nom_langue']}**")
        st.caption(
            f"AUSTLANG Code: `{current_language['code']}` | Status:"
            f" `{current_language['statut']}`"
        )

        loc_quiz = str(current_language["localisation"])
        if len(loc_quiz) > 200:
            loc_quiz = loc_quiz[:200] + "..."
        st.info(f"💡 **Location Hint:** {loc_quiz}")

    st.markdown("#### 🗺️ Click on the region of origin for this language:")

    quiz_regions = sorted(df["territoire"].unique())
    quiz_cols = st.columns(4)

    # Quiz buttons creation
    st.markdown("##### 🧭 Region choice")
    for i, reg in enumerate(quiz_regions):
        with quiz_cols[i % 4]:
            # use_container_width=True makes the buttons the same size and use all the page width
            if st.button(reg, use_container_width=True, key=f"btn_reg_{reg}"):
                if reg == current_language["territoire"]:
                    st.session_state.score += 1
                    st.session_state.feedback = (
                        "success",
                        (
                            "Correct! **"
                            + str(current_language["nom_langue"])
                            + "** originates from the **"
                            + str(reg)
                            + "** region 🎉"
                        ),
                    )
                else:
                    st.session_state.feedback = (
                        "error",
                        (
                            "Incorrect! The correct region for this language was **"
                            + str(current_language["territoire"])
                            + "** (not "
                            + str(reg)
                            + ")."
                        ),
                    )
                st.rerun()

    if st.session_state.feedback:
        st_type, msg = st.session_state.feedback
        if st_type == "success":
            st.success(msg)
        else:
            st.error(msg)

        if st.button("➡️ Next Question"):
            st.session_state.quiz_language = df.sample(1).iloc[0]
            st.session_state.feedback = None
            st.rerun()

    st.markdown("---")
    st.metric("🏆 Your Current Score", f"{st.session_state.score} points")

# ---------------------------------------------------------------------------
# VIEW 3 : Stats & Map
with tab_stats:
    st.header("Statistical Analysis and Cartography")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribution by Region")
        st.bar_chart(df["territoire"].value_counts())

    with col_b:
        st.subheader("Documentation Status")
        st.bar_chart(df["statut"].value_counts())

    st.subheader("Global Map of Geolocated Languages")
    # Filter rows with valid GPS coordinates for the map
    map_df = df.dropna(subset=["latitude", "longitude"])

    # put australia in the center of the map
    view_state = pdk.ViewState(
        latitude=-25.2744, longitude=133.7751, zoom=3.5, pitch=0
    )

    # layer to show the points
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["longitude", "latitude"],
        get_color=[13, 148, 136, 190],
        get_radius=30000,
        pickable=True,
        auto_highlight=True,
    )

    # put the layers together
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="light",
        tooltip={
            "text": (
                "Language: {nom_langue}\nCode: {code}\nRegion:"
                " {territoire}\nStatus: {statut}"
            )
        },
    )

    # show the pydeck in streamlit
    st.pydeck_chart(r)
    st.write(
        f"Displaying {len(map_df)} geolocated languages on the map of"
        " Australia."
    )