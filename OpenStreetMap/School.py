# -*- coding: utf-8 -*-
"""
School.py

Author: Anderson Wong

Date: March 6, 2025

Description: This is a Python program that generates RDF triples 
for schools using OpenStreetMap data in a geojson file.
    
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

g.add((contact.workPhone, RDF.type, contact.PhoneType))
g.add((contact.faxPhone, RDF.type, contact.PhoneType))

# Generate triples for CompleteCommunityAmneity superclass and displayColor
g.add((gcie.School, rdfs.subClassOf, cdt.CompleteCommunityAmenity))
g.add((gcie.School, cdt.displayColor, Literal("#4287f5")))

# Generate triples for displayProperties
g.add((gcie.School, cdt.displayProperties, genprop.hasName))
g.add((gcie.School, cdt.displayProperties, gcie.hasOwnership))
g.add((gcie.School, cdt.displayProperties, cdt.website))
g.add((gcie.School, cdt.displayProperties, cdt.languageOfInstruction))
g.add((gcie.School, cdt.displayProperties, cdt.religion))
g.add((gcie.School, cdt.displayProperties, contact.hasTelephone))
g.add((gcie.School, cdt.displayProperties, cdt.operator))
g.add((gcie.School, cdt.displayProperties, cdt.osmID))
g.add((gcie.School, cdt.displayProperties, contact.hasAddress))

g.add((contact.PhoneNumber, cdt.displayProperties, contact.hasCountryCode))
g.add((contact.PhoneNumber, cdt.displayProperties, contact.hasAreaCode))
g.add((contact.PhoneNumber, cdt.displayProperties, contact.hasPhoneNumber))
g.add((contact.PhoneNumber, cdt.displayProperties, contact.hasPhoneType))

# Generate triples for each instance
for element in amenity["features"]:
    # Inititalize variables
    osmid = re.sub("[^0-9]", "", element["id"])
    instancename = osmid + amenityname
    addressname = instancename + "Address"
    telephonename = instancename + "Telephone"
    faxname = instancename + "Faxphone"
    streetname = ""
    
    # Generate triples for school instance
    g.add((cdt[instancename], loc.hasLocation, cdt[instancename + "Location"]))
    g.add((cdt[instancename], gci.forCity, toronto.toronto))
    g.add((cdt[instancename], cdt.osmID, Literal(osmid)))
    
    # Generate triples for location instance
    g.add((cdt[instancename + "Location"], RDF.type, loc.Location)) 
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
        g.add((cdt[instancename], cdt.languageOfInstruction, Literal(element['properties']['school:language'])))
    except:
        pass
    try:    
        g.add((cdt[instancename], cdt.religion, Literal(element['properties']['religion'])))
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
    
    # Generate triples for fax number information
    try:
        faxnumber = phonenumbers.parse(element['properties']['fax'], None)
        g.add((cdt[instancename], contact.hasTelephone, cdt[faxname]))
        g.add((cdt[faxname], RDF.type, contact.PhoneNumber))
        g.add((cdt[faxname], contact.hasCountryCode, Literal(faxnumber.country_code)))
        g.add((cdt[faxname], contact.hasAreaCode, Literal(int(str(faxnumber.national_number)[:3]))))
        g.add((cdt[faxname], contact.hasPhoneNumber, Literal(int(str(faxnumber.national_number)[3:]))))
        g.add((cdt[faxname], contact.hasPhoneType, contact.faxPhone))
    except:
        pass
    
    # Assign school type based on ISCED level and operator type
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

            

# Export the RDF graph as a .ttl file    
g.serialize(destination="Schools.ttl")





