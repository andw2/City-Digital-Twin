# -*- coding: utf-8 -*-
"""
Greengrocer.py

Author: Anderson Wong

Date: April 15, 2025

Description: This is a Python program that generates RDF triples 
for greengrocers using OpenStreetMap data in a geojson file.
    
"""

# Import modules
import rdflib
import json
import shapely
import re
import usaddress
import phonenumbers

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
contact = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-2/ed-1/en/ontology/Contact/')

# Create RDF graph
g = Graph()

# Initialize variables
filename = "greengrocer.geojson"
amenityname = "Greengrocer"
codename = "greengrocerOSMCode"

# Get the data
amenity = json.loads(open(filename, encoding='utf8').read())

# Generate triples
g.add((cdt[amenityname], code.hasCode, cdt[codename]))

g.add((cdt[codename], RDF.type, cdt.ShopOSMCode))

g.add((cdt[codename], genprop.hasName, Literal("shop=greengrocer")))
g.add((cdt[codename], genprop.hasDescription, Literal("A shop which sells fruits and vegetables")))

# Generate triples for CompleteCommunityAmneity superclass and displayColor
g.add((cdt.Greengrocer, rdfs.subClassOf, cdt.CompleteCommunityAmenity))
g.add((cdt.Greengrocer, cdt.displayColor, Literal("#f59042")))

# Generate triples for displayProperties
g.add((cdt.Greengrocer, cdt.displayProperties, genprop.hasName))
g.add((cdt.Greengrocer, cdt.displayProperties, cdt.website))
g.add((cdt.Greengrocer, cdt.displayProperties, contact.hasTelephone))
g.add((cdt.Greengrocer, cdt.displayProperties, cdt.osmID))
g.add((cdt.Greengrocer, cdt.displayProperties, contact.hasAddress))
g.add((cdt.Greengrocer, cdt.displayProperties, cdt.wheelchairAccess))
g.add((cdt.Greengrocer, cdt.displayProperties, cdt.openingHours))

# Generate triples for each instance
for element in amenity["features"]:
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + amenityname
    addressname = instancename + "Address"
    telephonename = instancename + "Telephone"
    streetname = ""
    
    g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))

    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location))
    
    g.add((cdt[instancename], RDF.type, cdt[amenityname]))

    # Generate triples for optional properties
    try:    
        g.add((cdt[instancename], genprop.hasName, Literal(element['properties']['name'])))
    except:
        pass
    try:    
        g.add((cdt[instancename], cdt.website, Literal(element['properties']['website'])))
    except:
        pass
    try:    
        g.add((cdt[instancename], cdt.wheelchairAccess, Literal(element['properties']['wheelchair'])))
    except:
        pass
    try:    
        g.add((cdt[instancename], cdt.openingHours, Literal(element['properties']['opening_hours'])))
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
    
    # Generate triples for telephone number information
    try:
        phonenumber = phonenumbers.parse(element['properties']['phone'], None)
        g.add((cdt[instancename], contact.hasTelephone, cdt[telephonename]))
        g.add((cdt[telephonename], RDF.type, contact.PhoneNumber))
        g.add((cdt[telephonename], contact.hasCountryCode, Literal(phonenumber.country_code)))
        g.add((cdt[telephonename], contact.hasAreaCode, Literal(int(str(phonenumber.national_number)[:3]))))
        g.add((cdt[telephonename], contact.hasPhoneNumber, Literal(int(str(phonenumber.national_number)[3:]))))
        g.add((cdt[telephonename], contact.hasPhoneType, contact.workPhone))
    except:
        pass

# Export the RDF graph as a .ttl file
g.serialize(destination= amenityname + ".ttl")





