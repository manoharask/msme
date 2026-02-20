"""
Graph Database Reset Script for IndiaAI Innovation Challenge 2026
Safely clears all data and prepares database for fresh seed

IMPORTANT: This script will DELETE ALL DATA in your Neo4j database.
Use only when you want to completely reset and re-seed.

Usage:
    python reset_graph.py
"""
import os
import tomllib
from pathlib import Path
from neo4j import GraphDatabase


def load_config():
    """Load credentials from .streamlit/secrets.toml, falling back to env vars."""
    secrets_path = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with open(secrets_path, "rb") as f:
            secrets = tomllib.load(f)
        os.environ.setdefault("NEO4J_URI", secrets.get("NEO4J_URI", ""))
        os.environ.setdefault("NEO4J_USERNAME", secrets.get("NEO4J_USERNAME", ""))
        os.environ.setdefault("NEO4J_PASSWORD", secrets.get("NEO4J_PASSWORD", ""))
    return {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USERNAME"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    }


def reset_graph(driver):
    """
    Complete graph database reset:
    1. Delete all nodes and relationships
    2. Drop all constraints
    3. Drop all indexes
    """
    with driver.session() as session:
        print("🗑️  Starting graph database reset...\n")
        
        # Step 1: Count existing data
        print("📊 Current database state:")
        node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
        print(f"   • Nodes: {node_count}")
        print(f"   • Relationships: {rel_count}\n")
        
        if node_count == 0 and rel_count == 0:
            print("ℹ️  Database is already empty. Skipping node deletion.\n")
        else:
            # Step 2: Delete all nodes and relationships
            print("🔥 Deleting all nodes and relationships...")
            session.run("MATCH (n) DETACH DELETE n")
            print("   ✅ All data deleted\n")
        
        # Step 3: Drop all constraints
        print("🔓 Dropping all constraints...")
        try:
            constraints = list(session.run("SHOW CONSTRAINTS"))
            if not constraints:
                print("   ℹ️  No constraints found\n")
            else:
                for record in constraints:
                    name = record["name"]
                    try:
                        session.run(f"DROP CONSTRAINT {name}")
                        print(f"   ✅ Dropped constraint: {name}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to drop constraint {name}: {e}")
                print()
        except Exception as e:
            print(f"   ⚠️  Could not list constraints: {e}\n")
        
        # Step 4: Drop all indexes
        print("📑 Dropping all indexes...")
        try:
            indexes = list(session.run("SHOW INDEXES"))
            if not indexes:
                print("   ℹ️  No indexes found\n")
            else:
                dropped_count = 0
                for record in indexes:
                    name = record["name"]
                    # Skip token lookup indexes (system-managed)
                    if "token" in name.lower() or "lookup" in name.lower():
                        continue
                    try:
                        session.run(f"DROP INDEX {name}")
                        print(f"   ✅ Dropped index: {name}")
                        dropped_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Failed to drop index {name}: {e}")
                
                if dropped_count == 0:
                    print("   ℹ️  No user-created indexes to drop\n")
                else:
                    print()
        except Exception as e:
            print(f"   ⚠️  Could not list indexes: {e}\n")
        
        # Verify cleanup
        print("✅ Verifying cleanup...")
        final_node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
        final_rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
        
        if final_node_count == 0 and final_rel_count == 0:
            print("   ✅ Database is completely clean\n")
        else:
            print(f"   ⚠️  Warning: {final_node_count} nodes and {final_rel_count} relationships remain\n")


def main():
    print("=" * 70)
    print("🔄 NEO4J GRAPH DATABASE RESET UTILITY")
    print("=" * 70)
    print("\n⚠️  WARNING: This will DELETE ALL DATA in your Neo4j database!")
    print("   • All MSE nodes")
    print("   • All SNP nodes")
    print("   • All Category nodes")
    print("   • All relationships")
    print("   • All indexes and constraints")
    
    # Safety confirmation
    print("\n" + "=" * 70)
    response = input("Are you sure you want to proceed? Type 'YES' to confirm: ")
    
    if response.strip().upper() != "YES":
        print("\n❌ Reset cancelled. No changes made to database.\n")
        return
    
    print("\n" + "=" * 70)
    
    # Load config and connect
    cfg = load_config()
    
    # Display connection info (hide password)
    print(f"\n🔌 Connecting to Neo4j:")
    print(f"   • URI: {cfg['NEO4J_URI']}")
    print(f"   • User: {cfg['NEO4J_USER']}")
    print(f"   • Password: {'*' * len(cfg['NEO4J_PASSWORD'])}\n")
    
    try:
        driver = GraphDatabase.driver(
            cfg["NEO4J_URI"],
            auth=(cfg["NEO4J_USER"], cfg["NEO4J_PASSWORD"])
        )
        
        # Test connection
        driver.verify_connectivity()
        print("✅ Successfully connected to Neo4j\n")
        
        # Perform reset
        reset_graph(driver)
        
        driver.close()
        
        print("=" * 70)
        print("✅ GRAPH DATABASE RESET COMPLETE!")
        print("=" * 70)
        print("\n📝 Next Steps:")
        print("   1. Run: python seed_graph.py")
        print("   2. This will create:")
        print("      • 35 Categories with ONDC mapping")
        print("      • 25 SNPs with rich metadata")
        print("      • 6 Database indexes for performance")
        print("\n💡 Tip: After seeding, verify with:")
        print("   MATCH (n) RETURN labels(n), count(n)")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to Neo4j")
        print(f"   {str(e)}\n")
        print("🔍 Troubleshooting:")
        print("   1. Check your .env file has correct credentials:")
        print("      NEO4J_URI=bolt://localhost:7687")
        print("      NEO4J_USERNAME=neo4j")
        print("      NEO4J_PASSWORD=your_password")
        print("   2. Ensure Neo4j is running (http://localhost:7474)")
        print("   3. Verify network connectivity if using cloud Neo4j\n")


if __name__ == "__main__":
    main()
