# -*- coding: utf-8 -*-
"""
Kindergarten.py

Author: Anderson Wong

Date: January 10, 2025

Description: This is a Python program that generates RDF triples 
for kindergartens using OpenStreetMap data in a geojson file.

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
gcie = rdflib.Namespace('http://ontology.eil.utoronto.ca/GCI/Education/GCI-Education.owl#')
rdfs = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')

# Create RDF graph
g = Graph()

# Initialize variables
filename = "school.geojson"
filename2 = "kindergarten.geojson"
amenityname = "Kindergarten"

# Get the data
amenity = json.loads(open(filename, encoding='utf8').read())
amenity2 = json.loads(open(filename2, encoding='utf8').read())

# Generate triples
g.add((cdt.Kindergarten, code.hasCode, cdt.level0ISCEDCode))

g.add((cdt.level0ISCEDCode, RDF.type, cdt.ISCEDCode))

g.add((cdt.level0ISCEDCode, genprop.hasName, Literal("0 Early childhood education")))
g.add((cdt.level0ISCEDCode, genprop.hasDescription, Literal("Education designed to support early development in preparation for participation in school and society.")))

g.add((cdt.Kindergarten, rdfs.subClassOf, gcie.EducationFacility))

# Generate triples for each instance
for element in amenity["features"]:
    try:
        print(element['properties']['isced:level'])
    except:
        pass
    else:
        if "0" in element['properties']['isced:level']:
            osmid = re.sub("[^0-9]", "", element["id"])
            instancename = osmid + amenityname
            
            g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))
            
            try:    
                g.add((cdt[instancename], genprop.hasName, Literal(element['properties']['name'])))
            except:
                pass
    
            g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
            g.add((cdt[instancename], gci.forCity, toronto.toronto))
            
            g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
            
            g.add((cdt[instancename + "Location"], RDF.type, loc.Location))
            
            g.add((cdt[instancename], RDF.type, cdt.Kindergarten))

for element in amenity2["features"]:
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + amenityname
    
    g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))
    
    try:    
        g.add((cdt[instancename], genprop.hasName, Literal(element['properties']['name'])))
    except:
        pass

    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location))
    
    g.add((cdt[instancename], RDF.type, cdt.Kindergarten))

# Export the RDF graph as a .ttl file
g.serialize(destination="Kindergartens.ttl")





