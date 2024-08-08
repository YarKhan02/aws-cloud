from psycopg_pool import ConnectionPool

import os
import sys
import re

from flask import current_app as app

class Db:
  def __init__(self):
    self.init_pool()

  def init_pool(self):
    connection_url = os.getenv("CONNECTION_URL")
    self.pool = ConnectionPool(connection_url)

  def template(self, name):
    template_path = os.path.join(app.root_path, 'db', 'sql', name + '.sql')
    with open(template_path, 'r') as f:
      template_content = f.read()

    return template_content

  def query_commit(self, sql, params = {}):
    app.logger.debug('-==================-\n')
    app.logger.debug(params)
    pattern = r"\bRETURNING\b"
    is_returning_id = re.search(pattern, sql)
    try:
      with self.pool.connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        if is_returning_id:
          returning_id = cur.fetchone()[0]
        conn.commit()
        if is_returning_id:
          return returning_id
    except Exception as err:
      self.print_sql_err(err)
      # conn.rollback()

  def query_array(self, sql, params = {}):
    wrapped_sql = self.query_wrap_array(sql)
    with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(wrapped_sql, params)
          json = cur.fetchone()
          return json[0]

  def query_object(self, sql, params = {}):
    wrapped_sql = self.query_wrap_object(sql)
    with self.pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(wrapped_sql, params)
          json = cur.fetchone()
          return json[0]

  def query_wrap_object(self, template):
      sql = f"""
      (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
      {template}
      ) object_row);
      """

      return sql

  def query_wrap_array(self, template):
    sql = f"""
    (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
    {template}
    ) array_row);
    """
    
    return sql

  def print_sql_err(self, err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    # print ("\nextensions.Diagnostics:", err.diag)

    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")

db = Db()