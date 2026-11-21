
{{ config(materialized='view') }}

WITH source AS (
    SELECT *
    FROM read_json_auto(
        's3://spotify-data-engineering-334116998170-us-east-2/bronze/artists/artists.json'
    )
),

artists AS (
    SELECT
        search_term,
        unnest(response.artists.items) AS artist
    FROM source
),

classified AS (
    SELECT
        artist.id AS artist_id,
        artist.name AS artist_name,
        artist.type AS artist_type,
        artist.uri AS artist_uri,
        artist.href AS artist_href,
        artist.external_urls.spotify AS spotify_url,
        search_term,

        CASE
            WHEN artist.id IN (
                '5M52tdBnJaKSvOpJGz8mfZ',
                '5eXLaFqz3RMCHW61WiXpqY',
                '0epOFNiUfyON9EYx7Tpr6V'
            )
            THEN TRUE
            ELSE FALSE
        END AS is_main_artist

    FROM artists
    WHERE artist.id IS NOT NULL
)

SELECT *
FROM classified
