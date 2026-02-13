{% macro list_dbs() %}
  {% set q %}
    select datname
    from pg_database
    where datistemplate = false
    order by datname;
  {% endset %}
  {% set r = run_query(q) %}
  {% do log("=== Databases visible ===", info=True) %}
  {% for row in r.rows %}
    {% do log(row[0], info=True) %}
  {% endfor %}
{% endmacro %}
