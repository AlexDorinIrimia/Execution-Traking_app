{% macro check_tables() %}

  {% set q1 %}
    select current_database() as db, current_schema() as schema;
  {% endset %}
  {% set r1 = run_query(q1) %}

  {% do log("=== Connection (db, schema) ===", info=True) %}
  {% for row in r1.rows %}
    {% do log(row[0] ~ " | " ~ row[1], info=True) %}
  {% endfor %}

  {% set q2 %}
    select table_schema, table_name
    from information_schema.tables
    where table_name ilike 'executions'
    order by table_schema, table_name;
  {% endset %}

     {% set q2 %}
  select table_schema, table_name
  from information_schema.tables
  where table_name ilike '%exec%'
  order by table_schema, table_name;
{% endset %}

  {% set r2 = run_query(q2) %}

  {% do log("=== Tables matching 'executions' ===", info=True) %}
  {% if r2.rows | length == 0 %}
    {% do log("No tables named 'executions' found in this database (for this user).", info=True) %}
  {% else %}
    {% for row in r2.rows %}
      {% do log(row[0] ~ "." ~ row[1], info=True) %}
    {% endfor %}
  {% endif %}

  {% set q2 %}
  select table_schema, table_name
  from information_schema.tables
  where table_name ilike '%exec%'
  order by table_schema, table_name;
{% endset %}

{% set q3 %}
  select
    current_database() as db,
    current_user as user,
    inet_server_addr()::text as server_ip,
    inet_server_port() as server_port;
{% endset %}
{% set r3 = run_query(q3) %}
{% do log("=== Server fingerprint ===", info=True) %}
{% for row in r3.rows %}
  {% do log("db=" ~ row[0] ~ ", user=" ~ row[1] ~ ", ip=" ~ row[2] ~ ", port=" ~ row[3], info=True) %}
{% endfor %}


{% endmacro %}
