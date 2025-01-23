# -*- coding: utf-8 -*-
"""
College.py

Author: Anderson Wong

Date: January 10, 2025

Description: This is a Python program that generates RDF triples 
for colleges using OpenStreetMap data in a geojson file.
    
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
filename = "college.geojson"
amenityname = "College"

# Get the data
amenity = json.loads(open(filename, encoding='utf8').read())

# Generate triples
g.add((cdt.College, code.hasCode, cdt.level4ISCEDCode))

g.add((cdt.level4ISCEDCode, RDF.type, cdt.ISCEDCode))

g.add((cdt.level4ISCEDCode, genprop.hasName, Literal("4 Post-secondary non-tertiary education")))
g.add((cdt.level4ISCEDCode, genprop.hasDescription, Literal("Programmes providing learning experiences that build on secondary education and prepare for labour market entry or tertiary education.")))

g.add((cdt.College, rdfs.subClassOf, gcie.EducationFacility))

# Generate triples for each instance
for element in amenity["features"]:
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
    
    g.add((cdt[instancename], RDF.type, cdt.College))

# Export the RDF graph as a .ttl file
g.serialize(destination="College.ttl")





