{% macro check_tables() %}
  {# FIX: the original defined q2 three times — the second definition silently
     overwrote the first, so the first SELECT (exact match on 'executions') was
     never executed. Consolidated into one clear query that searches for any
     table whose name contains 'exec'. Also removed the unreachable third q2
     block that appeared after the log loop. #}

  {% set q1 %}
    SELECT current_database() AS db, current_schema() AS schema;
  {% endset %}
  {% set r1 = run_query(q1) %}

  {% do log("=== Connection (db, schema) ===", info=True) %}
  {% for row in r1.rows %}
    {% do log(row[0] ~ " | " ~ row[1], info=True) %}
  {% endfor %}

  {% set q2 %}
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_name ILIKE '%exec%'
    ORDER BY table_schema, table_name;
  {% endset %}
  {% set r2 = run_query(q2) %}

  {% do log("=== Tables matching '%exec%' ===", info=True) %}
  {% if r2.rows | length == 0 %}
    {% do log("No tables matching '%exec%' found for this user.", info=True) %}
  {% else %}
    {% for row in r2.rows %}
      {% do log(row[0] ~ "." ~ row[1], info=True) %}
    {% endfor %}
  {% endif %}

  {% set q3 %}
    SELECT
      current_database()      AS db,
      current_user            AS "user",
      inet_server_addr()::text AS server_ip,
      inet_server_port()       AS server_port;
  {% endset %}
  {% set r3 = run_query(q3) %}
  {% do log("=== Server fingerprint ===", info=True) %}
  {% for row in r3.rows %}
    {% do log("db=" ~ row[0] ~ ", user=" ~ row[1] ~ ", ip=" ~ row[2] ~ ", port=" ~ row[3], info=True) %}
  {% endfor %}

{% endmacro %}
