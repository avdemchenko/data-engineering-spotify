{{
  config(
    materialized = 'table',
    description = 'Enriched Spotify tracks with musical key descriptions, decade categorization, and mood analysis'
  )
}}

SELECT 
    -- identifiers
    name,
    album,
    artists,
    explicit,
    song_id,
    -- audio features
    danceability,
    energy,
    {{ get_key_description('key') }} AS key_description, 
    loudness,
    {{ get_modality_description('mode') }} AS modality_description, 
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    valence,
    tempo,
    duration_s,
    -- time features
    year AS release_year,
    release_date,
    primary_artist,
    -- existing computed fields
    decade,
    -- new computed fields: mood based on valence
    CASE
        WHEN valence > 0.5 THEN 'Happy'
        WHEN valence < 0.5 THEN 'Sad'
        ELSE 'Ambivalent'
    END AS mood
FROM {{ source('spotify', 'cleaned_tracks_features') }}