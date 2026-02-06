from neo4j import GraphDatabase

# Neo4j connection details
uri = "neo4j+s://858b3697.databases.neo4j.io"
user = "neo4j"
password = "H5Jf9TpR0fJONAATHL-zzYe8zi5DvnzDuL-yXO49SG4"

driver = GraphDatabase.driver(uri, auth=(user, password))

def reset_graph():
    with driver.session() as session:
        # 1. Delete all nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")

        # 2. Drop all constraints
        constraints = session.run("SHOW CONSTRAINTS")
        for record in constraints:
            name = record["name"]
            try:
                session.run(f"DROP CONSTRAINT {name}")
                print(f"Dropped constraint: {name}")
            except Exception as e:
                print(f"Failed to drop constraint {name}: {e}")

        # 3. Drop all indexes
        indexes = session.run("SHOW INDEXES")
        for record in indexes:
            name = record["name"]
            try:
                session.run(f"DROP INDEX {name}")
                print(f"Dropped index: {name}")
            except Exception as e:
                print(f"Failed to drop index {name}: {e}")

        print("✅ Graph reset complete.")

reset_graph()
driver.close()