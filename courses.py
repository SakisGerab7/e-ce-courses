'''
EXAMPLES:
----------------------------------------------------------------------------------------------------
$ python courses.py                  (Prints everything)
$ python courses.py -a soft,net      (Prints all courses in Software and Networking Subject Areas)
$ python courses.py -s 1,2,3         (Prints all courses in the 1st, 2nd and 2rd Semesters)
$ python courses.py -r true -a cs    (Prints all required courses in the Computer Science Subject Area)
$ python courses.py -p ECE069,ECE420 (Prints all courses that require ECE069 and ECE420 to be passed)
----------------------------------------------------------------------------------------------------
'''

import argparse
import sqlite3
import tabulate
import os

DATABASE = 'courses.db'

SUBJECT_AREAS = {
    'cs': 'Computer Science',
    'soft': 'Software',
    'hard': 'Hardware',
    'net': 'Networking',
    'energy': 'Energy',
    'other': 'Other'
}

class QueryBuilder():
    def __init__(self):
        self._params = []
        self._qstr   = ''
        self._select = False
        self._join   = False
        self._where  = False

    def get_query(self):
        return self._qstr
    
    def get_params(self):
        return self._params

    def select(self, select_cols, from_table):
        if not (self._select or self._join or self._where):
            self._select = True
            self._qstr = f"SELECT {', '.join(select_cols)} FROM {from_table}"

        return self

    def join(self, table, on_cond):
        if self._select and not (self._join or self._where):
            self._join = True
            self._qstr += f' JOIN {table} ON {on_cond}'

        return self

    def where(self, col, params):
        if self._select:
            self._join = True

            if self._where:
                self._qstr += ' AND'
            else:
                self._where = True
                self._qstr += ' WHERE'

            if type(params) is list:
                self._params.extend(params)
                self._qstr += f" {col} IN ({','.join('?' * len(params))})"
            else:
                self._params.append(params)
                self._qstr += f" {col} = ?"

        return self


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--semester')
    parser.add_argument('-a', '--subject-area')
    parser.add_argument('-r', '--required')
    parser.add_argument('-p', '--prerequisite')

    args = parser.parse_args()

    query = QueryBuilder().select(['Course_ID', 'Course_Name', 'Subject_Area', 'Semester', 'Required_Elective'], 'Courses c')

    if args.prerequisite:
        prerequisites = args.prerequisite.split(',')
        query = query.join('Requirements r', 'c.Course_ID = r.Requiring_ID').where('r.Required_ID', prerequisites)

    if args.semester:
        semesters = [int(s) for s in args.semester.split(',')]
        query = query.where('Semester', semesters)

    if args.subject_area:
        areas = [SUBJECT_AREAS[s] for s in args.subject_area.split(',') if s in SUBJECT_AREAS]
        query = query.where('Subject_Area', areas)
        
    if args.required:
        required = 'Required' if args.required.lower() == 'true' else 'Elective'
        query = query.where('Required_Elective', required)

    db_exists = os.path.isfile(DATABASE)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if not db_exists:
        with open('create_db.sql', 'r') as f:
            all = f.read().strip()
            c.executescript(all)
                
        conn.commit()

    c.execute(query.get_query(), query.get_params())
    results = c.fetchall()

    cols = ['Course ID', 'Course Name', 'Subject Area', 'Semester', 'Required/Elective']
    print(tabulate.tabulate(results, headers=cols, tablefmt='psql'))

    conn.close()