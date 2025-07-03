import codecs

from .lib import print_red
try:
    from .lib.mysql_reader import MysqlReader
    MYSQLDB_AVAILABLE = True
except ImportError:
    MYSQLDB_AVAILABLE = False
    MysqlReader = None
from .lib.mysql_dump_reader import MysqlDumpReader
from .lib.postgres_file_writer import PostgresFileWriter
try:
    from .lib.postgres_db_writer import PostgresDbWriter
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    PostgresDbWriter = None
from .lib.converter import Converter
from .lib.config import Config
from .lib.errors import ConfigurationFileInitialized


class Mysql2Pgsql(object):
    def __init__(self, options):
        self.run_options = options
        try:
            self.file_options = Config(options.file, True).options
        except ConfigurationFileInitialized as e:
            print_red(str(e))
            raise e

    def convert(self):
        mysql_opts = self.file_options['mysql']
        # Use MysqlDumpReader if dump_file is specified or MySQLdb is not available
        if mysql_opts.get('dump_file') or not MYSQLDB_AVAILABLE:
            if not MYSQLDB_AVAILABLE and not mysql_opts.get('dump_file'):
                print_red("MySQLdb (mysqlclient) is not installed. Only dump_file input is supported.")
                raise ImportError("MySQLdb (mysqlclient) is not installed. Please install it or use a MySQL dump file as input.")
            reader = MysqlDumpReader(mysql_opts)
        else:
            if MysqlReader is None:
                print_red("MySQLdb (mysqlclient) is not installed. Cannot use MySQL as a source.")
                raise ImportError("MySQLdb (mysqlclient) is not installed.")
            reader = MysqlReader(mysql_opts)

        # Use file writer if destination is file or psycopg2 is not available
        if self.file_options['destination']['file'] or not PSYCOPG2_AVAILABLE:
            if not PSYCOPG2_AVAILABLE and not self.file_options['destination']['file']:
                print_red("psycopg2 is not installed. Only file output is supported.")
                raise ImportError("psycopg2 is not installed. Please install it or set a file output destination.")
            writer = PostgresFileWriter(self._get_file(self.file_options['destination']['file']), 
                                        self.run_options.verbose, 
                                        index_prefix=self.file_options.get("index_prefix"),
                                        tz=self.file_options.get('timezone'))
        else:
            if PostgresDbWriter is None:
                print_red("psycopg2 is not installed. Cannot use PostgreSQL as a destination.")
                raise ImportError("psycopg2 is not installed.")
            writer = PostgresDbWriter(self.file_options['destination']['postgres'], 
                                      self.run_options.verbose, 
                                      index_prefix=self.file_options.get("index_prefix"),
                                      tz=self.file_options.get('timezone'))

        Converter(reader, writer, self.file_options, self.run_options.verbose).convert()

    def _get_file(self, file_path):
        return codecs.open(file_path, 'wb', 'utf-8')
