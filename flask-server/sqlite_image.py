# import sqlite3

# conn = sqlite3.connect('test.db')

# print ("数据库打开成功")

#!/usr/bin/python

import sqlite3
print(sqlite3.sqlite_version)

import sqlite_vec

conn = sqlite3.connect('test.db')

conn.enable_load_extension(True)
sqlite_vec.load(conn)
conn.enable_load_extension(False)

print ("数据库打开成功")
c = conn.cursor()
c.execute('''CREATE TABLE COMPANY
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')
print ("数据表创建成功")
conn.commit()
conn.close()

import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()
print ("数据库打开成功")

for i in range(10,100000):

    c.execute(f"INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
        VALUES ({i}, 'Mark', 25, 'Rich-Mond ', 65000.00 )")

conn.commit()
print ("数据插入成功")
conn.close()