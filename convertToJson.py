#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

# Main code to convert osm file into json file for further import to MongoDB
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
# Mapping of abbreviations to full words 
mapping = { "ул.": "улица",
            "пер.": "переулок"
            }
# Expected street kinds list
expected = ["улица", "переулок", "бульвар", "проспект", "шоссе", "микрорайон", "слобода",
            "съезд", "проезд", "деревня", "посёлок", "набережная", "площадь"]

# Convert osm element into json element and shaping it to meet required type
def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        node['id'] = element.attrib['id']
        if 'visible' in element.keys():
            node['visible'] = element.attrib['visible']
        if 'lat' in element.keys():
            pos = []
            pos.append(float(element.attrib['lat']))
            pos.append(float(element.attrib['lon']))
            node['pos'] = pos
        created = {}
        created['version'] = element.attrib['version']
        created['changeset'] = element.attrib['changeset']
        created['timestamp'] = element.attrib['timestamp']
        created['user'] = element.attrib['user']
        created['uid'] = element.attrib['uid']
        node['created'] = created
        
        addr = {}
        for child in element.iter('tag'):
            if problemchars.match(child.attrib['k']):
                print(child.attrib['k'])
            elif child.attrib['k'].startswith('addr:'):
                st = child.attrib['k'].split(':')
                if len(st) <= 2:
                    addr[st[1]] = child.attrib['v']
            else:
                node[child.attrib['k']] = child.attrib['v']
        if len(addr) > 0:
            if 'street' in addr:
                addr['street'] = update_name(addr['street'])
                #print(addr['street'])
            node['address'] = addr
        if element.tag == "way":
            node_refs = []
            for child in element.iter('nd'):
                node_refs.append(child.attrib['ref'])
            if len(node_refs) > 0:
                node['node_refs'] = node_refs
        return node
    else:
        return None

# Processing map file
def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

# Update street name - substitute abbreviations, change words order if required
def update_name(name):
    updated = False
    for k in mapping:
        if k in name and updated == False:
            name = name.replace(k, mapping[k])
            updated = True
    notFound = True
    type = ""
    for t in expected:
        if notFound:
            if t in name:
                notFound = False
                type = t
    if notFound:
        print("street type not found: ", name)
    else:
        if not name.startswith(type):
            name = type + " " + name.replace(" " + type, "")
    return name

# Invocation of osm file processing
data = process_map('data/nizhniy-novgorod_russia.osm', True)
#process_map("data/nizhniy-novgorod_russia_sample.osm", True)
#pprint.pprint(data)