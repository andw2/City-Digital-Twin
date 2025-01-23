# -*- coding: utf-8 -*-
"""
School.py

Author: Anderson Wong

Date: January 10, 2025

Description: This is a Python program that generates RDF triples 
for schools using OpenStreetMap data in a geojson file.
    
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
amenityname = "School"

# Get the data
amenity = json.loads(open(filename, encoding='utf8').read())

# Generate triples
g.add((gcie.PublicPrimarySchool, code.hasCode, cdt.level1ISCEDCode))
g.add((gcie.PublicPrimarySchool, gcie.delivers_Program, gcie.GradeLevelPrimaryOntario))
g.add((gcie.PrivatePrimarySchool, code.hasCode, cdt.level1ISCEDCode))
g.add((gcie.PrivatePrimarySchool, gcie.delivers_Program, gcie.GradeLevelPrimaryOntario))

g.add((gcie.GradeLevelPrimaryOntario, gcie.starting_Grade, gcie.GradeOne))
g.add((gcie.GradeLevelPrimaryOntario, gcie.ending_Grade, gcie.GradeSix))

g.add((gcie.PublicMiddleSchool, code.hasCode, cdt.level2ISCEDCode))
g.add((gcie.PublicMiddleSchool, gcie.delivers_Program, gcie.GradeLevelMiddleOntario))
g.add((gcie.PrivateMiddleSchool, code.hasCode, cdt.level2ISCEDCode))
g.add((gcie.PrivateMiddleSchool, gcie.delivers_Program, gcie.GradeLevelMiddleOntario))

g.add((gcie.GradeLevelMiddleOntario, gcie.starting_Grade, gcie.GradeSeven))
g.add((gcie.GradeLevelMiddleOntario, gcie.ending_Grade, gcie.GradeEight))

g.add((gcie.PublicSecondarySchool, code.hasCode, cdt.level3ISCEDCode))
g.add((gcie.PublicSecondarySchool, gcie.delivers_Program, gcie.GradeLevelSecondaryOntario))
g.add((gcie.PrivateSecondarySchool, code.hasCode, cdt.level3ISCEDCode))
g.add((gcie.PrivateSecondarySchool, gcie.delivers_Program, gcie.GradeLevelSecondaryOntario))

g.add((gcie.GradeLevelSecondaryOntario, gcie.starting_Grade, gcie.GradeNine))
g.add((gcie.GradeLevelSecondaryOntario, gcie.ending_Grade, gcie.GradeTwelve))

g.add((cdt.ISCEDCode, rdfs.subClassOf, code.Code))
g.add((cdt.level1ISCEDCode, RDF.type, cdt.ISCEDCode))
g.add((cdt.level2ISCEDCode, RDF.type, cdt.ISCEDCode))
g.add((cdt.level3ISCEDCode, RDF.type, cdt.ISCEDCode))

g.add((cdt.level1ISCEDCode, genprop.hasName, Literal("1 Primary Education")))
g.add((cdt.level1ISCEDCode, genprop.hasDescription, Literal("Programmes typically designed to provide students with fundamental skills in reading, writing and mathematics and to establish a solid foundation for learning.")))
g.add((cdt.level2ISCEDCode, genprop.hasName, Literal("2 Lower Secondary Education")))
g.add((cdt.level2ISCEDCode, genprop.hasDescription, Literal("First stage of secondary education building on primary education, typically with a more subject-oriented curriculum.")))
g.add((cdt.level3ISCEDCode, genprop.hasName, Literal("3 Upper Secondary Education")))
g.add((cdt.level3ISCEDCode, genprop.hasDescription, Literal("Second/final stage of secondary education preparing for tertiary education or providing skills relevant to employment. Usually with an increased range of subject options and streams.")))

g.add((gcie.PublicPrimarySchool, rdfs.subClassOf, gcie.PublicSchool))
g.add((gcie.PublicMiddleSchool, rdfs.subClassOf, gcie.PublicSchool))
g.add((gcie.PublicSecondarySchool, rdfs.subClassOf, gcie.PublicSchool))

g.add((gcie.PrivatePrimarySchool, rdfs.subClassOf, gcie.PrivateSchool))
g.add((gcie.PrivateMiddleSchool, rdfs.subClassOf, gcie.PrivateSchool))
g.add((gcie.PrivateSecondarySchool, rdfs.subClassOf, gcie.PrivateSchool))

g.add((gcie.PublicSchool, rdfs.subClassOf, gcie.School))
g.add((gcie.PrivateSchool, rdfs.subClassOf, gcie.School))

# Generate triples for each instance
for element in amenity["features"]:
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + amenityname
    
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
    
    try:
        print(element['properties']['operator:type'])
    except:
        g.add((cdt[instancename], RDF.type, gcie.School))
    else:
        if element['properties']['operator:type'] == "public":
            g.add((cdt[instancename], gcie.hasOwnership, Literal("public")))
            try:
                print(element['properties']['isced:level'])
            except:
                g.add((cdt[instancename], RDF.type, gcie.PublicSchool))
            else:
                if "1" in element['properties']['isced:level']:
                    g.add((cdt[instancename], RDF.type, gcie.PublicPrimarySchool))
                if "2" in element['properties']['isced:level']:
                    g.add((cdt[instancename], RDF.type, gcie.PublicMiddleSchool))
                if "3" in element['properties']['isced:level']:
                    g.add((cdt[instancename], RDF.type, gcie.PublicSecondarySchool))
        elif element['properties']['operator:type'] == "private":
            g.add((cdt[instancename], gcie.hasOwnership, Literal("private")))
            try:
                print(element['properties']['isced:level'])
            except:
                g.add((cdt[instancename], RDF.type, gcie.PrivateSchool))
            else:
                if "1" in element['properties']['isced:level']:
                    g.add((cdt[instancename], RDF.type, gcie.PrivatePrimarySchool))
                if "2" in element['properties']['isced:level']:
                    g.add((cdt[instancename], RDF.type, gcie.PrivateMiddleSchool))
                if "3" in element['properties']['isced:level']:
                    g.add((cdt[instancename], RDF.type, gcie.PrivateSecondarySchool))

    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location))

# Export the RDF graph as a .ttl file    
g.serialize(destination="Schools.ttl")





