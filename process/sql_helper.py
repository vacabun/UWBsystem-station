import sqlite3

from process.typedef import position
from process.typedef import MeasureData

class SqlHelper:
    def __init__(self):
        self.cursor = None
        self.sql_text = None
        self.res_db_conn = None

    def init_db(self):
        self.res_db_conn = sqlite3.connect('data.sqlite')

    def _create_data_table(self, label_address: int):
        self.res_db_conn = sqlite3.connect('data.sqlite')
        self.cursor = self.res_db_conn.cursor()
        self.sql_text = '''
            create table label_{label_address}
            (
                label_address  integer   not null,
                node_address   integer   not null,
                asctime        TEXT      not null,
                frame_num      integer   not null,
                distance       integer   not null
            );
        '''.format(label_address=label_address)
        self.cursor.execute(self.sql_text)
        self.res_db_conn.commit()
        self.res_db_conn.close()

    def _find_data_table(self, label_address: int) -> bool:
        self.res_db_conn = sqlite3.connect('data.sqlite')
        self.cursor = self.res_db_conn.cursor()
        self.sql_text = '''
            select count(*) from sqlite_master where type = \'table\' and name = \'label_{label_address}\';
            '''.format(label_address=label_address)
        self.cursor.execute(self.sql_text)
        res = 0
        for row in self.cursor:
            res = row[0]
        self.res_db_conn.commit()
        self.res_db_conn.close()
        if res == 1:
            return True
        else:
            return False

    def add_data(self, data: MeasureData):
        if not self._find_data_table(data.label_address):
            self._create_data_table(data.label_address)

        self.res_db_conn = sqlite3.connect('data.sqlite')
        self.cursor = self.res_db_conn.cursor()
        self.sql_text = '''
            INSERT INTO label_{label_address} (label_address, node_address, asctime, frame_num, distance) 
            VALUES ({label_address}, {node_address}, \'{asctime}\', {frame_num}, {distance})
            '''.format(label_address=data.label_address, node_address=data.node_address, asctime=data.asctime,
                       frame_num=data.frame_num, distance=data.distance)
        self.cursor.execute(self.sql_text)
        self.res_db_conn.commit()
        self.res_db_conn.close()

