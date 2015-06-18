## About
Simple little program to demonstrate geospatial search on DataStax Enterprise.

## Prerequisites
1. [DataStax Enterprise](http://www.datastax.com/) 4.7 or greater, with the ```bin``` directory in the ```PATH```
1. The DataStax [python driver](https://github.com/datastax/python-driver)
1. The script assumes DSE is running in search mode on localhost.

### Sample Output
```
➜  dse-geospatial git:(master) ./populate.py
change the working dir to the path of the script
create the schema if it doesn't exist
enable solr with the geospatial functionality
create sample records

First 5 points within 50 of San Francisco
Row(key=u'000ac391-d0ca-4e05-9a38-24f6d7f1ac84', color=u'indian red', location=u'37.8607145366,-122.274641772', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'000ee404-91f5-4829-b947-caac48baa34b', color=u'brown', location=u'37.611731215,-122.549939843', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'001f8513-5afb-4b60-b615-3497eea64d83', color=u'medium orchid', location=u'37.881696696,-122.143367075', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'003b5b78-8a16-411c-9994-cb7e5df55254', color=u'dark orange', location=u'37.8152005505,-121.886771981', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'00440d7f-6bdd-42b1-9cf2-d7ab9331f130', color=u'light pink', location=u'37.6610144355,-122.458829376', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)

First 5 points within 50 of San Francisco and of color thistle
Row(key=u'024c6647-d3f4-4fb4-a259-e75b5f935d3f', color=u'thistle', location=u'37.5486535146,-122.85101992', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'02535e19-79e1-4340-ab77-cdb0fa5ba09d', color=u'thistle', location=u'37.7084139878,-122.727847109', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'0364a66d-f8e5-4bd9-99b1-bcc212ba7474', color=u'thistle', location=u'37.4572288338,-122.599730277', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'0573e64d-249a-45d9-b6c2-366bd0d4a278', color=u'thistle', location=u'37.5622093447,-122.731784305', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)
Row(key=u'0797ecac-dddf-4f5d-823e-8eb7267dec9a', color=u'thistle', location=u'37.7148699883,-122.655282915', location_0_coordinate=None, location_1_coordinate=None, solr_query=None)

Get top 5 most frequent colors (facets)
(u'violet', 4338)
(u'red', 4234)
(u'dark', 3574)
(u'brown', 2892)
(u'light', 2819)
```

