{{
    config(
        materialized='table'
    )
}}

{{ read_zipcode_csv('data/utf_ken_all.csv') }}
