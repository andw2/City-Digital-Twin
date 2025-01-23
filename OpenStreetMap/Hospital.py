# -*- coding: utf-8 -*-
"""
Hospital.py

Author: Anderson Wong

Date: January 16, 2025

Description: This is a Python program that generates RDF triples 
for hospitals using OpenStreetMap data in a geojson file.
    
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
sc = rdflib.Namespace('http://schema.org/')
gcih = rdflib.Namespace('http://ontology.eil.utoronto.ca/GCI/Health/GCI-Health.owl#')

# Create RDF graph
g = Graph()

# Initialize variables
filename = "hospital.geojson"
amenityname = "Hospital"
codename = "hospitalOSMCode"
codeclass = "AmenityOSMCode"

# Get the data
amenity = json.loads(open(filename, encoding='utf8').read())

# Generate triples
g.add((cdt[amenityname], code.hasCode, cdt[codename]))
g.add((cdt[codename], RDF.type, cdt[codeclass]))
g.add((cdt[codeclass], rdfs.subClassOf, code.Code))

g.add((cdt[codename], genprop.hasName, Literal("amenity=hospital")))
g.add((cdt[codename], genprop.hasDescription, Literal("A hospital providing in-patient medical treatment")))

g.add((gcih.PublicHospital, rdfs.subClassOf, sc.Hospital))
g.add((gcih.PrivateHospital, rdfs.subClassOf, sc.Hospital))

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
    
    try:
        print(element['properties']['operator:type'])
    except:
        g.add((cdt[instancename], RDF.type, sc.Hospital))
    else:
        if "public" in element['properties']['operator:type']:
            g.add((cdt[instancename], RDF.type, gcih.PublicHospital))
        if "private" in element['properties']['operator:type']:
            g.add((cdt[instancename], RDF.type, gcih.PrivateHospital))

# Export the RDF graph as a .ttl file
g.serialize(destination= amenityname + ".ttl")





