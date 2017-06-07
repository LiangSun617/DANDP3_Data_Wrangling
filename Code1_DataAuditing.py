
#Create a sample osm
 
import xml.etree.ElementTree as ET  

OSM_FILE = "denver.osm" 
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')
    # write every k-th element into the sample file
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')



# Auditing street names
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = SAMPLE_FILE
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) #the last word, case insensitive


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", 
            "Lane", "Road", "Trail", "Parkway", "Commons","Highway","Circle",
            "Bypass","Broadway","Way","Plaza","Place","Point","State Highway",
            "State Route"]

# UPDATE THIS VARIABLE: problematic street names and their correct forms
mapping = { "st.": "Street",
            "st": "Street",
            "strret": "Street",
            "sreet": "Street",
            "ste.": "Suite",
            "ste": "Suite",
            "mainstreet": "Main Street",
            "blvd": "Boulevard",
            "blvd.": "Boulevard",
            "blvd,": "Boulevard",
            "cir": "Circle",
            "ct": "Court",
            "dr": "Drive",
            "dr.": "Drive",
            "pl": "Place",
            "ave": "Avenue",
            "ave.": "Avenue",
            "av": "Avenue",
            "rd.": "Road",
            "rd": "Road",
            "hwy": "Highway",
            "pky": "Parkway",
            "pkwy": "Parkway",
            "sh": "State Highway",
            "sr": "State Route",
            "ln": "Lane",
            "e": "East",
            "e.": "East",
            "w": "West",
            "w.": "West",
            "n": "North",
            "n.": "North",
            "s": "South",
            "s.": "South"}


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name) 
    # check if any string matches the pattern and return its location
    if m: # if true
        street_type = m.group() #return all the match
        if street_type not in expected: 
            street_types[street_type].add(street_name) 
            # a dictionary with these unusual street_types and their names


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
    #check if it is true that the element has addr:street value

def audit(osmfile):
    """ get all the street types that are not in the expected list """
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    """ change the incorrect street types into there correct forms """
    name_list = name.split(' ')
    for i in range(len(name_list)):
        # do not change "Unit E" into "Unit East"
        if name_list[i].lower() in mapping.keys() and "Unit E" not in name:
            name_list[i] = mapping[name_list[i].lower()]
        if name_list[i].lower() in mapping.keys() and "Unit E" in name:
            if name_list[i].lower() != "e":
                name_list[i] = mapping[name_list[i].lower()]
    new_name = ' '.join(name_list)
    
    return new_name

# check the list of problematic address names
audit(SAMPLE_FILE)


# Audit zip code
def audit_zip_value(zip_value):
    if zip_value[0:2]!= '80':  # Denver area zip codes starts with 80
        return zip_value


def is_zip_name(elem):
    return (elem.attrib['k'] == "addr:postcode") 

def audit_zip(osmfile):
    """ get a list of problematic postal codes """
    osm_file = open(osmfile, "r")
    zip_values = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zip_name(tag):  
                    zip_values.add(audit_zip_value(tag.attrib['v']))
    osm_file.close()
    return zip_values

# check the list of problematic postal codes
audit_zip(SAMPLE_FILE) 

 
