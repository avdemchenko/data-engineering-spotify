{% macro get_key_description(key_column) %}
    CASE {{ key_column }}
        WHEN 0 THEN 'C'
        WHEN 1 THEN 'C#/Db'
        WHEN 2 THEN 'D'
        WHEN 3 THEN 'D#/Eb'
        WHEN 4 THEN 'E'
        WHEN 5 THEN 'F'
        WHEN 6 THEN 'F#/Gb'
        WHEN 7 THEN 'G'
        WHEN 8 THEN 'G#/Ab'
        WHEN 9 THEN 'A'
        WHEN 10 THEN 'A#/Bb'
        WHEN 11 THEN 'B'
        ELSE 'Unknown'
    END
{% endmacro %}

{% macro get_modality_description(mode_column) %}
    CASE {{ mode_column }}
        WHEN 0 THEN 'Minor'
        WHEN 1 THEN 'Major'
        ELSE 'Unknown'
    END
{% endmacro %}
