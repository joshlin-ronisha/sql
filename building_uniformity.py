import xml.etree.cElementTree as ET #importing the xml parser as ET
osm_file ='chennai_india.osm'
sample_file ='chennaisample.osm'
def correction(filename):
    for event,elem in ET.iterparse(filename):
        if elem.tag =='tag' and elem.attrib['k'] == 'building':
            if elem.attrib['v'] == 'yes':
                print elem.attrib['v']
            else:
                elem.attrib['v'] = 'yes'
                print elem.attrib['v']
correction(osm_file)
#correction(sample_file)

