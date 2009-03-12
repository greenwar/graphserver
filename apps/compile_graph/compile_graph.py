from graphserver.graphdb import GraphDatabase
from graphserver.ext.gtfs.gtfsdb import GTFSDatabase
from graphserver.ext.osm.osmdb import OSMDB
from graphserver import compiler
import sys
from sys import argv

def process_transit_graph(gtfsdb_filename, agency_id, graphdb_filename, link=False):
    gtfsdb = GTFSDatabase( gtfsdb_filename )
    
    g = Graph()
    service_ids = [x.encode("ascii") for x in gtfsdb.service_ids()]
    compiler.load_gtfsdb_to_boardalight_graph(g, gtfsdb, agency_id=agency_id, service_ids=service_ids)
    
    if link:
        compiler.link_nearby_stops( g, gtfsdb )
    
    graphdb = GraphDatabase( graphdb_filename, overwrite=True )
    graphdb.populate( g, reporter=sys.stdout )
    
def process_street_graph():
    OSMDB_FILENAME = "ext/osm/bartarea.sqlite"
    GRAPHDB_FILENAME = "bartstreets.db"
    
    print( "Opening OSM-DB '%s'"%OSMDB_FILENAME )
    osmdb = OSMDB( OSMDB_FILENAME )
    
    g = Graph()
    compiler.load_streets_to_graph( g, osmdb, sys.stdout )
    
    graphdb = GraphDatabase( GRAPHDB_FILENAME, overwrite=True )
    graphdb.populate( g, reporter=sys.stdout )
    
def process_transit_street_graph(graphdb_filename, gtfsdb_filename, osmdb_filename, agency_id=None):
    g = Graph()

    # Load gtfsdb ==============================
    
    gtfsdb = GTFSDatabase( gtfsdb_filename )
    service_ids = [x.encode("ascii") for x in gtfsdb.service_ids()]
    compiler.load_gtfsdb_to_boardalight_graph(g, gtfsdb, agency_id=agency_id, service_ids=service_ids)
    
    # Load osmdb ===============================
    
    print( "Opening OSM-DB '%s'"%osmdb_filename )
    osmdb = OSMDB( osmdb_filename )
    compiler.load_streets_to_graph( g, osmdb, sys.stdout )
    
    # Link osm to transit ======================
    
    compiler.load_transit_street_links_to_graph( g, osmdb, gtfsdb, reporter=sys.stdout )
    
    # Export to graphdb ========================
    
    graphdb = GraphDatabase( graphdb_filename, overwrite=True )
    graphdb.populate( g, reporter=sys.stdout )


if __name__=='__main__':

    usage = """usage: python compile_graph.py <link|conflate>"""
    
    if len(argv) < 2:
        print usage
        quit()
        
    mode = argv[1]
    
    if mode == "link":
        
        usage = "usage: python compile_graph.py link <gtfsdb_filename> <graphdb_filename>"
        
        if len(argv)<5:
            print usage
            quit()

        gtfsdb_filename = argv[3]
        graphdb_filename = argv[4]
            
        compiler.process_transit_graph( gtfsdb_filename, graphdb_filename, link=True )
            
    elif mode == "conflate":
        
        usage = "usage: python compile_graph.py conflate <graphdb_filename> <gtfsdb_filename> <osmdb_filename>"

        if len(argv)<5:
            print usage
            quit()

        graphdb_filename = argv[2]
        gtfsdb_filename = argv[3]
        osmdb_filename = argv[4]
     
        print "graphdb_filename: %s"%graphdb_filename
        print "gtfsdb_filename: %s"%gtfsdb_filename
        print "osmdb_filename: %s"%osmdb_filename

        compiler.process_transit_street_graph( graphdb_filename, gtfsdb_filename, osmdb_filename ) 
        