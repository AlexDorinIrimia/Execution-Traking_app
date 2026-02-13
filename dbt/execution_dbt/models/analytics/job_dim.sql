SELECT DISTINCT
  job_name
FROM {{ ref('stg_executions') }}
