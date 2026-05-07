-- FIX: the original file had newlines *inside* column aliases, e.g.:
--
--   id::bigint AS
--   execution_id,
--
-- This is invalid SQL and causes a parse error in both dbt and raw Postgres.
-- All AS clauses are now on the same line as their expression.

WITH src AS (
    SELECT * FROM {{ source('raw', 'executions') }}
),

clean AS (
    SELECT
        id::bigint                                            AS execution_id,
        job_name::text                                        AS job_name,
        run_id::text                                          AS run_id,
        lower(status)::text                                   AS status,
        start_time::timestamp                                 AS start_time,
        end_time::timestamp                                   AS end_time,
        created_at::timestamp                                 AS created_at,
        extract(epoch FROM (end_time - start_time))::numeric  AS duration_seconds
    FROM src
)

SELECT * FROM clean
