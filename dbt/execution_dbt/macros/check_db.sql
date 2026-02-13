{% macro check_db() %}

  {% set q1 %}
    select current_database() as db, current_user as usr;
  {% endset %}
  {% set r1 = run_query(q1) %}
  {% do log("=== Who/Where ===", info=True) %}
  {% for row in r1.rows %}
    {% do log("db=" ~ row[0] ~ ", user=" ~ row[1], info=True) %}
  {% endfor %}

  {% set q2 %}
    select schema_name
    from information_schema.schemata
    order by schema_name;
  {% endset %}
  {% set r2 = run_query(q2) %}
  {% do log("=== Schemas visible ===", info=True) %}
  {% for row in r2.rows %}
    {% do log(row[0], info=True) %}
  {% endfor %}

  {% set q3 %}
    select table_schema, table_name
    from information_schema.tables
    where table_schema not in ('pg_catalog','information_schema')
    order by table_schema, table_name
    limit 200;
  {% endset %}
  {% set r3 = run_query(q3) %}
  {% do log("=== First 200 tables visible ===", info=True) %}
  {% if r3.rows | length == 0 %}
    {% do log("No non-system tables visible to this user.", info=True) %}
  {% else %}
    {% for row in r3.rows %}
      {% do log(row[0] ~ "." ~ row[1], info=True) %}
    {% endfor %}
  {% endif %}

{% endmacro %}
