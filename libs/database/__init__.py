import sqlite3

con = sqlite3.connect('libs/database/matrix.db')
con.row_factory = sqlite3.Row
