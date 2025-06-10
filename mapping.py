
# coding: utf-8

# In[1]:

import xml.etree.cElementTree as ET #importing the xml parser as ET
import re # Importing re module for the regular expression
from collections import defaultdict # importing the default dict from the collection
import os #importing os
osm_file ='chennai_india.osm'
sample_file ='chennaisample.osm'
mapping = {
        'Ave':  'Avenue',
        'AVENUE' : 'Avenue',
        'colony': 'Colony',
        'Extn':'Extension',
        'Extn.':'Extension',
        'EXTN':'Extension',
        'LANE':'Lane',
        'nagar':'Nagar',
        'Rd':'Road',
        'ROAD':'Road',
        'road':'Road',
        'St':'Street',
        'street' : 'Street'
        }


all_street_word = set()
name_list = []
def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")
def audit_street(osmfile):
    osm_file = open(osmfile, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag in["node", "way", "relation"] :
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    better_name = update_name(tag.attrib['v'])
                    name_list.append(better_name)
                    
    osm_file.close()
    return name_list

def update_name(name):

    # YOUR CODE HERE
    for n in name.split():
        if n in mapping:
            name = name.replace(n, mapping[n])
    return name



#st_name = audit_street(sample_file)
st_name = audit_street(osm_file)
print st_name


# In[ ]:



