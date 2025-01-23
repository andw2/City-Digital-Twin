# -*- coding: utf-8 -*-
"""
Park.py

Author: Anderson Wong

Date: January 10, 2025

Description: This is a Python program that generates RDF triples 
for parks using OpenStreetMap data in a geojson file.
    
"""

# Import modules
import rdflib
import json
import shapely
import re

from rdflib import Graph, Literal, XSD, RDF

# Declare namespaces
toronto = rdflib.Namespace('http://ontology.eil.utoronto.ca/Toronto/Toronto#')
genprop = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-1/ed-1/en/ontology/GenericProperties/')
cdt = rdflib.Namespace('http://ontology.eil.utoronto.ca/CDT#')
gcir = rdflib.Namespace('http://ontology.eil.utoronto.ca/GCI/Recreation/GCIRecreation.owl#')
loc = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-1/ed-1/en/ontology/SpatialLoc/')
geo = rdflib.Namespace('http://www.opengis.net/ont/geosparql#')
gci = rdflib.Namespace('http://ontology.eil.utoronto.ca/GCI/Foundation/GCI-Foundation.owl#')
code = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-2/ed-1/en/ontology/Code/')
rdfs = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')

# Create RDF graph
g = Graph()

# Get the data
parks = json.loads(open('park.geojson', encoding='utf8').read())

g.add((gcir.Park, code.hasCode, cdt.parkOSMCode))
g.add((gcir.parkOSMCode, RDF.type, cdt.LeisureOSMCode))
g.add((cdt.parkOSMCode, genprop.hasName, Literal("leisure=park")))
g.add((cdt.parkOSMCode, genprop.hasDescription, Literal("A park, usually in an urban (municipal) setting, created for recreation and relaxation. ")))
g.add((gcir.LeisureOSMCode, rdfs.subClassOf, code.Code))

# Generate triples
for element in parks["features"]:
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + "Park"
    
    """
    if element["geometry"]["type"] == "Point":
        g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.Point(element["lon"], element["lat"]).to_wkt, datatype=geo.wktLiteral)))
    else:
        pointlist = []
        for point in element["geometry"]:
            pointlist.append([point["lon"], point["lat"]])
        g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.Polygon(pointlist).to_wkt, datatype=geo.wktLiteral)))
"""
    g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))
    try:    
        g.add((cdt[instancename], genprop.hasName, Literal(element['properties']['name'])))
    except:
        pass
    g.add((cdt[instancename], RDF.type, gcir.Park))
    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    
    
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location))

# Export the RDF graph as a .ttl file
g.serialize(destination="Parks2.ttl")





