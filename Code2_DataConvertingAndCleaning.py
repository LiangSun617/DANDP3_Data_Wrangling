
# Set the schema for csv files

SCHEMA = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
} 



# Write xml data to csv files
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

OSM_PATH = "output2.xml"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []   

    if element.tag == 'node':
        """ updating tags first """
        for tag in element.findall('./'):
            # Improving street names  
            if is_street_name(tag):
                tag.attrib['v'] = update_name(tag.attrib['v'],mapping)
            # Updating postal codes
            if is_zip_name(tag):
                # remove all non-digit characters first
                tag.attrib['v'] = re.sub('[^0-9]','', tag.attrib['v'])
                # the postal code should be either 80XXX or 80XXX-XXXX
                if len(tag.attrib['v'])>5:
                    tag.attrib['v'] = tag.attrib['v'][0:5]+'-'+tag.attrib['v'][5:]
                if tag.attrib['v'][0:2]=='90': # one value was found to be 90XXX
                    tag.attrib['v'] = '80'+tag.attrib['v'][2:5] 
        """ extract the information from different types of tags and write into a dictionary """
        for key in NODE_FIELDS:
            node_attribs[key] = element.attrib[key]
        for tag in element.findall('./'):    
            tag_value=tag.attrib['k']
            if PROBLEMCHARS.search(tag_value,) == None:    
            #has no problematic character
                tag_dict={}     
                if ':' not in tag_value:
                    tag_dict['key']= tag_value
                    tag_dict['type'] = 'regular'
                else:
                    tag_value_new = tag_value.split(':',1)
                    tag_dict['type']= tag_value_new[0]
                    tag_dict['key']= tag_value_new[1]
  
                tag_dict['id']=node_attribs['id']
                tag_dict['value']=tag.attrib['v']
                tags.append(tag_dict) 
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for tag in element.findall('./'):
        # improving street names    
            if is_street_name(tag):
                tag.attrib['v'] = update_name(tag.attrib['v'],mapping)
        # Updating postal codes
            if is_zip_name(tag): 
                tag.attrib['v'] = re.sub('[^0-9]','', tag.attrib['v'])
                if len(tag.attrib['v'])>5:
                    tag.attrib['v'] = tag.attrib['v'][0:5]+'-'+tag.attrib['v'][5:]
                if tag.attrib['v'][0:2]=='90':
                    tag.attrib['v'] = '80'+tag.attrib['v'][2:5]   

        for key in WAY_FIELDS:
            way_attribs[key] = element.attrib[key]
        position = 0
        for way_sub in element.findall('./'):
            if way_sub.tag == 'nd':
                way_dict={}
                way_dict['id']=way_attribs['id']
                way_dict['node_id']=way_sub.attrib['ref']
                way_dict['position']= position
                position += 1
                way_nodes.append(way_dict)
            if way_sub.tag == 'tag':
                tag_value=way_sub.attrib['k']
                if PROBLEMCHARS.search(tag_value,) == None:    
                    tag_dict={}     
                    if ':' not in tag_value:
                        tag_dict['key']= tag_value
                        tag_dict['type'] = 'regular'
                    else:
                        tag_value_new = tag_value.split(':',1)
                        tag_dict['type']= tag_value_new[0]
                        tag_dict['key']= tag_value_new[1]
  
                    tag_dict['id']=way_attribs['id']
                    tag_dict['value']=way_sub.attrib['v']
                    tags.append(tag_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
     
        

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    #all elements including subelements are read as separate element
    _, root = next(context) #skip root
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


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
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,         codecs.open(WAYS_PATH, 'w') as ways_file,         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

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

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)


    
    
#=================================#
##   Analyze data using sqlite   ##
#=================================#


### Read csv files into SQL tables ###
 
# "DataType Mismatch" error occurs when importing nodes.csv file directly, because an empty field in a CSV file is just an empty string, which is not valid for an INTEGER PRIMARY KEY column. Therefore, I import csv file into sql table without identifying primary key first, and then set primary key for the existing table:
 

