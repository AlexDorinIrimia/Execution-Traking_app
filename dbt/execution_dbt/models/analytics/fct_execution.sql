SELECT
  execution_id,
  job_name,
  run_id,
  status,
  start_time,
  end_time,
  created_at,
  duration_seconds
FROM {{ ref('stg_executions') }}
