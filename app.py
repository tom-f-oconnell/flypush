#!/usr/bin/env python3

"""
"""

import socket

from flask import Flask
from flask import render_template
#import psycopg2 as pg
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)
#url = 'postgresql+psycopg2://flypush:flypush@localhost:5432/flypush'
url = 'postgresql+psycopg2://flypush:flypush@localhost:5432/flypush'
conn = create_engine(url)

class Table:
    def __init__(self, name, separate_history=False):
        self.name = name
        #self.separate_history = separate_history
        self.url = name

    # TODO make this an attribute .pretty_name or something?
    # and use this for html? separate magic for that?
    def __str__(self):
        return pretty_name(self.name)

    # do i want these objects to actually have data of table?

    #def has_separate_history(

def get_tables():
    tables = conn.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema') AND
        table_schema NOT LIKE 'pg_toast%%'""")
    # TODO what is type of output here?
    tables = [t[0] for t in tables]
    # TODO handle tables w/ extra <table_name>_history table differently
    # (want view as one table, not two?)
    # TODO TODO find tables with history by finding tables w/ primary key as
    # timestamp[tz(0)], that references another table w/ NOT NULL constraint on
    # reference
    return [Table(t) for t in tables if '_history' not in t]

def pretty_name(table_name):
    return table_name.capitalize().replace('_', ' ')

@app.route('/')
def index():
    tables = get_tables()
    return render_template('index.html',
        host=socket.gethostname(),
        tables=tables
    )

# TODO nice way to round up a bunch of nice labels for routes / fns, to use in
# nav, dynamically?

# TODO 404 for wrong tablename
@app.route('/<table_name>')
def render_table(table_name):
    tables = get_tables()
    # TODO TODO only render stuff owned by current user (default to showing
    # all?)
    # TODO explicitly check valid tablename first?
    # could also use sqlalchemy and pd.read_sql_table(table, engine)
    df = pd.read_sql_table(table_name, con=conn)
    # TODO 404 if df is empty (but w/ different message?) (at least show cols?)
    print(table_name)
    print(df)
    return render_template('table.html', tables=tables, table=df.to_html())

# TODO make another helper function for tables where there is a separate
# history table

# TODO checkbox to show historical data for things like boxes, and maybe
# otherwise only show most recent info?

'''
@app.route('/<name>')
def lab_member(name):
    return render_template('lab_member.html', name=name)
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
