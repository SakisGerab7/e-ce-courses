import sqlite3

conn = sqlite3.connect('courses.db')
c = conn.cursor()

with open('table.sql', 'r') as f:
    all = f.read().strip()
    c.executescript(all)
        
conn.commit()
conn.close()