sqlite> CREATE TABLE nodes (id INTEGER NOT NULL,
     lat REAL,
     lon REAL,
     user TEXT,
     uid INTEGER,
     version INTEGER,
     changeset INTEGER,
     timestamp TEXT
 );
 
sqlite> .mode csv
sqlite> .separator ','
sqlite> .import nodes.csv nodes
 
sqlite> PRAGMA foreign_keys=off;
sqlite> BEGIN TRANSACTION;
sqlite> ALTER TABLE nodes RENAME TO old_nodes;
 
sqlite> CREATE TABLE nodes (id INTEGER PRIMARY KEY NOT NULL,
     lat REAL,
     lon REAL,
     user TEXT,
     uid INTEGER,
     version INTEGER,
     changeset INTEGER,
     timestamp TEXT
 );
 
sqlite> INSERT INTO nodes SELECT * FROM old_nodes;
sqlite> DROP TABLE old_nodes;
sqlite> COMMIT;
sqlite> PRAGMA foreign_keys=on;
 


# Do the similar process for creating the table "ways":
 

sqlite> CREATE TABLE ways (
     id INTEGER NOT NULL,
     user TEXT,
     uid INTEGER,
     version TEXT,
     changeset INTEGER,
     timestamp TEXT
 );
 
sqlite> .mode csv
sqlite> .separator ','
sqlite> .import ways.csv ways
 
sqlite> PRAGMA foreign_keys=off;
sqlite> BEGIN TRANSACTION;
sqlite> ALTER TABLE ways RENAME TO old_ways;
 
sqlite> CREATE TABLE ways (
     id INTEGER PRIMARY KEY NOT NULL,
     user TEXT,
     uid INTEGER,
     version TEXT,
     changeset INTEGER,
     timestamp TEXT
 );
 
sqlite> INSERT INTO ways SELECT * FROM old_ways;
sqlite> DROP TABLE old_ways;
sqlite> COMMIT;
sqlite> PRAGMA foreign_keys=on;
 


# For the other three tables, it is more straightforward because no primary key is to be set:

sqlite> CREATE TABLE nodes_tags (
     id INTEGER,
     key TEXT,
     value TEXT,
     type TEXT,
     FOREIGN KEY (id) REFERENCES nodes(id)
 );
 
sqlite> .mode csv
sqlite> .import nodes_tags.csv nodes_tags
 
sqlite> CREATE TABLE ways_tags (
     id INTEGER NOT NULL,
     key TEXT NOT NULL,
     value TEXT NOT NULL,
     type TEXT,
     FOREIGN KEY (id) REFERENCES ways(id)
 );
 
sqlite> .mode ways_tags
sqlite> .import ways_tags.csv ways_tags
 
sqlite> CREATE TABLE ways_nodes (
     id INTEGER NOT NULL,
     node_id INTEGER NOT NULL,
     position INTEGER NOT NULL,
     FOREIGN KEY (id) REFERENCES ways(id),
     FOREIGN KEY (node_id) REFERENCES nodes(id)
 );
 
sqlite> .mode csv
sqlite> .import ways_nodes.csv ways_nodes
 


### Analyzing using SQL ###

# Number of unique users

SELECT COUNT(DISTINCT(e.uid)) 
FROM (SELECT uid FROM nodes UNION SELECT uid FROM ways) AS e;
 
# Number of nodes and ways

SELECT COUNT(*) 
FROM nodes;

SELECT COUNT(*) 
FROM ways;
  
#Number of chosen type of nodes
  
# Cafes

SELECT COUNT(*) 
FROM nodes_tags 
WHERE key = 'amenity' and value = 'cafe';
 
# Shops

SELECT COUNT(*) 
FROM nodes_tags 
WHERE key = 'shop';


### Additional statistics ###

# Ten most contributing users
SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
 
# Top ten categories of shops
SELECT COUNT(*),value 
FROM nodes_tags 
WHERE key = 'shop' 
GROUP BY value 
ORDER BY COUNT(*) DESC 
LIMIT 10;


#Further analysis of the tourism 
SELECT DISTINCT(value) 
FROM nodes_tags 
WHERE key = 'tourism';






