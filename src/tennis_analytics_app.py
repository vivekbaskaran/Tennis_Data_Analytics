
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Tennis Analytics Dashboard",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Connect to the database
@st.cache_resource
def get_connection():
    return sqlite3.connect('tennis_analytics.db')

# Function to execute SQL query and return DataFrame
@st.cache_data
def run_query(query):
    conn = get_connection()
    result = pd.read_sql_query(query, conn)
    return result

# Sidebar navigation
st.sidebar.title("Tennis Analytics")

page = st.sidebar.radio(
    "Navigate to",
    ["Dashboard", "Competitions", "Venues", "Competitors", "Search", "About"]
)

# Dashboard page
if page == "Dashboard":
    st.title("🎾 Tennis Analytics Dashboard")
    st.subheader("Unlocking Tennis Data with SportRadar API")

    # Create columns for summary statistics
    col1, col2, col3 = st.columns(3)

    # Total competitors
    total_competitors = run_query("SELECT COUNT(*) as count FROM Competitors").iloc[0]['count']
    col1.metric("Total Competitors", total_competitors)

    # Total countries
    total_countries = run_query("SELECT COUNT(DISTINCT country) as count FROM Competitors").iloc[0]['count']
    col2.metric("Countries Represented", total_countries)

    # Highest points
    highest_points = run_query("SELECT MAX(points) as max_points FROM Competitor_Rankings").iloc[0]['max_points']
    col3.metric("Highest Points", highest_points)

    st.markdown("---")

    # Create two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Competitors by Country")
        country_data = run_query("""
            SELECT country, COUNT(*) as count 
            FROM Competitors 
            GROUP BY country 
            ORDER BY count DESC 
            LIMIT 10
        """)
        fig = px.bar(country_data, x='country', y='count', color='count',
                    title="Top 10 Countries by Number of Competitors")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Competition Types Distribution")
        type_data = run_query("""
            SELECT type, COUNT(*) as count 
            FROM Competitions 
            GROUP BY type
        """)
        fig = px.pie(type_data, values='count', names='type', 
                    title="Distribution of Competition Types")
        st.plotly_chart(fig, use_container_width=True)

    # Rankings distribution
    st.subheader("Rankings Distribution")
    rank_data = run_query("""
        SELECT rank, points FROM Competitor_Rankings ORDER BY rank LIMIT 50
    """)
    fig = px.scatter(rank_data, x='rank', y='points', 
                    title="Relationship between Rank and Points (Top 50)",
                    labels={"rank": "Rank", "points": "Points"})
    st.plotly_chart(fig, use_container_width=True)

