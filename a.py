import sqlite3

def run(db: str):
    connection = sqlite3.connect(db)
    
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS isk 
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS isk(
                    id INTEGER PRIMARY KEY,
                    number TEXT NOT NULL 
                   )
                        ''')
    connection.commit()        
    connection.close()

a = 'database_sud.db'


run(a)

