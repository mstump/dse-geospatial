#!/usr/bin/env python
from __future__ import print_function
import inspect
import json
import locale
import multiprocessing
import os
import operator
import random
import sys
import signal
import time
import uuid
from datetime import date, timedelta
from itertools import *

# from cassandra.io.libevreactor import LibevConnection
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

KEYSPACE = "geo"
COLUMN_FAMILY = "geo"

KEYSPACE_CREATION_STATEMENT = """CREATE KEYSPACE IF NOT EXISTS %s WITH replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };""" % KEYSPACE

COLUMN_FAMILY_CREATION_STATEMENT = """
CREATE TABLE IF NOT EXISTS %s.%s (
  key text,
  color text,
  location text,
  location_0_coordinate double,
  location_1_coordinate double,
  PRIMARY KEY ((key))
);""" % (KEYSPACE, COLUMN_FAMILY)

LOCATION_FILTER_STATEMENT = """SELECT * FROM %s.%s WHERE solr_query='{"q":"*:*", "fq":"{!geofilt pt=?,? sfield=location d=?}"}';""" % (KEYSPACE, COLUMN_FAMILY)
LOCATION_FILTER_PREPARED = None

COLORS = ["thistle", "medium purple", "purple", "blue violet", "dark violet", "dark orchid", "medium orchid", \
          "orchid", "plum", "violet", "magenta", "violet red", "medium violet red", "maroon", "pale violet red", \
          "light pink", "pink", "deep pink", "hot pink", "red", "orange red", "tomato", "light coral", "coral", \
          "dark orange", "orange", "light salmon", "salmon", "dark salmon", "brown", "firebrick", "chocolate", "tan", \
          "sandy brown", "wheat", "beige", "burlywood", "peru", "sienna", "saddle brown", "indian red", "rosy brown", \
          "dark goldenrod", "goldenrod", "light goldenrod"]

# SF Geo coordinates: 37.7752,-122.4232
SF_LAT = 37.7752
SF_LON = -122.4232


def prepare_statements(session):
    global LOCATION_FILTER_PREPARED
    LOCATION_FILTER_PREPARED = session.prepare(LOCATION_FILTER_STATEMENT)


def find_within_distance(session, lat, lon, distance, fetch_size=20):
    # Find all points within a diameter of lat and lon
    # http://localhost:8983/solr/geo.geo/select?wt=json&indent=true&q=*:*&fq={!geofilt%20pt=37.7752,-122.4232%20sfield=location%20d=5000}
    query = """SELECT * FROM %s.%s WHERE solr_query='{"q":"*:*", "fq":"{!geofilt pt=%s,%s sfield=location d=%s}"}';""" \
            % (KEYSPACE, COLUMN_FAMILY, lat, lon, distance)

    statement = SimpleStatement(query)
    statement.fetch_size = fetch_size
    return session.execute(statement)


def find_within_distance_and_color(session, lat, lon, distance, color, fetch_size=20):
    # Find all points of color within a diameter of lat and lon
    query = """SELECT * FROM %s.%s WHERE solr_query='{"q":"color:%s", "fq":"+{!geofilt pt=%s,%s sfield=location d=%s}"}';""" \
            % (KEYSPACE, COLUMN_FAMILY, color, lat, lon, distance)
    statement = SimpleStatement(query)
    statement.fetch_size = fetch_size
    return session.execute(statement)


def find_within_distance_sorted(session, lat, lon, distance, fetch_size=20):
    # Find all points of color within a diameter of lat and lon
    # Not supported yet via CQL, need to use HTTP interface (DSP-5975)
    # http://localhost:8983/solr/geo.geo/select?wt=json&indent=true&fl=key,color&q=*:*&sfield=location&pt=37.7752,-122.4232&sort=geodist()%20asc&fl=_dist_:geodist(),key,color
    query = """SELECT * FROM %s.%s WHERE solr_query='{"q":"*:*", "fq":"+{!geofilt pt=%s,%s sfield=location d=%s}", "sort":"geodist(location,%s,%s) asc"}';""" \
            % (KEYSPACE, COLUMN_FAMILY, lat, lon, distance, lat, lon)
    statement = SimpleStatement(query)
    statement.fetch_size = fetch_size
    return session.execute(statement)


def get_color_facets(session):
    query = """SELECT * FROM %s.%s WHERE solr_query='{"q":"*:*", "facet":{"field":"color"}}';""" \
            % (KEYSPACE, COLUMN_FAMILY)
    statement = SimpleStatement(query)
    result = session.execute(statement)
    return sorted(json.loads(result[0][0])["color"].items(), lambda x,y: cmp(x[1], y[1]), reverse=True)


def get_script_path():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def create_schema(session):
    session.execute(KEYSPACE_CREATION_STATEMENT)
    session.execute(COLUMN_FAMILY_CREATION_STATEMENT)


def check_solr_status():
    cmd = """dsetool reload_core %s.%s schema=schema.xml solrconfig=solrconfig.xml""" % (KEYSPACE, COLUMN_FAMILY)
    output = os.popen(cmd).read()
    if not output.find("No resource") == -1:
        return False
    return True


def setup_solr():
    operation = "reload_core" if check_solr_status() else "create_core"
    cmd = """dsetool %s %s.%s schema=schema.xml solrconfig=solrconfig.xml""" % (operation, KEYSPACE, COLUMN_FAMILY)
    os.popen(cmd)


def populate(session, count):
    insert_string = """INSERT INTO %s.%s (key, color, location) VALUES (?, ?, ?);""" % (KEYSPACE, COLUMN_FAMILY)
    insert_prepared = session.prepare(insert_string)

    for i in xrange(count):
        id = str(uuid.uuid4())
        color = random.choice(COLORS)
        op = random.choice([operator.add, operator.sub])
        lat = op(SF_LAT, random.random())
        lon = op(SF_LON, random.random())
        lat_lon = "%s,%s" % (lat, lon)
        session.execute(insert_prepared.bind((id, color, lat_lon)))


def limit_iterator(source, limit=5):
    if not type(source) == type(iter([])):
        source = iter(source)

    try:
        for _ in xrange(limit):
            yield next(source)
    except StopIteration:
        pass


def highlight(source):
    return "\033[0;36m%s\033[0m" % source


if __name__ == '__main__':
    COUNT = 1000
    COLOR = "thistle"
    cluster = Cluster()
    # cluster.connection_class = LibevConnection
    session = cluster.connect()

    print(highlight("change the working dir to the path of the script"))
    os.chdir(get_script_path())
    prepare_statements(session)

    print(highlight("create the schema if it doesn't exist"))
    create_schema(session)

    print(highlight("enable solr with the geospatial functionality"))
    setup_solr()

    print(highlight("create sample records"))
    populate(session, COUNT)

    print(highlight("First 5 points within 50 of San Francisco"))
    for i in limit_iterator(find_within_distance(session, SF_LAT, SF_LON, 50)):
        print(i)

    print(highlight("First 5 points within 50 of San Francisco and of color %s" % COLOR))
    for i in limit_iterator(find_within_distance_and_color(session, SF_LAT, SF_LON, 50, COLOR)):
        print(i)

    print(highlight("Get top 5 most frequent colors (facets)"))
    for i in limit_iterator(get_color_facets(session)):
        print(i)

    print(highlight("First 5 points within 50 of San Francisco sorted by distance"))
    for i in limit_iterator(find_within_distance_sorted(session, SF_LAT, SF_LON, 50)):
        print(i)
