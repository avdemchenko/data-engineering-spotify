import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery

# Page configuration
st.set_page_config(
    page_title="Spotify Music Analysis Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to improve the appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1DB954;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #1DB954;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .insight-text {
        font-size: 1.1rem;
        color: #191414;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h1 class='main-header'>Spotify Music Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Explore trends and patterns in Spotify music data across decades, genres, and audio features.")
st.markdown("---")

# Initialize BigQuery client using application default credentials
try:
    client = bigquery.Client(project="data-engineering-spotify")
    st.sidebar.success("✅ Connected to BigQuery using Application Default Credentials")
    connection_successful = True
except Exception as e:
    st.sidebar.error(f"Error connecting to BigQuery: {e}")
    st.sidebar.warning("Please run 'gcloud auth application-default login' in your terminal")
    connection_successful = False


# Function to run BigQuery queries
@st.cache_data(ttl=3600)
def run_query(query):
    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()


# Only proceed if connection is successful
if connection_successful:
    # Sidebar filters
    st.sidebar.header("Filters")

    # Get decades for filtering
    decades_query = """
    SELECT DISTINCT decade 
    FROM `data-engineering-spotify.dbt_spotify.spotify_music_analysis`
    WHERE decade IS NOT NULL
    ORDER BY decade
    """
    decades_df = run_query(decades_query)

    if not decades_df.empty:
        decades = decades_df['decade'].tolist()
        selected_decades = st.sidebar.multiselect(
            "Select Decades",
            decades,
            default=decades[:5] if len(decades) >= 5 else decades
        )

        # Fix the f-string issue by constructing the filter differently
        if selected_decades:
            quoted_decades = [f"'{d}'" for d in selected_decades]
            decades_filter = f"AND decade IN ({', '.join(quoted_decades)})"
        else:
            decades_filter = ""

        # Main dashboard content
        # 1. Decade Overview
        st.markdown("<h2 class='section-header'>Music Across Decades</h2>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        # Audio features by decade
        features_query = f"""
        SELECT 
            decade,
            AVG(danceability) as avg_danceability,
            AVG(energy) as avg_energy,
            AVG(valence) as avg_valence,
            AVG(acousticness) as avg_acousticness,
            COUNT(*) as track_count
        FROM `data-engineering-spotify.dbt_spotify.spotify_music_analysis`
        WHERE decade IS NOT NULL {decades_filter}
        GROUP BY decade
        ORDER BY decade
        """
        features_df = run_query(features_query)

        if not features_df.empty:
            with col1:
                # Convert to long format for plotly
                features_long = pd.melt(
                    features_df,
                    id_vars=['decade', 'track_count'],
                    value_vars=['avg_danceability', 'avg_energy', 'avg_valence', 'avg_acousticness'],
                    var_name='feature', value_name='value'
                )

                # Clean feature names
                features_long['feature'] = features_long['feature'].str.replace('avg_', '')

                # Create the line chart
                fig = px.line(
                    features_long,
                    x='decade',
                    y='value',
                    color='feature',
                    title="Audio Features Evolution Across Decades",
                    labels={'value': 'Average Value (0-1)', 'decade': 'Decade', 'feature': 'Audio Feature'},
                    markers=True,
                    line_shape='spline',
                    color_discrete_sequence=px.colors.qualitative.Set1
                )
                fig.update_layout(height=500, legend_title_text='Audio Feature')
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    "<p class='insight-text'>This chart shows how key audio features have evolved over the decades. Danceability, energy, and valence (positivity) reflect changing musical preferences and production techniques.</p>",
                    unsafe_allow_html=True)

            with col2:
                # Mood distribution by decade
                mood_query = f"""
                SELECT 
                    decade,
                    mood,
                    COUNT(*) as track_count
                FROM `data-engineering-spotify.dbt_spotify.spotify_music_analysis`
                WHERE decade IS NOT NULL {decades_filter}
                GROUP BY decade, mood
                ORDER BY decade, mood
                """
                mood_df = run_query(mood_query)

                if not mood_df.empty:
                    # Calculate percentage within each decade
                    mood_pivot = mood_df.pivot_table(
                        index='decade',
                        columns='mood',
                        values='track_count',
                        fill_value=0
                    )
                    mood_pivot_percent = mood_pivot.div(mood_pivot.sum(axis=1), axis=0) * 100

                    # Convert back to long format for plotting
                    mood_long = mood_pivot_percent.reset_index().melt(
                        id_vars=['decade'],
                        var_name='mood',
                        value_name='percentage'
                    )

                    # Create stacked bar chart
                    fig = px.bar(
                        mood_long,
                        x='decade',
                        y='percentage',
                        color='mood',
                        title="Mood Distribution by Decade",
                        labels={'percentage': 'Percentage of Tracks', 'decade': 'Decade', 'mood': 'Mood'},
                        color_discrete_map={'Happy': '#1DB954', 'Sad': '#191414', 'Ambivalent': '#CCCCCC'}
                    )
                    fig.update_layout(height=500, barmode='stack', legend_title_text='Mood')
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown(
                        "<p class='insight-text'>This chart shows the distribution of happy, sad, and ambivalent songs across decades, revealing shifting emotional tones in popular music.</p>",
                        unsafe_allow_html=True)

        # 2. Musical Key Analysis
        st.markdown("<h2 class='section-header'>Musical Key Insights</h2>", unsafe_allow_html=True)

        key_query = f"""
        SELECT 
            key_description,
            modality_description,
            COUNT(*) as track_count,
            AVG(valence) as avg_valence
        FROM `data-engineering-spotify.dbt_spotify.spotify_music_analysis`
        WHERE decade IS NOT NULL {decades_filter}
        GROUP BY key_description, modality_description
        ORDER BY track_count DESC
        """
        key_df = run_query(key_query)

        if not key_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                # Create combined key-modality labels and calculate percentages
                key_df['key_mode'] = key_df['key_description'] + ' ' + key_df['modality_description']
                key_df['percentage'] = key_df['track_count'] / key_df['track_count'].sum() * 100

                # Sort by track count
                key_df_sorted = key_df.sort_values(by='track_count', ascending=False)

                # Create horizontal bar chart for key distribution
                fig = px.bar(
                    key_df_sorted.head(12),  # Top 12 keys
                    x='percentage',
                    y='key_mode',
                    color='modality_description',
                    title="Most Popular Musical Keys",
                    labels={'percentage': 'Percentage of Tracks', 'key_mode': 'Musical Key',
                            'modality_description': 'Mode'},
                    color_discrete_map={'Major': '#1DB954', 'Minor': '#191414'},
                    orientation='h'
                )
                fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    "<p class='insight-text'>This chart shows the most commonly used musical keys in the dataset. The distribution reveals preferences for certain keys and modalities in popular music.</p>",
                    unsafe_allow_html=True)

            with col2:
                # Create a heatmap for valence (happiness) by key and mode
                pivot_df = key_df.pivot_table(
                    index='modality_description',
                    columns='key_description',
                    values='avg_valence',
                    fill_value=0
                )

                # Define the order of keys for the heatmap (circle of fifths)
                key_order = ['C', 'G', 'D', 'A', 'E', 'B', 'F#/Gb', 'C#/Db', 'G#/Ab', 'D#/Eb', 'A#/Bb', 'F']
                mode_order = ['Major', 'Minor']

                # Reindex to ensure correct order
                ordered_pivot = pivot_df.reindex(index=mode_order, columns=key_order)

                # Create the heatmap
                fig = px.imshow(
                    ordered_pivot,
                    x=ordered_pivot.columns,
                    y=ordered_pivot.index,
                    color_continuous_scale='Viridis',
                    title="Average 'Happiness' (Valence) by Musical Key",
                    labels=dict(x="Musical Key", y="Mode", color="Avg. Valence (0-1)")
                )

                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    "<p class='insight-text'>This heatmap reveals the average 'happiness' level (valence) of songs in different musical keys and modes. Traditionally, major keys are associated with happier emotional tones.</p>",
                    unsafe_allow_html=True)

        # 3. Explore correlations between audio features
        st.markdown("<h2 class='section-header'>Audio Feature Relationships</h2>", unsafe_allow_html=True)

        # Get a sample of tracks for scatter plot
        corr_query = f"""
        SELECT 
            danceability,
            energy,
            acousticness,
            valence,
            tempo/200 as tempo_scaled,  -- Scale tempo to 0-1 range (assuming max tempo around 200)
            mood
        FROM `data-engineering-spotify.dbt_spotify.spotify_music_analysis`
        WHERE decade IS NOT NULL {decades_filter}
        ORDER BY RAND()
        LIMIT 5000
        """
        corr_df = run_query(corr_query)

        if not corr_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                # Create correlation matrix heatmap
                corr_matrix = corr_df[['danceability', 'energy', 'acousticness', 'valence', 'tempo_scaled']].corr()

                # Plot correlation matrix
                fig = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    color_continuous_scale='RdBu_r',
                    title="Correlation Between Audio Features",
                    range_color=[-1, 1]
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    "<p class='insight-text'>This correlation matrix shows relationships between different audio features. Strong positive correlations appear in dark blue, while negative correlations appear in dark red.</p>",
                    unsafe_allow_html=True)

            with col2:
                # Feature selection for scatter plot
                x_feature = st.selectbox("X-axis feature",
                                         ['energy', 'danceability', 'acousticness', 'valence', 'tempo_scaled'], index=0)
                y_feature = st.selectbox("Y-axis feature",
                                         ['danceability', 'energy', 'acousticness', 'valence', 'tempo_scaled'], index=1)

                # Create scatter plot
                fig = px.scatter(
                    corr_df,
                    x=x_feature,
                    y=y_feature,
                    color='mood',
                    title=f"Relationship: {x_feature.capitalize()} vs {y_feature.capitalize()}",
                    labels={
                        x_feature: x_feature.capitalize().replace('_scaled', ' (scaled)'),
                        y_feature: y_feature.capitalize().replace('_scaled', ' (scaled)'),
                        'mood': 'Mood'
                    },
                    opacity=0.7,
                    color_discrete_map={'Happy': '#1DB954', 'Sad': '#191414', 'Ambivalent': '#CCCCCC'}
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    "<p class='insight-text'>This scatter plot allows you to explore relationships between different audio features. The color represents the mood classification based on valence.</p>",
                    unsafe_allow_html=True)

        # 4. Additional insights section
        st.markdown("<h2 class='section-header'>Additional Insights</h2>", unsafe_allow_html=True)

        # Query to get top artists by decade
        artist_query = f"""
        SELECT 
            decade,
            primary_artist,
            COUNT(*) as track_count,
            AVG(danceability) as avg_danceability,
            AVG(energy) as avg_energy,
            AVG(valence) as avg_valence
        FROM `data-engineering-spotify.dbt_spotify.spotify_music_analysis`
        WHERE decade IS NOT NULL {decades_filter}
        GROUP BY decade, primary_artist
        HAVING COUNT(*) > 5  -- Only include artists with more than 5 tracks
        ORDER BY decade, track_count DESC
        """
        artist_df = run_query(artist_query)

        if not artist_df.empty:
            # Create a dataframe with top 3 artists per decade
            top_artists = artist_df.groupby('decade').apply(lambda x: x.nlargest(3, 'track_count')).reset_index(
                drop=True)

            col1, col2 = st.columns(2)

            with col1:
                # Top artists by decade table
                st.subheader("Top Artists by Decade")

                # Format the table for display
                display_df = top_artists[['decade', 'primary_artist', 'track_count']].copy()
                display_df.columns = ['Decade', 'Artist', 'Number of Tracks']

                # Display as a styled table
                st.dataframe(
                    display_df,
                    column_config={
                        "Decade": st.column_config.TextColumn("Decade"),
                        "Artist": st.column_config.TextColumn("Artist"),
                        "Number of Tracks": st.column_config.NumberColumn("Number of Tracks")
                    },
                    hide_index=True,
                    use_container_width=True
                )

            with col2:
                # Create a chart showing audio features for top artists in the selected decades
                selected_decade = st.selectbox(
                    "Select decade for artist comparison",
                    sorted(top_artists['decade'].unique())
                )

                decade_artists = top_artists[top_artists['decade'] == selected_decade].copy()

                # Prepare data for radar chart
                artists = decade_artists['primary_artist'].tolist()
                fig = go.Figure()

                for i, artist in enumerate(artists):
                    artist_data = decade_artists[decade_artists['primary_artist'] == artist].iloc[0]

                    fig.add_trace(go.Scatterpolar(
                        r=[
                            artist_data['avg_danceability'],
                            artist_data['avg_energy'],
                            artist_data['avg_valence'],
                            artist_data['track_count'] / max(decade_artists['track_count'])  # Normalize
                        ],
                        theta=['Danceability', 'Energy', 'Valence', 'Popularity'],
                        fill='toself',
                        name=artist
                    ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    title=f"Artist Comparison in {selected_decade}",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    "<p class='insight-text'>This radar chart compares the musical characteristics of top artists from the selected decade.</p>",
                    unsafe_allow_html=True)

        # Footer with data info
        st.markdown("---")
        st.caption("Data source: Spotify tracks dataset from BigQuery | Analyzed using dbt and Streamlit")

    else:
        st.error("Error fetching decade data from BigQuery. Please check your connection and dataset.")
else:
    st.error("Please set up authentication to proceed.")
    st.info("Run 'gcloud auth application-default login' in your terminal, then restart this app.")

    # Authentication instructions
    st.markdown("""
    ## Authentication Instructions

    To authenticate with Google Cloud and access your BigQuery data, follow these steps:

    1. Open a terminal or command prompt
    2. Run the following command:
       ```
       gcloud auth application-default login
       ```
    3. A browser window will open. Log in with your Google account that has access to the BigQuery dataset
    4. After successful authentication, close the browser and return to the terminal
    5. Restart this Streamlit app

    This will create application default credentials that the app can use to connect to BigQuery.
    """)