# Competitions page
elif page == "Competitions":
    st.title("Tennis Competitions")

    # Filters
    st.sidebar.header("Filters")

    # Get unique categories
    categories = run_query("SELECT DISTINCT category_name FROM Categories ORDER BY category_name")
    selected_category = st.sidebar.selectbox("Select Category", ["All"] + categories['category_name'].tolist())

    # Get unique types
    types = run_query("SELECT DISTINCT type FROM Competitions ORDER BY type")
    selected_type = st.sidebar.selectbox("Select Type", ["All"] + types['type'].tolist())

    # Get unique genders
    genders = run_query("SELECT DISTINCT gender FROM Competitions ORDER BY gender")
    selected_gender = st.sidebar.selectbox("Select Gender", ["All"] + genders['gender'].tolist())

    # Build query based on filters
    query = """
    SELECT c.competition_id, c.competition_name, cat.category_name, c.type, c.gender
    FROM Competitions c
    JOIN Categories cat ON c.category_id = cat.category_id
    WHERE 1=1
    """

    if selected_category != "All":
        query += f" AND cat.category_name = '{selected_category}'"

    if selected_type != "All":
        query += f" AND c.type = '{selected_type}'"

    if selected_gender != "All":
        query += f" AND c.gender = '{selected_gender}'"

    competitions = run_query(query)

    # Display competitions
    st.write(f"Showing {len(competitions)} competitions")
    st.dataframe(competitions)

    # Visualizations
    st.subheader("Competitions Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Competition count by category
        category_data = run_query("""
            SELECT cat.category_name, COUNT(c.competition_id) as count
            FROM Competitions c
            JOIN Categories cat ON c.category_id = cat.category_id
            GROUP BY cat.category_name
            ORDER BY count DESC
            LIMIT 10
        """)
        fig = px.bar(category_data, x='category_name', y='count', 
                    title="Top 10 Categories by Number of Competitions")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Gender distribution
        gender_data = run_query("""
            SELECT gender, COUNT(*) as count 
            FROM Competitions 
            GROUP BY gender
        """)
        fig = px.pie(gender_data, values='count', names='gender', 
                    title="Gender Distribution in Competitions")
        st.plotly_chart(fig, use_container_width=True)

# Venues page
elif page == "Venues":
    st.title("Tennis Venues")

    # Filters
    st.sidebar.header("Filters")

    # Get unique countries
    countries = run_query("SELECT DISTINCT country_name FROM Venues ORDER BY country_name")
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries['country_name'].tolist())

    # Build query based on filters
    query = """
    SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, c.complex_name, v.timezone
    FROM Venues v
    JOIN Complexes c ON v.complex_id = c.complex_id
    WHERE 1=1
    """

    if selected_country != "All":
        query += f" AND v.country_name = '{selected_country}'"

    venues = run_query(query)

    # Display venues
    st.write(f"Showing {len(venues)} venues")
    st.dataframe(venues)

    # Visualizations
    st.subheader("Venues Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Venues by country
        country_data = run_query("""
            SELECT country_name, COUNT(*) as count 
            FROM Venues 
            GROUP BY country_name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        fig = px.bar(country_data, x='country_name', y='count', color='count',
                    title="Top 10 Countries by Number of Venues")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Venues by complex
        complex_data = run_query("""
            SELECT c.complex_name, COUNT(v.venue_id) as count
            FROM Venues v
            JOIN Complexes c ON v.complex_id = c.complex_id
            GROUP BY c.complex_name
            ORDER BY count DESC
            LIMIT 10
        """)
        fig = px.bar(complex_data, x='complex_name', y='count',
                    title="Top 10 Complexes by Number of Venues")
        st.plotly_chart(fig, use_container_width=True)

    # Map of venues
    st.subheader("Venues Map")
    st.write("Note: This is a placeholder for a map visualization. In a real implementation, you would need to geocode the venues.")

# Competitors page
elif page == "Competitors":
    st.title("Tennis Competitors")

    # Filters
    st.sidebar.header("Filters")

    # Get unique countries
    countries = run_query("SELECT DISTINCT country FROM Competitors ORDER BY country")
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries['country'].tolist())

    # Rank range
    min_rank, max_rank = st.sidebar.slider("Rank Range", 1, 100, (1, 50))

    # Build query based on filters
    query = """
    SELECT c.name, c.country, c.country_code, cr.rank, cr.points, cr.movement, cr.competitions_played
    FROM Competitors c
    JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    WHERE cr.rank BETWEEN ? AND ?
    """

    params = [min_rank, max_rank]

    if selected_country != "All":
        query += " AND c.country = ?"
        params.append(selected_country)

    query += " ORDER BY cr.rank"

    # Execute query with parameters
    conn = get_connection()
    competitors = pd.read_sql_query(query, conn, params=params)

    # Display competitors
    st.write(f"Showing {len(competitors)} competitors")
    st.dataframe(competitors)

    # Visualizations
    st.subheader("Competitors Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Points vs Rank
        fig = px.scatter(competitors, x='rank', y='points', color='country',
                        hover_name='name', title="Points vs Rank")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Movement analysis
        movement_data = competitors.copy()
        movement_data['movement_type'] = movement_data['movement'].apply(
            lambda x: 'Up' if x > 0 else ('Down' if x < 0 else 'No Change')
        )
        movement_counts = movement_data['movement_type'].value_counts().reset_index()
        movement_counts.columns = ['movement_type', 'count']

        fig = px.pie(movement_counts, values='count', names='movement_type',
                    title="Rank Movement Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # Top 10 competitors
    st.subheader("Top 10 Competitors by Points")
    top_competitors = run_query("""
        SELECT c.name, c.country, cr.rank, cr.points
        FROM Competitors c
        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.points DESC
        LIMIT 10
    """)

    fig = px.bar(top_competitors, x='name', y='points', color='country',
                text='rank', title="Top 10 Competitors by Points")
    fig.update_traces(texttemplate='Rank: %{text}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# Search page
elif page == "Search":
    st.title("Search Tennis Data")

    search_type = st.radio("Search Type", ["Competitor", "Competition", "Venue"])
    search_term = st.text_input("Enter search term")

    if search_term:
        if search_type == "Competitor":
            results = run_query(f"""
                SELECT c.name, c.country, cr.rank, cr.points
                FROM Competitors c
                JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
                WHERE c.name LIKE '%{search_term}%'
                ORDER BY cr.rank
            """)

            if not results.empty:
                st.write(f"Found {len(results)} competitors matching '{search_term}'")
                st.dataframe(results)

                # Show details for first match
                if len(results) > 0:
                    st.subheader(f"Details for {results.iloc[0]['name']}")

                    competitor_name = results.iloc[0]['name']
                    competitor_details = run_query(f"""
                        SELECT c.name, c.country, c.country_code, c.abbreviation,
                               cr.rank, cr.points, cr.movement, cr.competitions_played
                        FROM Competitors c
                        JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
                        WHERE c.name = '{competitor_name}'
                    """)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Basic Information**")
                        st.write(f"Name: {competitor_details.iloc[0]['name']}")
                        st.write(f"Country: {competitor_details.iloc[0]['country']} ({competitor_details.iloc[0]['country_code']})")
                        st.write(f"Abbreviation: {competitor_details.iloc[0]['abbreviation']}")

                    with col2:
                        st.write("**Ranking Information**")
                        st.write(f"Current Rank: {competitor_details.iloc[0]['rank']}")
                        st.write(f"Points: {competitor_details.iloc[0]['points']}")
                        st.write(f"Movement: {competitor_details.iloc[0]['movement']}")
                        st.write(f"Competitions Played: {competitor_details.iloc[0]['competitions_played']}")
            else:
                st.warning(f"No competitors found matching '{search_term}'")

        elif search_type == "Competition":
            results = run_query(f"""
                SELECT c.competition_name, cat.category_name, c.type, c.gender
                FROM Competitions c
                JOIN Categories cat ON c.category_id = cat.category_id
                WHERE c.competition_name LIKE '%{search_term}%'
            """)

            if not results.empty:
                st.write(f"Found {len(results)} competitions matching '{search_term}'")
                st.dataframe(results)
            else:
                st.warning(f"No competitions found matching '{search_term}'")

        elif search_type == "Venue":
            results = run_query(f"""
                SELECT v.venue_name, v.city_name, v.country_name, c.complex_name
                FROM Venues v
                JOIN Complexes c ON v.complex_id = c.complex_id
                WHERE v.venue_name LIKE '%{search_term}%' OR v.city_name LIKE '%{search_term}%'
            """)

            if not results.empty:
                st.write(f"Found {len(results)} venues matching '{search_term}'")
                st.dataframe(results)
            else:
                st.warning(f"No venues found matching '{search_term}'")

# About page
elif page == "About":
    st.title("About Tennis Analytics")

    # Using markdown instead of multi-line string to avoid nested triple quotes
    st.markdown("""
    ## Game Analytics: Unlocking Tennis Data with SportRadar API

    This application provides comprehensive analytics for tennis data extracted from the SportRadar API.

    ### Features:

    - **Competition Analysis**: Explore tennis competitions, their categories, types, and gender distribution.
    - **Venue Exploration**: Discover tennis venues around the world and their associated complexes.
    - **Competitor Rankings**: Analyze player rankings, points, and performance metrics.
    - **Search Functionality**: Find specific competitors, competitions, or venues.
    """)

    st.markdown("""
    ### Data Sources:

    All data is sourced from the SportRadar API, which provides comprehensive sports data for various sports including tennis.
    """)

    st.markdown("""
    ### Technologies Used:

    - **Python**: Core programming language
    - **SQLite**: Database for storing and querying data
    - **Streamlit**: Web application framework
    - **Pandas**: Data manipulation and analysis
    - **Plotly**: Interactive data visualization
    """)

    st.markdown("""
    ### Project Information:

    This project was developed as part of a data analytics exercise to demonstrate skills in API integration, database management, and data visualization.
    """)

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Tennis Analytics Dashboard v1.0")
