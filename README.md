
## OpenStreetMap Data Case Study

### Liang Sun     June 5, 2017

-----

### 1. Map Area

Denver-Boulder, Colorado

https://mapzen.com/data/metro-extracts/metro/denver-boulder_colorado/

Denver is the capital and most populous municipality of the state of Colorado. It is also close to the Rocky Mountains and has rich resources for tourism. I chose Denver-Boulder area as the object of analysis for this case study because I will move there this summer. I am curious about the city of my future home and hope to have a better knowledge about it.

----

### 2. Problems Encountered in the Map

#### Identifying the problems
Some of the information in the data should follow certain formats, particularly address names should be easy to read and correctly spelt. Also, postal codes should be consistent in this area (the first two digits are "80"). A few problems have been noticed by checking the map data:

- Overabbreviated street names ("Hwy", "Ave", "St", "S", "West", etc.)

- Wrongly spelt street names ("South Holly Strret","South Fairplay Sreet")

- Wrongly combined street names ("East Mainstreet")

- Inconsistent postal codes ("CO 80305","CO80219","Golden, CO 80401")

- Wrong postal codes ("1800", "6210", "Highlands Ranch")

Street names that were wrongly spelt or combined can be verified by searching Google Map and thus be corrected.

In addition, street names that contain foreign character ("Pe$\tilde n$a Boulevard") are left as they are.

Postal codes with wrong values are neglected and remain unchanged due to lack of correct information.

#### Auditing and cleaning the data

- Street names

The main function I used for improving street names:

``` python
def update_name(name, mapping):
    name_list = name.split(' ')
    for i in range(len(name_list)):
        if name_list[i].lower() in mapping.keys() and "Unit E" not in name:
            #do not change "Unit E" into "Unit East"
            name_list[i] = mapping[name_list[i].lower()]
        if name_list[i].lower() in mapping.keys() and "Unit E" in name:
            if name_list[i].lower() != "e":
                name_list[i] = mapping[name_list[i].lower()]
    new_name = ' '.join(name_list)
    return new_name

```

This updates all problematic address strings, for example,

|Problematic Address|Updated Address|
|------|-----|
|SH 7|State Highway 7|
|E Orchard Pl|East Orchard Place|
|Ken Pratt Blvd Unit E|Ken Pratt Boulevard Unit E|

- Postal codes

The main function I used for making the format of postal codes consistent:

``` python
for tag in root.findall('./node/tag'):
    if is_zip_name(tag):
        #remove all non-digit characters first
        tag.attrib['v'] = re.sub('[^0-9]','', tag.attrib['v'])
        #the postal code format is either 80XXX or 80XXX-XXXX
        if len(tag.attrib['v'])>5:
            tag.attrib['v'] = tag.attrib['v'][0:5]+'-'+tag.attrib['v'][5:]
        #one postal code was found to be 90222
        if tag.attrib['v'][0:2]=='90':
            tag.attrib['v'] = '80'+tag.attrib['v'][2:5]
```

This updates all problematic postal codes, for example,

|Problematic Postal Codes|Updated Postal Codes|
|------|-----|
|CO 80305|80305|
|Golden,CO 80401|80401|
|CO80219|80219|
|90222|80222|

----

### 3. Overview of the Data

After writing the orignial map osm data into csv files, I used sqlite to convert csv files into tables in an SQL database following the schema as suggested.

#### Size of the file

``` sql
denver.osm ......... 890 MB   
nodes.csv .......... 350 MB    
node_tags.csv ......  13 MB    
ways.csv ...........  28 MB    
way_nodes.csv ...... 116 MB    
way_tags.csv .......  65 MB    
osm.db ............. 550 MB    
```
#### Number of unique users

``` sql
SELECT COUNT(DISTINCT(e.uid))
FROM (SELECT uid FROM nodes UNION SELECT uid FROM ways) AS e;

```
3365

#### Number of nodes and ways

``` sql
SELECT COUNT(*)
FROM nodes;
```
524287

``` sql
SELECT COUNT(*)
FROM ways;
```
924395

#### Number of chosen type of nodes

- Cafes

``` sql
SELECT COUNT(*)
FROM nodes_tags
WHERE key = 'amenity' and value = 'cafe';

```
471


- Shops

``` sql
SELECT COUNT(*)
FROM nodes_tags
WHERE key = 'shop';
```
4018




#### Additional statistics

- Ten most contributing users

``` sql
SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) AS e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;

```

