from neo4j import GraphDatabase

def delete_all_nodes_and_relationships(uri, username, password):
    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        # Delete all relationships
        session.run("MATCH ()-[r]->() DELETE r")
        
        # Delete all nodes
        session.run("MATCH (n) DELETE n")

    driver.close()

    print("All nodes and relationships have been deleted from the database.")

# Replace these with your Neo4j Aura connection details
uri = "neo4j+s://767773ef.databases.neo4j.io:7687"
username = "neo4j"
password = "OAy6La6vdETPz8dvAwVNVaYY30fiOrViFRPtAK88wHc"

delete_all_nodes_and_relationships(uri, username, password)
