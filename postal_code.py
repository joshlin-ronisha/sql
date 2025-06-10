import xml.etree.cElementTree as ET #importing the xml parser as ET
import re # Importing re module for the regular expression
from collections import defaultdict # importing the default dict from the collection
import os #importing os
osm_file ='chennai_india.osm'
sample_file ='chennaisample.osm'
default = 600001
def length(ele):
    if ele.startswith('600'):
        if len(ele) > 6 :
            ele = ele[:3] + ele[4:]
            return ele
        elif len(ele) == 6 :
            return ele
        else:
            return default
    else:
        return default
        
def display(filename):
    for event,elem in ET.iterparse(filename):
        if elem.tag == 'tag' and elem.attrib['k']=='addr:postcode' :
            #print elem.attrib['v']
            elem.attrib['v']= re.sub(r'\s+','',elem.attrib['v'])
            elem.attrib['v']=elem.attrib['v'].strip('.')
            elem.attrib['v'] =elem.attrib['v'].strip(',')
            elem.attrib['v'] = length(elem.attrib['v'])
            print elem.attrib['v']
display(osm_file)
#display(sample_file)

