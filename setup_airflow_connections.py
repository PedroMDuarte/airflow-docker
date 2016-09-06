#!/usr/bin/env python
import argparse
import sys
from collections import namedtuple

from airflow import settings
from sqlalchemy import MetaData, create_engine, Table, select, delete
from sqlalchemy.exc import OperationalError

description = """This script will add the necessary connections into the
airflow database. For more info on the connections take a look at
`docs/Connections.md`
"""

AIRFLOW_DB = settings.SQL_ALCHEMY_CONN

parser = argparse.ArgumentParser(
    prog='bin/setup_airflow_connections.py',
    description=description
)

parser.add_argument('--hm', action='store_true', default=False,
                    help='Select `hadoop-master` as the Hive server. ' +
                    'Default server is `cdh`.')

parser.add_argument('--schema', type=str, default='default',
                    help='Hive schema that will be used by airflow hooks. ' +
                    'Default schema is `default`.')

parser.add_argument('--dev', action='store_true', default=False,
                    help='Select `dev` as the MSSQL database. ' +
                    'Default MSSQL database is `pipeline`.')

parser.add_argument('--dev2', action='store_true', default=False,
                    help='Select `dev2` as the MSSQL database. ' +
                    'Default MSSQL database is `pipeline`.')

args = parser.parse_args()


# ------------------------
# Pretty print connections
# ------------------------

def show_existing_connections(details=False):
    print
    print '\t', '=' * 60
    print '\tAIRFLOW CONNECTION ENTRIES %s' % ('(DETAILS)' if details else '')
    print '\t', '=' * 60

    s = select([conn_table])
    results = engine.execute(s).fetchall()

    if not details:
        for r in results:
            print '\t', r.conn_id

    else:
        for r in results:
            print '-' * 40
            print '{} : {}'.format('conn_id', r.conn_id)
            print '{} : {}'.format('conn_type', r.conn_type)
            print '{} : {}'.format('host', r.host)
            print '{} : {}'.format('schema', r.schema)
            print '{} : {}'.format('login', r.login)
            print '{} : {}'.format('password', r.password)
            print '{} : {}'.format('port', r.port)
            print '{} : {}'.format('extra', r.extra)
            print

    print


# -------------------------------------------------
# Setup connections according to command line flags
# -------------------------------------------------

Conn = namedtuple('Conn', ['conn_id', 'conn_type', 'host', 'schema',
                           'login', 'password', 'port', 'extra'])

hive = Conn(
    conn_id='hiveserver2_default',
    conn_type='hiveserver2',
    host='hadoop-master.dev.internal.getaltx.com' if args.hm else 'cdh',
    schema=args.schema,
    login='hive',
    password=None,
    port=10000,
    extra=None)

mssql = {
    'conn_id': 'mssql_default',
    'conn_type': 'mssql',
    'host': 'sql.pipeline.internal.getaltx.com',
    'schema': None,
    'login': 'altx_ingestion',
    'password': '2332ssis',
    'port': 1433,
    'extra': '{"database": "Altx_Main"}'
}

if args.dev2 and args.dev:
    raise ValueError("`--dev` and `--dev2` flags are in conflict.")

if args.dev:
    mssql.update({
        'host': 'sql.dev.internal.getaltx.com',
        'login': 'altx_ingestion',
        'password': '2332ssis'
    })

elif args.dev2:
    mssql.update({
        'host': 'sql.dev2.internal.getaltx.com',
        'login': 'altx_ingestion',
        'password': '2332ssis'
    })

mssql = Conn(**mssql)


# -------------------
# Connect to database
# -------------------

print "\n\tUsing airflow database at %s ..." % AIRFLOW_DB

metadata = MetaData()
engine = create_engine(AIRFLOW_DB, echo=False)

try:
    conn_table = Table('connection', metadata, autoload=True,
                       autoload_with=engine)
except OperationalError:
    print "Unable to open database."
    sys.exit()

VERBOSE = False

if VERBOSE:
    show_existing_connections()


# -----------------------------
# Delete unnecesary connections
# -----------------------------

unnecessary = [
    'airflow_ci',
    'bigquery_default',
    'beeline_default',
    'presto_default',
    'hive_cli_default',
    'local_mysql',
    'metastore_default',
    'mysql_default',
    'postgres_default',
    'sqlite_default',
    'http_default',
    'vertica_default',
    'webhdfs_default',
    'bigquery_default'
]

will_be_recreated = [
    'airflow_db',
    'hiveserver2_default',
    'hdfs_default',
    'mongo_default',
    'mssql_RAW_ADV',
    'mssql_AltxStaging_New',
    'mssql_default',
]

to_delete = unnecessary + will_be_recreated

d = delete(conn_table).where(conn_table.c.conn_id.in_(to_delete))
result = engine.execute(d)
print "\tDeleted {:d} connections.".format(result.rowcount)
if VERBOSE:
    show_existing_connections()


# ---------------------------
# Insert pipeline connections
# ---------------------------

airflow = Conn(
    conn_id='airflow_db',
    conn_type='Postgres',
    host='airflow-postgres',
    schema='airflow',
    login='airflow',
    password='airflow',
    port=5432,
    extra=None)

hdfs = Conn(
    conn_id='hdfs_default',
    conn_type='hdfs',
    host=hive.host,
    schema=None,
    login='hdfs',
    password=None,
    port=8020,
    extra=None)


mssql_RAW_ADV = Conn(
    conn_id='mssql_RAW_ADV',
    conn_type='mssql',
    host='ingestion.internal.getaltx.com',
    schema='RAW_ADV',
    login='altx',
    password='Sw6QN8A37P3HF7U',
    port=1433,
    extra=None)

mssql_AltxStaging_New = mssql_RAW_ADV._replace(conn_id='mssql_AltxStaging_New')

mongo = Conn(
    conn_id='mongo_default',
    conn_type=None,
    host='mongo',
    schema='default',
    login=None,
    password=None,
    port=None,
    extra=None)


all_connnections = map(lambda x: x._asdict(),
                       [airflow, hdfs, hive, mssql, mssql_RAW_ADV,
                        mssql_AltxStaging_New, mongo])

result = engine.execute(conn_table.insert(), all_connnections)

print "\tInserted {:d} connections.\n".format(result.rowcount)

print '\tHadoop filesystem host        :', hive.host
print '\tHiveServer connection host    :', hive.host
print '\tHiveServer connection schema  :', args.schema
print '\tMSSQL host                    :', mssql.host

show_existing_connections()
if VERBOSE:
    show_existing_connections(details=True)
