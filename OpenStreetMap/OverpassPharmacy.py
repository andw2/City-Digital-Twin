# -*- coding: utf-8 -*-

"""
OverpassPharmacy.py

Author: Anderson Wong

Date: January 23, 2025

Description: This is a Python program that generates neighborhood walking distance 
indicators for pharmacies using OpenStreetMap data.
    
"""

# Import modules
import time
import overpy
import sparql_dataframe
import shapely
import rdflib

from rdflib import Graph, Literal, XSD, RDF

# Declare namespaces
cdt = rdflib.Namespace('http://ontology.eil.utoronto.ca/CDT#')
rdfs = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
iso21972 = rdflib.Namespace('http://ontology.eil.utoronto.ca/ISO21972/iso21972#')
uoft = rdflib.Namespace('http://ontology.eil.utoronto.ca/tove/cacensus#')
toronto = rdflib.Namespace('http://ontology.eil.utoronto.ca/Toronto/Toronto#')
building = rdflib.Namespace('https://standards.iso.org/iso-iec/5087/-2/ed-1/en/ontology/Building/')

# Create RDF graph
g = Graph()

# Declare SPARQL Endpoint
endpoint = "http://ec2-3-97-59-180.ca-central-1.compute.amazonaws.com:7200/repositories/CACensus"

# Declare OpenStreetMap Overpass API
api = overpy.Overpass()

# Initialize variables
tag = "amenity=pharmacy"
amenity = "Pharmacy"
walkdistance = "400"

# SPARQL query the City Digital Twin for neighborhood polygons
q = """
PREFIX toronto: <http://ontology.eil.utoronto.ca/Toronto/Toronto#>
PREFIX iso50871: <http://ontology.eil.utoronto.ca/5087/1/SpatialLoc/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>

SELECT ?area ?coordinates

WHERE{
      ?area a toronto:Neighborhood;
      iso50871:hasLocation ?location.
      
      ?location geo:asWKT ?coordinates.
}
"""

# Save query results as a Pandas DataFrame object
df = sparql_dataframe.get(endpoint, q)

