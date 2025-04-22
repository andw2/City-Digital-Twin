# -*- coding: utf-8 -*-
"""
Kindergarten.py

Author: Anderson Wong

Date: March 14, 2025

Description: This is a Python program that generates RDF triples 
for kindergartens using OpenStreetMap data in a geojson file.

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

# Generate triples for CompleteCommunityAmneity superclass and displayColor
g.add((cdt.Kindergarten, rdfs.subClassOf, cdt.CompleteCommunityAmenity))
g.add((cdt.Kindergarten, cdt.displayColor, Literal("#4287f5")))

# Generate triples for displayProperties
g.add((cdt.Kindergarten, cdt.displayProperties, genprop.hasName))
g.add((cdt.Kindergarten, cdt.displayProperties, cdt.website))
g.add((cdt.Kindergarten, cdt.displayProperties, contact.hasTelephone))
g.add((cdt.Kindergarten, cdt.displayProperties, cdt.operator))
g.add((cdt.Kindergarten, cdt.displayProperties, cdt.osmID))
g.add((cdt.Kindergarten, cdt.displayProperties, contact.hasAddress))

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
            addressname = instancename + "Address"
            telephonename = instancename + "Telephone"
            streetname = ""
            
            g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))
            
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
                g.add((cdt[instancename], cdt.operator, Literal(element['properties']['operator'])))
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
            g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
            g.add((cdt[instancename], gci.forCity, toronto.toronto))
            
            g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
            
            g.add((cdt[instancename + "Location"], RDF.type, loc.Location))
            
            g.add((cdt[instancename], RDF.type, cdt.Kindergarten))

for element in amenity2["features"]:
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + amenityname
    addressname = instancename + "Address"
    telephonename = instancename + "Telephone"
    streetname = ""
    
    g.add((cdt[instancename + "Location"], geo.asWKT, Literal(shapely.to_wkt(shapely.geometry.shape(element["geometry"])), datatype=geo.wktLiteral)))
    
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
        g.add((cdt[instancename], cdt.operator, Literal(element['properties']['operator'])))
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

    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location))
    
    g.add((cdt[instancename], RDF.type, cdt.Kindergarten))

# Export the RDF graph as a .ttl file
g.serialize(destination="Kindergartens.ttl")