``` sql
woodpeck_fixbot ......... 344837  
"Your Village Maps" ..... 101328  
chachafish ............... 90597  
GPS_dr ................... 64810  
jjyach ................... 41332  
DavidJDBA ................ 23340  
Stevestr ................. 19800  
balrog-kun ............... 19126  
russdeffner .............. 14886  
CornCO ................... 12046
```
It seems that the first user has way much more contribution to the database than other users. The name itself looks like a robot. By checking online, I found this account is used by Frederik Ramm for automated edits. The second user "Your Village Maps" which looks like an abnormal name is actually a real mapper.



- Top ten categories of shops

``` sql
SELECT COUNT(*),value
FROM nodes_tags
WHERE key = 'shop'
GROUP BY value
ORDER BY COUNT(*) DESC
LIMIT 10;

```

``` sql
Convenience .... 417  
Unspecified .... 359  
Car_repair ..... 272  
Hairdresser .... 270  
Alcohol ........ 219   
Clothes ........ 217   
Supermarket .... 193   
Beauty ......... 143  
Doityourself ... 138   
Car ............ 136   
```
Many node tags with the key "shop" have the value "yes" instead of an actual name, which means the shops are unspecified.

The category "doityourself" includes a variety of shops or services, such as parking spot, self storage, Auto Zone, Home Depot, Lowes, etc.

Interestingly, there are also 4 "marijuana" shops in the data because recreational use of marijuana is legal in Colorado, which may not be found if we explore map data of many other states.

----

### 4. Other Ideas about the Dataset



#### Guidelines for mappers

From the data auditing and cleaning process, I encountered a few problems with the formatting of addresses and postal codes as discussed above. In addition, there are some other undiscussed problems with the information collected by the database. For example, the categorizations of nodes need to be improved since information for many nodes is incomplete and a large number of shops are not specified.

If the OpenStreetMap has not done the following suggestion yet, I think it would help if some guidelines or manuals can be provided for mappers to follow when they are entering and coding addresses, postal codes, and categorizing shops or other facilities. By doing so, there would be fewer confusions and errors in the data. For example, the addresses will become easier to read, search and extract for users. More informative categorizations of amenities and facilities will help users to find the closest and the most convenient target in the map.

However, some problems can be anticipated in implementing this improvement:

- There are thousands of users who contribute to the map data, and more new mappers will join the mapping in future. It will be a challenge to have the guidelines read by everyone.

- Mappers have their own preferences for mapping and lack motivation to follow the guidelines. We can only encourage rather than demand them to follow.

- Mappers have inadequate communication with each other and do not have a consensus of the construct and the format of the data.

- Errors are unavoidable because human's work cannot be always perfect.


A few measures can be taken to deal with the problems stated above:

- Start promoting guidelines among a focus group of top mappers by strengthening the communication with them, since the contributions are highly skewed and a small number of mappers contribute the majority of entries in the data. Once the majority of entries are presented in a consistent format, other mappers are more likely to follow.

- Introduce gamification system and give users virtual rank or title as incentives based on the number and quality of their contributions. The quality of their work can be measured by how well they follow the guidelines.

- Sponsor and organize annual workshops or meetings to award top contributors, promote OSM guidelines and enhance communication among mappers.

- Encourage mappers to check and review other people's contribution based on the guidelines, and their work is taken into account by the gamification system.







#### Further analysis of the tourism


Colorado is well-known for its natural attractions. Tourism is an important basic industry in the state and contributes to 5 percent of state GDP and 11.3 percent of jobs. Due to its tourism and rich resources for outdoors activities, Colorado is also rated one of the most healthiest state in the United States.

Here we can have an idea of the tourism resources of Colorado by looking into the Denver OSM data.



``` sql
SELECT DISTINCT(value)
FROM nodes_tags
WHERE key = 'tourism';

```

``` sql
Picnic_site .......... 438  
Camp_site  ........... 431  
Information .......... 261  
Artwork .............. 123  
Viewpoint ............. 92  
Hotel ................. 88  
Motel ................. 57  
Museum ................ 37  
Gallery ............... 28  
Attraction ............ 22  
Caravan_site .......... 17  
Guest_house ............ 9  
Hostel ................. 4  
Alpine_hut ............. 3  
Unspecified ............ 2  
Theme_park ............. 1  
Trail_riding_station ... 1  
```

In more in-depth and comprehensive analysis, we can compare the tourism resources of different cities in the state or compare Colorado with other states and thus know the advantages and disadvantages of Colorado cities in tourism.


Source:  
https://www.openstreetmap.org/user/woodpeck_fixbot  
https://www.openstreetmap.org/user/Your%20Village%20Maps  
http://www.cobizmag.com/Articles/The-economist-Whats-the-most-important-industry-in-Colorado/  
http://www.today.com/health/healthiest-states-report-ranks-well-being-u-s-regions-t107621
https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
