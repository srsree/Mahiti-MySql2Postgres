========================================================================================
mysql2postgres - A tool for migrating/converting/exporting data from MySQL to PostgreSQL
========================================================================================

This tool allows you to take data from a MySQL server (tested on 5.x and later) and write a PostgreSQL-compatible (8.2 or higher) dump file, or pipe it directly into your running PostgreSQL server (8.2 or higher).

.. attention::
   Currently there is no support for importing `spatial data from MySQL
   <http://dev.mysql.com/doc/refman/5.5/en/spatial-extensions.html>`_.


Installation:
=============

It is recommended to use a virtual environment for installation.

::

    python3 -m venv ~/envs/mysql2postgres
    source ~/envs/mysql2postgres/bin/activate
    pip install -r requirements.txt

Or install directly from PyPI:

::

    pip install mysql2postgres


Requirements:
-------------

* Python 3.6+
* `mysqlclient <https://pypi.org/project/mysqlclient/>`_ (Python 3 fork of MySQLdb) (optional, required for direct MySQL connection)
* `psycopg2 <https://pypi.org/project/psycopg2/>`_ (optional, required for direct PostgreSQL connection)
* `PyYAML <https://pypi.org/project/PyYAML/>`_
* `termcolor <https://pypi.org/project/termcolor/>`_ (unless you're installing on Windows)
* `pytz <https://pypi.org/project/pytz/>`_


On Windows
----------

You can install `mysqlclient` and `psycopg2` using pre-built wheels from PyPI. Make sure you have the appropriate build tools or use wheels for your Python version.

::

    pip install mysqlclient psycopg2


From source:
------------

::

    git clone https://github.com/philipsoutham/py-mysql2pgsql.git
    cd py-mysql2pgsql
    pip install .


Usage:
======

Looking for help?

::

    mysql2postgres -h
    usage: mysql2postgres [-h] [-v] [-f FILE]

    Tool for migrating/converting data from mysql to postgresql.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Show progress of data migration.
      -f FILE, --file FILE  Location of configuration file (default:
                            mysql2postgres.yml). If none exists at that path,
                            one will be created for you.


Don't worry if this is your first time, it'll be gentle.

::

    mysql2postgres
    No configuration file found.
    A new file has been initialized at: mysql2postgres.yml
    Please review the configuration and retry...

As the output suggests, a file was created at mysql2postgres.yml for you
to edit. For the impatient, here is what the file contains.

::

    # a socket connection will be selected if a 'socket' is specified
    # also 'localhost' is a special 'hostname' for MySQL that overrides the 'port' option
    # and forces it to use a local socket connection
    # if tcp is chosen, you can use compression

    mysql:
     hostname: localhost
     port: 3306
     socket: /tmp/mysql.sock
     username: mysql2psql
     password: 
     database: mysql2psql_test
     compress: false
    destination:
     # if file is given, output goes to file, else postgres
     file: 
     postgres:
      hostname: localhost
      port: 5432
      username: mysql2psql
      password: 
      database: mysql2psql_test

    # if only_tables is given, only the listed tables will be converted.  leave empty to convert all tables.
    #only_tables:
    #- table1
    #- table2
    # if exclude_tables is given, exclude the listed tables from the conversion.
    #exclude_tables:
    #- table3
    #- table4

    # if supress_data is true, only the schema definition will be exported/migrated, and not the data
    supress_data: false

    # if supress_ddl is true, only the data will be exported/imported, and not the schema
    supress_ddl: false

    # if force_truncate is true, forces a table truncate before table loading
    force_truncate: false

    # if timezone is true, forces to append/convert to UTC tzinfo mysql data
    timezone: false
    
    # if index_prefix is given, indexes will be created whith a name prefixed with index_prefix
    index_prefix:

Pretty self explanatory right? A couple things to note, first if
`destination -> file` is populated all output will be dumped to the
specified location regardless of what is contained in `destination ->
postgres`. So if you want to dump directly to your server make sure
the `file` value is blank.

Say you have a MySQL db with many, many tables, but you're only
interested in exporting a subset of those table, no problem. Add only
the tables you want to include in `only_tables` or tables that you
don't want exported to `exclude_tables`. 

Other items of interest may be to skip moving the data and just create
the schema or vice versa. To skip the data and only create the schema
set `supress_data` to `true`. To migrate only data and not recreate the
tables set `supress_ddl` to `true`; if there's existing data that you
want to drop before importing set `force_truncate` to
`true`. `force_truncate` is not necessary when `supress_ddl` is set to
`false`.

Note that when migrating, it's sometimes possible to knock your 
sequences out of whack. When this happens, you may get IntegrityErrors 
about your primary keys saying things like, "duplicate key value violates 
unique constraint." See `this page <https://wiki.postgresql.org/wiki/Fixing_Sequences>`_ for a fix

Due to different naming conventions in mysql an postgresql, there is a chance
that the tool generates index names that collide with table names. This can
be circumvented by setting index_prefix.

One last thing, the `--verbose` flag. Without it the tool will just go
on it's merry way without bothering you with any output until it's
done. With it you'll get a play-by-play summary of what's going
on. Here's an example.

::

    mysql2postgres -v -f mysql2postgres.yml
    START PROCESSING table_one
      START  - CREATING TABLE table_one
      FINISH - CREATING TABLE table_one
      START  - WRITING DATA TO table_one
      24812.02 rows/sec [20000]  
      FINISH - WRITING DATA TO table_one
      START  - ADDING INDEXES TO table_one
      FINISH - ADDING INDEXES TO table_one
      START  - ADDING CONSTRAINTS ON table_one
      FINISH - ADDING CONSTRAINTS ON table_one
    FINISHED PROCESSING table_one

    START PROCESSING table_two
      START  - CREATING TABLE table_two
      FINISH - CREATING TABLE table_two
      START  - WRITING DATA TO table_two

      FINISH - WRITING DATA TO table_two
      START  - ADDING INDEXES TO table_two
      FINISH - ADDING INDEXES TO table_two
      START  - ADDING CONSTRAINTS ON table_two
      FINISH - ADDING CONSTRAINTS ON table_two
    FINISHED PROCESSING table_two


Data Type Conversion Legend
===========================

Since there is not a one-to-one mapping between MySQL and
PostgreSQL data types, listed below are the conversions that are applied. I've
taken some liberties with some, others should come as no surprise.

==================== ===========================================
MySQL                PostgreSQL
==================== ===========================================
char                 character
varchar              character varying
tinytext             text
mediumtext           text
text                 text
longtext             text
tinyblob             bytea
mediumblob           bytea
blob                 bytea
longblob             bytea
binary               bytea
varbinary            bytea
bit                  bit varying
tinyint              smallint
tinyint unsigned     smallint
smallint             smallint
smallint unsigned    integer
mediumint            integer
mediumint unsigned   integer
int                  integer
int unsigned         bigint
bigint               bigint
bigint unsigned      numeric
float                real
float unsigned       real
double               double precision
double unsigned      double precision
decimal              numeric
decimal unsigned     numeric
numeric              numeric
numeric unsigned     numeric
date                 date
datetime             timestamp without time zone
time                 time without time zone
timestamp            timestamp without time zone
year                 smallint
enum                 character varying (with `check` constraint)
set                  ARRAY[]::text[]
==================== ===========================================


Conversion caveats:
===================

Not just any valid MySQL database schema can be simply converted to the
PostgreSQL. So when you end with a different database schema please note that:

* Most MySQL versions don't enforce `NOT NULL` constraint on `date` and `enum`
  fields. Because of that `NOT NULL` is skipped for this types. Here's an
  excuse for the dates: `<http://bugs.mysql.com/bug.php?id=59526>`_.

About:
======

I ported much of this from an existing project written in Ruby by Max
Lapshin over at `<https://github.com/maxlapshin/mysql2postgres>`_. I
found that it worked fine for most things, but for migrating large tables
with millions of rows it started to break down. This motivated me to
write *mysql2postgres* which uses a server side cursor, so there is no "paging"
which means there is no slow down while working it's way through a
large dataset.

New Feature: Convert from MySQL Dump File
========================================

You can now convert a MySQL SQL backup file directly to a PostgreSQL-compatible SQL file, without needing access to a live MySQL database.

To use this feature, add the following to your config under the 'mysql' section:

.. code-block:: yaml

    mysql:
      dump_file: /path/to/your/mysql_dump.sql

If 'dump_file' is specified, the tool will parse the dump file and convert its schema and data to PostgreSQL format. All other options under 'mysql' are ignored in this mode.

Optional Dependencies and Modes
------------------------------

- If `mysqlclient` (MySQLdb) is **not installed**, you can only use a MySQL dump file as input (see the `dump_file` option in the config). Direct connection to a MySQL server will not be available.
- If `psycopg2` is **not installed**, you can only output to a PostgreSQL-compatible SQL file. Direct connection to a PostgreSQL server will not be available.
- If you attempt to use a database source or destination without the required library, the tool will print a clear error and exit.

Typical error messages:
- "MySQLdb (mysqlclient) is not installed. Only dump_file input is supported."
- "psycopg2 is not installed. Only file output is supported."
