import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


def load_config():
    load_dotenv()
    return {
        "NEO4J_URI": os.getenv("NEO4J_URI"),
        "NEO4J_USER": os.getenv("NEO4J_USERNAME"),
        "NEO4J_PASSWORD": os.getenv("NEO4J_PASSWORD"),
    }


def seed_categories(session):
    categories = [
        ("TX001", "Textiles", "Manufacturing", ["textile", "fabric", "cotton", "shirt", "uniform"]),
        ("LE001", "Leather Goods", "Manufacturing", ["leather", "belt", "wallet", "bag", "footwear"]),
        ("FD001", "Food Processing", "Processing", ["food", "snack", "spice", "masala", "dry fruit"]),
        ("AG001", "Agri Products", "Agriculture", ["agri", "seed", "grain", "fertilizer", "pulses"]),
        ("HM001", "Handicrafts", "Crafts", ["handicraft", "craft", "art", "decor"]),
        ("EL001", "Electronics Components", "Electronics", ["electronics", "circuit", "pcb", "component"]),
        ("PH001", "Pharmaceuticals", "Healthcare", ["pharma", "pharmaceutical", "pharmaceuticals", "tablet", "tablets", "capsule", "medicine", "drug", "दवा", "दवाई", "टैबलेट", "कैप्सूल", "फार्मा", "फार्मास्यूटिकल", "औषधि"]),
        ("CH001", "Chemicals", "Manufacturing", ["chemical", "chemicals", "solvent"]),
        ("PL001", "Plastics", "Manufacturing", ["plastic", "polymer", "moulding"]),
        ("MT001", "Metal Works", "Manufacturing", ["metal", "steel", "iron", "forging"]),
        ("WO001", "Wood Products", "Manufacturing", ["wood", "timber", "plywood"]),
        ("PA001", "Packaging", "Manufacturing", ["packaging", "box", "carton", "label"]),
        ("AU001", "Auto Parts", "Automotive", ["auto", "automotive", "spare", "parts"]),
        ("RE001", "Renewable Energy", "Energy", ["solar", "renewable", "wind", "inverter"]),
        ("CO001", "Construction Materials", "Construction", ["construction", "cement", "brick", "tiles"]),
        ("PC001", "Personal Care", "FMCG", ["personal care", "cosmetic", "soap", "shampoo"]),
        ("SP001", "Sports Goods", "Manufacturing", ["sports", "ball", "bat", "equipment"]),
        ("FU001", "Furniture", "Manufacturing", ["furniture", "chair", "table", "sofa"]),
        ("ST001", "Stationery", "FMCG", ["stationery", "paper", "notebook", "pen", "pencil", "file"]),
        ("JE001", "Jewelry", "Manufacturing", ["jewelry", "gold", "silver", "ornament"]),
    ]
    for code, name, sector, keywords in categories:
        session.run(
            "MERGE (c:Category {code: $code}) "
            "SET c.name = $name, c.sector = $sector, c.keywords = $keywords",
            code=code,
            name=name,
            sector=sector,
            keywords=keywords,
        )


def seed_snps(session):
    snps = [
        ("SNP001", "TextileHub Bengaluru", "Bengaluru", 0.92, 200, 12.97, 77.59, ["TX001", "ST001"]),
        ("SNP002", "LeatherWorks Chennai", "Chennai", 0.95, 250, 13.08, 80.27, ["LE001"]),
        ("SNP003", "AgriConnect Pune", "Pune", 0.88, 180, 18.52, 73.86, ["AG001", "FD001"]),
        ("SNP004", "CraftLine Jaipur", "Jaipur", 0.86, 140, 26.91, 75.79, ["HM001", "JE001"]),
        ("SNP005", "ElectroServe Noida", "Noida", 0.91, 220, 28.53, 77.39, ["EL001"]),
        ("SNP006", "PharmaLink Hyderabad", "Hyderabad", 0.93, 210, 17.39, 78.49, ["PH001"]),
        ("SNP007", "ChemEdge Ankleshwar", "Ankleshwar", 0.84, 160, 21.62, 73.00, ["CH001"]),
        ("SNP008", "PlastoFlex Rajkot", "Rajkot", 0.82, 150, 22.30, 70.80, ["PL001"]),
        ("SNP009", "MetalForge Jamshedpur", "Jamshedpur", 0.90, 240, 22.80, 86.20, ["MT001", "AU001"]),
        ("SNP010", "WoodCraft Mysuru", "Mysuru", 0.85, 130, 12.30, 76.65, ["WO001", "FU001"]),
        ("SNP011", "PackPro Surat", "Surat", 0.87, 170, 21.17, 72.83, ["PA001"]),
        ("SNP012", "AutoPart Hub Gurugram", "Gurugram", 0.89, 200, 28.46, 77.03, ["AU001"]),
        ("SNP013", "SolarEdge Jaipur", "Jaipur", 0.83, 160, 26.91, 75.79, ["RE001"]),
        ("SNP014", "BuildMate Indore", "Indore", 0.86, 190, 22.72, 75.86, ["CO001"]),
        ("SNP015", "CarePlus Lucknow", "Lucknow", 0.88, 150, 26.85, 80.95, ["PC001"]),
        ("SNP016", "Sportify Meerut", "Meerut", 0.84, 140, 28.98, 77.70, ["SP001"]),
        ("SNP017", "FurniCore Kochi", "Kochi", 0.85, 165, 9.93, 76.26, ["FU001"]),
        ("SNP018", "StationeryMart Kolkata", "Kolkata", 0.86, 155, 22.57, 88.36, ["ST001"]),
        ("SNP019", "JewelCraft Mumbai", "Mumbai", 0.90, 175, 19.07, 72.88, ["JE001"]),
        ("SNP020", "FreshFoods Nashik", "Nashik", 0.87, 160, 19.99, 73.79, ["FD001"]),
    ]
    for snp_id, name, city, rating, capacity, lat, lon, categories in snps:
        session.run(
            """
            MERGE (s:SNP {id: $id})
            SET s.name = $name, s.city = $city, s.rating = $rating,
                s.capacity = $capacity, s.lat = $lat, s.lon = $lon
            """,
            id=snp_id,
            name=name,
            city=city,
            rating=rating,
            capacity=capacity,
            lat=lat,
            lon=lon,
        )
        for code in categories:
            session.run(
                """
                MATCH (s:SNP {id: $id}), (c:Category {code: $code})
                MERGE (s)-[:SERVES]->(c)
                """,
                id=snp_id,
                code=code,
            )


def main():
    cfg = load_config()
    driver = GraphDatabase.driver(
        cfg["NEO4J_URI"], auth=(cfg["NEO4J_USER"], cfg["NEO4J_PASSWORD"])
    )
    with driver.session() as session:
        seed_categories(session)
        seed_snps(session)
    driver.close()
    print("Seeded 20 categories and 20 SNPs.")


if __name__ == "__main__":
    main()
