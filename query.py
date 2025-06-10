
# coding: utf-8

# In[25]:

import sqlite3
def number():
    result = cur.execute("select count(*) from nodes;")
    return result.fetchall()
def way():
    result = cur.execute("select count(*) from ways;")
    return result.fetchall()
def unique():
    result = cur.execute("select user,count(*) as num from nodes group by user order by num desc limit 3;")
    return result.fetchall()
def amenity():
    result = cur.execute("select value,count(*) as num from nodes_tags where key ='amenity' group by value order by num desc limit 5;")
    return result.fetchall()
def shop():
    result = cur.execute("select value,count(*) as num from nodes_tags where key ='shop' group by value order by num desc limit 5;")
    return result.fetchall()
def cuisine ():
    result=cur.execute("select value,count(*) as num from nodes_tags where key ='cuisine' group by value order by num desc limit 5;")
    return result.fetchall()
conn = sqlite3.connect("chennai.db")
cur = conn.cursor()
print "nodes ",number()
print "ways",way()
print "unique", unique()
print "amenity",amenity()
print "shop",shop()
print "cuisine", cuisine()

conn.close()


# In[ ]:



