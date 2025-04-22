# -*- coding: utf-8 -*-
"""
Park.py

Author: Anderson Wong

Date: March 6, 2025

Description: This is a Python program that generates RDF triples 
for parks using OpenStreetMap data in a geojson file.
    
"""
# Import modules
import rdflib
import json
import shapely
import re
import usaddress
from pyproj import Geod

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
contact = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-2/ed-1/en/ontology/Contact/')
cityunits = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-1/ed-1/en/ontology/CityUnits/')
iso21972 = rdflib.Namespace('http://ontology.eil.utoronto.ca/ISO21972/iso21972#')
schema = rdflib.Namespace('http://schema.org/')

# Create RDF graph
g = Graph()

# Get the data
parks = json.loads(open('park.geojson', encoding='utf8').read())

# Generate triples for Code
g.add((gcir.Park, code.hasCode, cdt.parkOSMCode))
g.add((gcir.parkOSMCode, RDF.type, cdt.LeisureOSMCode))
g.add((cdt.parkOSMCode, genprop.hasName, Literal("leisure=park")))
g.add((cdt.parkOSMCode, genprop.hasDescription, Literal("A park, usually in an urban (municipal) setting, created for recreation and relaxation. ")))
g.add((cdt.LeisureOSMCode, rdfs.subClassOf, code.Code))

# Generate triples for CompleteCommunityAmneity superclass and displayColor
g.add((gcir.Park, rdfs.subClassOf, cdt.CompleteCommunityAmenity))
g.add((gcir.Park, cdt.displayColor, Literal("#24b34a")))

# Generate triples for displayProperties
g.add((gcir.Park, cdt.displayProperties, genprop.hasName))
g.add((gcir.Park, cdt.displayProperties, cdt.lit))
g.add((gcir.Park, cdt.displayProperties, cdt.website))
g.add((gcir.Park, cdt.displayProperties, cdt.openingHours))
g.add((gcir.Park, cdt.displayProperties, cdt.surface))
g.add((gcir.Park, cdt.displayProperties, cdt.operatorType))
g.add((gcir.Park, cdt.displayProperties, cdt.operator))
g.add((gcir.Park, cdt.displayProperties, cdt.osmID))
g.add((gcir.Park, cdt.displayProperties, cityunits.hasArea))
g.add((gcir.Park, cdt.displayProperties, contact.hasAddress))

g.add((contact.Address, cdt.displayProperties, contact.hasUnitNumber))
g.add((contact.Address, cdt.displayProperties, contact.hasStreet))
g.add((contact.Address, cdt.displayProperties, contact.hasStreetType))
g.add((contact.Address, cdt.displayProperties, contact.hasStreetDirection))
g.add((contact.Address, cdt.displayProperties, contact.hasStreetNumber))
g.add((contact.Address, cdt.displayProperties, contact.hasBuilding))
g.add((contact.Address, cdt.displayProperties, contact.hasPostalBox))
g.add((contact.Address, cdt.displayProperties, contact.hasPostalCode))
g.add((contact.Address, cdt.displayProperties, contact.hasCity))
g.add((contact.Address, cdt.displayProperties, contact.hasProvince))
g.add((contact.Address, cdt.displayProperties, contact.hasCountry))

g.add((cityunits.Area, cdt.displayProperties, iso21972.value))

g.add((iso21972.Measure, cdt.displayProperties, iso21972.numerical_value))

# Generate an instance for Ontario and Canada
g.add((cdt.ontario, RDF.type, schema.State))
g.add((cdt.canada, RDF.type, schema.Country))

# Generate triples for each park
for element in parks["features"]:
    # Initialize variables
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + "Park"
    addressname = instancename + "Address"
    areaname = instancename + "Area"
    areameasurename = areaname + "Measure"
    streetname = ""
    
    # Generate triples for park instance
    g.add((cdt[instancename], RDF.type, gcir.Park))
    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    
    # Calculate surface area
    polygon = shapely.geometry.shape(element["geometry"])
    geod = Geod(ellps="WGS84")
    poly_area, poly_perimeter = geod.geometry_area_perimeter(polygon)
    
    # Generate triples for surface area
    g.add((cdt[areaname], RDF.type, cityunits.Area))
    g.add((cdt[areameasurename], RDF.type, iso21972.Measure))
    g.add((cdt[instancename], cityunits.hasArea, cdt[areaname]))
    g.add((cdt[areaname], iso21972.value, cdt[areameasurename]))
    g.add((cdt[areameasurename], iso21972.unit_of_measure, iso21972.square_metre))
    g.add((cdt[areameasurename], iso21972.numerical_value, Literal(poly_area)))
    
    # Generate triple for osmID property
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    # Generate triple for location instance
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location))
    
    # Generate triple for asWKT property
    g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))
    
    # Generate triples for optional properties
    try:    
        g.add((cdt[instancename], genprop.hasName, Literal(element['properties']['name'])))
    except:
        pass
    try: 
        g.add((cdt[instancename], cdt.openingHours, Literal(element['properties']['opening_hours'])))
    except:
        pass
    try: 
        g.add((cdt[instancename], cdt.website, Literal(element['properties']['website'])))
    except:
        pass
    try: 
        g.add((cdt[instancename], cdt.lit, Literal(element['properties']['lit'])))
    except:
        pass
    try: 
        g.add((cdt[instancename], cdt.operator, Literal(element['properties']['operator'])))
    except:
        pass
    try: 
        g.add((cdt[instancename], cdt.operatorType, Literal(element['properties']['operator:type'])))
    except:
        pass
    try: 
        g.add((cdt[instancename], cdt.surface, Literal(element['properties']['surface'])))
    except:
        pass
    
    # Generate triples for address information
    try:
        street = usaddress.tag(element['properties']['addr:street'])
        try:
            streetname += street[0]["StreetNamePreModifier"]
        except: 
            pass
        try:
            streetname += street[0]["StreetNamePreDirectional"]
        except: 
            pass
        streetname += street[0]["StreetName"]
        g.add((cdt[addressname], contact.hasStreet, Literal(streetname)))
        try:
            g.add((cdt[addressname], contact.hasStreetType, contact[street[0]["StreetNamePostType"].lower()]))
        except:
            pass
        try:
            g.add((cdt[addressname], contact.hasStreetDirection, contact[street[0]["StreetNamePostDirectional"].lower()]))
        except:
            pass
        g.add((cdt[addressname], contact.hasCity, toronto.toronto))
        g.add((cdt[addressname], contact.hasProvince, cdt.ontario))
        g.add((cdt[addressname], contact.hasCountry, cdt.canada))
        g.add((cdt[addressname], RDF.type, contact.Address))
        g.add((cdt[instancename], contact.hasAddress, cdt[addressname]))
    except:
        pass
    try:
        g.add((cdt[addressname], contact.hasStreetNumber, Literal(element['properties']['addr:housenumber'])))
    except:
        pass
    try:
        g.add((cdt[addressname], contact.hasPostalCode, Literal(element['properties']['addr:postcode'])))
    except:
        pass

# Export the RDF graph as a .ttl file
g.serialize(destination="Parks2.ttl")





