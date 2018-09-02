#!/usr/bin/env python3

"""
"""

import socket

from flask import Flask
from flask import render_template, abort
#import psycopg2 as pg
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)
url = 'postgresql+psycopg2://flypush:flypush@localhost:5432/flypush'
conn = create_engine(url)

class Table:
    def __init__(self, name):
        self.name = name
        self.url = name

    # TODO make this an attribute .pretty_name or something?
    # and use this for html? separate magic for that?
    def __str__(self):
        return pretty_name(self.name)

def list_tables():
    tables = conn.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema') AND
        table_schema NOT LIKE 'pg_toast%%'""")
    tables = [t[0] for t in tables]
    # TODO handle tables w/ extra <table_name>_history table differently
    # (want view as one table, not two?)
    # TODO TODO find tables with history by finding tables w/ primary key as
    # timestamp[tz(0)], that references another table w/ NOT NULL constraint on
    # reference
    return [Table(t) for t in tables]

def pretty_name(table_name):
    return table_name.capitalize().replace('_', ' ')

@app.route('/')
def index():
    tables = list_tables()
    simple_tables = [t for t in tables if '_history' not in t.name]
    return render_template('index.html',
        host=socket.gethostname(),
        tables=simple_tables
    )

def get_table(table_name):
    """Returns DataFrame for data in SQL table table_name.

    For case where table is table describing static objects, with associated
    history table, the two tables are joined.
    """
    # TODO restrict these queries to (relevance to) table_name?
    ref_q = '''
    SELECT
        tc.table_name as history_table,
        ccu.table_name as static_table,
        kcu.column_name

    FROM
      information_schema.table_constraints tc
      JOIN information_schema.constraint_column_usage AS ccu
	USING (constraint_schema, constraint_name)
      JOIN information_schema.columns AS c
	ON c.table_schema = tc.constraint_schema
	AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
      JOIN information_schema.key_column_usage AS kcu
	ON tc.constraint_name = kcu.constraint_name
	AND tc.table_schema = kcu.table_schema

    WHERE ccu.table_name = '{}'
      AND kcu.column_name = ccu.column_name
      AND constraint_type = 'FOREIGN KEY' AND is_nullable = 'NO'
    '''.format(table_name)
    # TODO just get out history_table field for input to second sql statement
    rows = list(conn.execute(ref_q))
    candidates = [r[0] for r in rows]
    print('Q1 results:')
    print(rows)
    print(candidates)
    for c in candidates:
        print(c)
        print(type(c))

    if len(candidates) == 0:
        return pd.read_sql_table(table_name, con=conn)

    pk_q = '''
    SELECT COUNT(*)
    FROM
      information_schema.table_constraints tc
      JOIN information_schema.constraint_column_usage AS ccu
      USING (constraint_schema, constraint_name) JOIN information_schema.columns
      AS c ON c.table_schema = tc.constraint_schema
      AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
    WHERE data_type = 'timestamp with time zone'
      AND constraint_type = 'PRIMARY KEY'
      AND tc.table_name {};
    '''.format('in {}'.format(tuple(candidates)) if len(candidates) > 1 else
        "= '{}'".format(candidates[0]))

    # will this fail in some cases? more idiomatic way to get count?
    count = list(conn.execute(pk_q))[0][0]
    if count == 0:
        return pd.read_sql_table(table_name, con=conn)

    assert len(rows) == 1
    static_table = rows[0][1]
    history_table = rows[0][0]
    common_id_col = rows[0][2]

    # TODO make sure this join is what I want, once I get actual data
    join_q = 'SELECT * FROM {} JOIN {} USING ({})'.format(
        static_table, history_table, common_id_col)
    return pd.read_sql_query(join_q, con=conn)

        
@app.route('/<table_name>')
def render_table(table_name):
    tables = list_tables()
    if table_name not in [t.name for t in tables]:
        # TODO how to add message to 404?
        abort(404)

    simple_tables = [t for t in tables if '_history' not in t.name]

    df = get_table(table_name)
    # TODO TODO only render stuff owned by current user (default to showing

    return render_template('table.html', host=socket.gethostname(),
        tables=simple_tables, table=df.to_html())

# TODO checkbox to show historical data for things like boxes, and maybe
# otherwise only show most recent info?

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
