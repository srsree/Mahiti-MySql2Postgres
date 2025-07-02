import re

class MysqlDumpReader(object):
    class Table(object):
        def __init__(self, name, columns, indexes=None, foreign_keys=None, triggers=None, comment=None, data=None):
            self._name = name
            self._columns = columns
            self._indexes = indexes or []
            self._foreign_keys = foreign_keys or []
            self._triggers = triggers or []
            self._comment = comment
            self._data = data or []

        @property
        def name(self):
            return self._name

        @property
        def columns(self):
            return self._columns

        @property
        def comment(self):
            return self._comment

        @property
        def indexes(self):
            return self._indexes

        @property
        def foreign_keys(self):
            return self._foreign_keys

        @property
        def triggers(self):
            return self._triggers

        @property
        def query_for(self):
            # Not used for dump-based reader
            return None

    def __init__(self, options):
        self.dump_file = options.get('dump_file')
        if not self.dump_file:
            raise ValueError('No dump_file specified in options')
        self.tables_dict = self._parse_dump(self.dump_file)

    @property
    def tables(self):
        return self.tables_dict.values()

    def read(self, table):
        # Return an iterator over the data rows for the table
        return iter(table._data)

    def close(self):
        pass

    def _parse_dump(self, dump_file):
        # Minimal parser for CREATE TABLE and INSERT INTO
        tables = {}
        with open(dump_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        # Parse CREATE TABLE
        create_table_re = re.compile(r'CREATE TABLE `([^`]+)` \((.*?)\)[^;]*;', re.S)
        insert_into_re = re.compile(r'INSERT INTO `([^`]+)` \((.*?)\) VALUES (.*?);', re.S)
        for match in create_table_re.finditer(sql):
            table_name = match.group(1)
            columns_sql = match.group(2)
            columns = []
            for col_line in columns_sql.split(',\n'):
                col_line = col_line.strip()
                if col_line.startswith('`'):
                    col_match = re.match(r'`([^`]+)` ([^ ]+)', col_line)
                    if col_match:
                        col_name = col_match.group(1)
                        col_type = col_match.group(2)
                        columns.append({'name': col_name, 'type': col_type, 'null': True, 'primary_key': False, 'auto_increment': False, 'default': None, 'comment': None, 'table_name': table_name})
            tables[table_name] = self.Table(table_name, columns)
        # Parse INSERT INTO
        for match in insert_into_re.finditer(sql):
            table_name = match.group(1)
            if table_name not in tables:
                continue
            values_sql = match.group(3)
            # Split values (very basic, does not handle all edge cases)
            values = re.findall(r'\((.*?)\)', values_sql, re.S)
            for value_row in values:
                row = [v.strip(" '") for v in value_row.split(',')]
                tables[table_name]._data.append(row)
        return tables 