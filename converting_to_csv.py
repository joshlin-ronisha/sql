
# coding: utf-8

# In[31]:


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
osm_file ='chennai_india.osm'
sample_file ='chennaisample.osm'

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
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
        'St.' : 'Street',
        'street' : 'Street'
        }

def clean_street(name,mapping):   
    m = street_type_re.search(name)
    if m:
        for a in mapping:
            if a == m.group():
                name = re.sub(street_type_re, mapping[a], name)
    return name
def clean_postalcode(elem):
    default = 600001
    def length(ele):
        if ele.startswith('600'):
            if len(ele) > 6 :
                ele = ele[:3] + ele[4:]
                return ele
            elif len(ele) == 6 :
                ele = ele
                return ele
            else:
                ele = default
                return ele
        else:
            ele = default
            return ele            
    elem= re.sub(r'\s+','',elem)
    elem=elem.strip('.')
    elem =elem.strip(',')
    elem = length(elem)
    return elem
def clean_building(element): 
        if element== 'yes':
            return element
        else:
            element = 'yes'
            return element
  
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []# Handle secondary tags the same way for both node and way element
    def create_tags_dict(element):
        tags = []
        for tag in element.iter('tag'):
            info ={}
            if PROBLEMCHARS.search(tag.attrib['k']):
                pass
            else:
                try:
                    if tag.attrib['k'].index(':'):
                        first_colon_position = tag.attrib['k'].index(':')
                        info['id'] = element.attrib['id']
                        info['key'] =tag.attrib['k'][first_colon_position +1 :]
                        info['type'] = tag.attrib['k'][:first_colon_position]
                        if info['key'] == 'street' and info['type'] == 'addr':
                            updated_name= clean_street(tag.attrib['v'],mapping)
                            info['value'] = updated_name
                        elif info['key'] == 'postcode'and info['type'] == 'addr':
                            updated_code = clean_postalcode(tag.attrib['v'])
                            info['value'] = updated_code
                        else:
                            info['value'] = tag.attrib['v']
                        tags.append(info)
                except ValueError:
                    info['id'] = element.attrib['id']
                    info['key'] = tag.attrib['k']
                    if info['key'] == 'building':
                        info['value'] = clean_building(tag.attrib['v'])
                    else:
                        info['value'] = tag.attrib['v']
                    info['type'] = default_tag_type
                    tags.append(info)
        return tags
                                
    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in node_attr_fields:
                node_attribs[attrib] = element.attrib[attrib]
        tags = create_tags_dict(element)
        node =  {'node': node_attribs, 'node_tags': tags}
        return node
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in way_attr_fields:
                way_attribs[attrib] = element.attrib[attrib]
        tags = create_tags_dict(element)
        way_nodes = []
        for waynode in element.findall('nd'):
            info = {
                'id' : element.attrib['id'],
                'node_id' : waynode.attrib['ref'],
                'position' : element.findall('nd').index(waynode)
                }
            way_nodes.append(info)
        way =  {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        return way


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()




class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()


        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

#process_map(sample_file)
if __name__ == "__main__":
    
    process_map(osm_file)


# In[ ]:




# In[ ]:



