'''
EXAMPLES:
----------------------------------------------------------------------------------------------------
$ python courses.py               (Prints everything)
$ python courses.py -a soft,net   (Prints all courses in Software and Networking Subject Areas)
$ python courses.py -s 1,2,3      (Prints all courses in the 1st, 2nd and 2rd Semesters)
$ python courses.py -r true -a cs (Prints all required courses in the Computer Science Subject Area)
----------------------------------------------------------------------------------------------------
'''

import argparse
import sqlite3
import tabulate

SUBJECT_AREAS = {
    'cs': 'Computer Science',
    'soft': 'Software',
    'hard': 'Hardware',
    'net': 'Networking',
    'energy': 'Energy',
    'other': 'Other'
}

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--semester')
parser.add_argument('-a', '--subject-area')
parser.add_argument('-r', '--required')

args = parser.parse_args()

where_clause = []
params = []

if args.semester:
    semesters = [int(s) for s in args.semester.split(',')]
    params.extend(semesters)
    where_clause.append(f"[Semester] IN ({','.join('?' * len(semesters))})")

if args.subject_area:
    areas = [SUBJECT_AREAS[s] for s in args.subject_area.split(',') if s in SUBJECT_AREAS]
    params.extend(areas)
    where_clause.append(f"[Subject Area] IN ({','.join('?' * len(areas))})")
    
if args.required:
    required = 'Required' if args.required.lower() == 'true' else 'Elective'
    params.append(required)
    where_clause.append("[Required/Elective] = ?")

query  = "SELECT * FROM [Courses]"
where_clause = f" WHERE {' AND '.join(where_clause)}"

if params:
    query += where_clause

conn = sqlite3.connect('courses.db')
c = conn.cursor()

c.execute(query, params)
results = c.fetchall()

cols = ['Course Name', 'Subject Area', 'Semester', 'Required/Elective']
print(tabulate.tabulate(results, headers=cols, tablefmt='psql'))