# Iterate for each neighborhood in the query result
for n in range(len(df)):
    
    # Initialize variables
    walkingdistancetotal = 0
    buildingtotal = 0
    
    # Get the neighborhood polygon in WKT format from the query result
    neighbourhood_polygon = df.iloc[n]["coordinates"]
    
    # Convert the WKT polygon coordinates to a Shapely Polygon
    poly = shapely.from_wkt(neighbourhood_polygon)
    
    # Check if polygon is a multipolygon
    if isinstance(poly, shapely.MultiPolygon):
        print("multipolygon")
        
        # Generates a list of polygons that comprise the multipolygon
        polygons = list(poly.geoms)
        
        # Iterate for each polygon in the polygon list
        for polygon in polygons:
            
            # Extract the x and y coordinates of the polygon
            xx, yy = polygon.exterior.coords.xy
            x = xx.tolist()
            y = yy.tolist()
            
            # Use the x and y coordinates to creates a list of xy coordinate pairs
            polylist = ""
            
            for i in range(len(x)):
                polylist += str(y[i]) + " " + str(x[i]) + " "
                
            polylist = polylist.rstrip()
            
            # Use OpenStreetMap's Overpass API to query for the number of residential 
            # buildings that are within walking distance of the amenity
            while True:
                try:
                    walkingdistanceresult = api.query("""
                    [out:json];
                    
                    (
                    nwr[building=apartments](poly:\"""" + polylist + """\");                        
                    nwr[building=detached](poly:\"""" + polylist + """\");         
                    nwr[building=house](poly:\"""" + polylist + """\");      
                    nwr[building=semidetached_house](poly:\"""" + polylist + """\");                                        
                    nwr[building=terrace](poly:\"""" + polylist + """\");          
                    nwr[building=residential](poly:\"""" + polylist + """\");                            
                    )->.buildings; 
                    
                    (
                      nwr[""" + tag + """](around.buildings:""" + walkdistance + """);
                    )->.amenity; 
                    
                    (
                      nwr.buildings(around.amenity:""" + walkdistance + """);
                    )->.buildingsNearAmenity; 
                    
                    .buildingsNearAmenity;
                    
                    out;""")
                except:
                    time.sleep(10)
                    continue
                break
                   
            # Use OpenStreetMap's Overpass API to query for the total number
            # of residential buildings 
            while True:
                try:
                    buildingresult = api.query("""
                    [out:json];
                    
                    (
                    nwr[building=apartments](poly:\"""" + polylist + """\");                        
                    nwr[building=detached](poly:\"""" + polylist + """\");         
                    nwr[building=house](poly:\"""" + polylist + """\");      
                    nwr[building=semidetached_house](poly:\"""" + polylist + """\");                                        
                    nwr[building=terrace](poly:\"""" + polylist + """\");          
                    nwr[building=residential](poly:\"""" + polylist + """\");                               
                    )->.buildings;  
                    
                    .buildings;
                    
                    out;
                                       """)
                except:
                    time.sleep(10)
                    continue
                break
            # Add the result of the queries to the current total
            walkingdistancetotal += len(walkingdistanceresult.nodes) + len(walkingdistanceresult.ways) + len(walkingdistanceresult.relations)
            buildingtotal +=  len(buildingresult.nodes) + len(buildingresult.ways) + len(buildingresult.relations)
            print(buildingtotal)
            print(walkingdistancetotal)
            
    else:
        print("polygon")
        
        # Extract the x and y coordinates of the polygon
        xx, yy = poly.exterior.coords.xy
        x = xx.tolist()
        y = yy.tolist()
        
        # Use the x and y coordinates to creates a list of xy coordinate pairs
        polylist = ""
        
        for i in range(len(x)):
            polylist += str(y[i]) + " " + str(x[i]) + " "
            
        polylist = polylist.rstrip()
        
        # Use OpenStreetMap's Overpass API to query for the number of residential 
        # buildings that are within walking distance of the amenity
        while True:
            try:
                walkingdistanceresult = api.query("""
                [out:json];
                
                (
                    nwr[building=apartments](poly:\"""" + polylist + """\");                        
                    nwr[building=detached](poly:\"""" + polylist + """\");         
                    nwr[building=house](poly:\"""" + polylist + """\");      
                    nwr[building=semidetached_house](poly:\"""" + polylist + """\");                                        
                    nwr[building=terrace](poly:\"""" + polylist + """\");          
                    nwr[building=residential](poly:\"""" + polylist + """\");                              
                )->.buildings; 
                
                (
                    nwr[""" + tag + """](around.buildings:""" + walkdistance + """);        
                )->.amenity; 
                
                (
                    nwr.buildings(around.amenity:""" + walkdistance + """);
                )->.buildingsNearAmenity; 
                
                .buildingsNearAmenity;
                
                out;
                                   """)
            except:
                time.sleep(10)
                continue
            break
                   
        # Use OpenStreetMap's Overpass API to query for the total number
        # of residential buildings
        while True:
            try:
                buildingresult = api.query("""
                [out:json];
                
                (
                    nwr[building=apartments](poly:\"""" + polylist + """\");                        
                    nwr[building=detached](poly:\"""" + polylist + """\");         
                    nwr[building=house](poly:\"""" + polylist + """\");      
                    nwr[building=semidetached_house](poly:\"""" + polylist + """\");                                        
                    nwr[building=terrace](poly:\"""" + polylist + """\");          
                    nwr[building=residential](poly:\"""" + polylist + """\");                                                           
                )->.buildings;  
                
                .buildings;
                
                out;
                                   """)
            except:
                time.sleep(10)
                continue
            break
                           
       # Add the result of the queries to the current total
        walkingdistancetotal += len(walkingdistanceresult.nodes) + len(walkingdistanceresult.ways) + len(walkingdistanceresult.relations)
        buildingtotal +=  len(buildingresult.nodes) + len(buildingresult.ways) + len(buildingresult.relations)
        print(buildingtotal)
        print(walkingdistancetotal)
    
    # Initialize variables
    neighbourhood = df.iloc[n]["area"].removeprefix('http://ontology.eil.utoronto.ca/Toronto/Toronto#')
    
    percentclass = "PercentWalkingDistance" + walkdistance + amenity
    percentindicator = neighbourhood + percentclass
    percentmeasure = percentindicator + "Measure"
    if buildingtotal == 0:
        percentvalue = 0
    else:
        percentvalue = walkingdistancetotal/buildingtotal
        print(round(percentvalue, 4))
        
    buildingclass = "NumberOfResidentialBuildings"
    buildingindicator = neighbourhood + buildingclass
    buildingmeasure = buildingindicator + "Measure"
    buildingvalue = buildingtotal
    buildingpopulation = buildingindicator + "Population"
    buildingpopulationclass = buildingclass + "Population"
    
    walkingclass = "NumberOfResidentialBuildingsWalkingDistance" + walkdistance + amenity
    walkingindicator = neighbourhood + walkingclass
    walkingmeasure = walkingindicator + "Measure"
    walkingvalue = walkingdistancetotal
    walkingpopulation = walkingindicator + "Population"
    walkingpopulationclass = walkingclass + "Population"
    
    # Generates triples that only need to be generated once
    if n == 0:
        percentsuperclass = "PercentWalkingDistance" + amenity
        
        g.add((cdt[percentclass], rdfs.subClassOf, cdt[percentsuperclass]))
        g.add((cdt[percentsuperclass], rdfs.subClassOf, iso21972.Indicator))
        g.add((cdt[percentclass], iso21972.numerator, cdt[walkingclass]))
        g.add((cdt[percentclass], iso21972.denominator, cdt[buildingclass]))
        g.add((cdt[percentclass], uoft.hasLocation, toronto.Neighbourhood))
        
        walkingsuperclass = "NumberOfResidentialBuildingsWalkingDistance" + amenity
        walkingdefineclass = "ResidentialBuildingWalkingDistance" + walkdistance + amenity
        walkingdefinesuperclass = "ResidentialBuildingWalkingDistance"  + amenity
        buildingdefineclass = "ResidentialBuilding"
        
        g.add((cdt[walkingclass], rdfs.subClassOf, cdt[walkingsuperclass]))
        g.add((cdt[walkingsuperclass], rdfs.subClassOf, iso21972.Indicator))
        g.add((cdt[walkingpopulationclass], rdfs.subClassOf, iso21972.Population))
        g.add((cdt[walkingpopulationclass], iso21972.defined_by, cdt[walkingdefineclass]))
        g.add((cdt[walkingdefineclass], rdfs.subClassOf, cdt[walkingdefinesuperclass]))
        g.add((cdt[walkingdefineclass], cdt.walkDistancePark, Literal("<=400")))
        g.add((cdt[walkingdefinesuperclass], rdfs.subClassOf, cdt[buildingdefineclass]))
        
    # Generates indicator triples for the current neighborhood
    g.add((cdt[percentindicator], RDF.type, cdt[percentclass]))
    g.add((cdt[percentindicator], uoft.hasLocation, toronto[neighbourhood]))
    g.add((cdt[percentindicator], iso21972.value, cdt[percentmeasure]))
    g.add((cdt[percentindicator], iso21972.hasUnit, iso21972.population_ratio_unit))
    g.add((cdt[percentmeasure], RDF.type, iso21972.Measure))
    g.add((cdt[percentmeasure], iso21972.numerical_value, Literal(round(percentvalue, 4), datatype=XSD.decimal)))
    g.add((cdt[percentmeasure], RDF.type, iso21972.Measure))
    g.add((cdt[percentindicator], iso21972.numerator, cdt[walkingindicator]))
    g.add((cdt[percentindicator], iso21972.denominator, cdt[buildingindicator]))
    
    
    g.add((cdt[walkingindicator], RDF.type, cdt[walkingclass]))
    g.add((cdt[walkingindicator], uoft.hasLocation, toronto[neighbourhood]))
    g.add((cdt[walkingindicator], iso21972.value, cdt[walkingmeasure]))
    g.add((cdt[walkingindicator], iso21972.hasUnit, iso21972.population_cardinality_unit))
    g.add((cdt[walkingindicator], iso21972.cardinality_of, cdt[walkingpopulation]))
    g.add((cdt[walkingpopulation], RDF.type, cdt[walkingpopulationclass]))
    g.add((cdt[walkingmeasure], iso21972.numerical_value, Literal(walkingvalue, datatype=XSD.integer)))
    g.add((cdt[walkingmeasure], RDF.type, iso21972.Measure))
    print(neighbourhood)
    print(n)

# Export the RDF graph as a .ttl file
filename = amenity + "WalkingDistance" + ".ttl"
g.serialize(destination=filename)
    
    
