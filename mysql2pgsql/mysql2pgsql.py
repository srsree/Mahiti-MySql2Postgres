import codecs

from .lib import print_red
from .lib.mysql_reader import MysqlReader
from .lib.mysql_dump_reader import MysqlDumpReader
from .lib.postgres_file_writer import PostgresFileWriter
from .lib.postgres_db_writer import PostgresDbWriter
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
        # Use MysqlDumpReader if dump_file is specified
        mysql_opts = self.file_options['mysql']
        if mysql_opts.get('dump_file'):
            reader = MysqlDumpReader(mysql_opts)
        else:
            reader = MysqlReader(mysql_opts)

        if self.file_options['destination']['file']:
            writer = PostgresFileWriter(self._get_file(self.file_options['destination']['file']), 
                                        self.run_options.verbose, 
                                        index_prefix=self.file_options.get("index_prefix"),
                                        tz=self.file_options.get('timezone'))
        else:
            writer = PostgresDbWriter(self.file_options['destination']['postgres'], 
                                      self.run_options.verbose, 
                                      index_prefix=self.file_options.get("index_prefix"),
                                      tz=self.file_options.get('timezone'))

        Converter(reader, writer, self.file_options, self.run_options.verbose).convert()

    def _get_file(self, file_path):
        return codecs.open(file_path, 'wb', 'utf-8')
