from common.sqlite import safe_execute
import sqlite3

connection = sqlite3.connect('database_sud.db') 
connection.row_factory = sqlite3.Row

safe_execute(connection, f'''UPDATE iskstatus 
                SET status = ?, 
                status_text = ?, 
                result = ?,
                result_date = ?,
                result_sud_name = ?,
                result_number = ?
                WHERE id = ?
                ''', 
                ('success', 
                '', 
               '', 
                'result_date',
                'result_sud_name',
                'result_number',
                 '2'),)