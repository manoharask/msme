"""
Enhanced Seed Graph for IndiaAI Innovation Challenge 2026
Expanded taxonomy: 35 categories, 25 SNPs with rich metadata
"""
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
    """
    35 categories covering major MSME sectors with ONDC alignment
    Enhanced with 10-15 keywords per category, including Hindi terms
    """
    categories = [
        # Manufacturing - Textiles & Apparel
        ("TX001", "Textiles & Fabrics", "Manufacturing", 
         ["textile", "fabric", "cotton", "silk", "yarn", "weaving", "कपड़ा", "वस्त्र", "धागा", "बुनाई"],
         "Fashion", "Apparel", "Textiles & Fabrics"),
        
        ("AP001", "Apparel & Garments", "Manufacturing",
         ["shirt", "trouser", "dress", "garment", "clothing", "uniform", "कमीज", "कपड़े", "यूनिफॉर्म"],
         "Fashion", "Apparel", "Readymade Garments"),
        
        ("FT001", "Footwear", "Manufacturing",
         ["shoes", "footwear", "sandal", "chappal", "boot", "leather shoe", "जूते", "चप्पल", "सैंडल"],
         "Fashion", "Footwear", "Leather & Synthetic Footwear"),
        
        # Manufacturing - Leather
        ("LE001", "Leather Goods", "Manufacturing",
         ["leather", "belt", "wallet", "bag", "purse", "leather goods", "चमड़ा", "बेल्ट", "बैग"],
         "Fashion", "Accessories", "Leather Products"),
        
        # Food & Beverages
        ("FD001", "Food Processing", "Processing",
         ["food", "snack", "namkeen", "biscuit", "pickle", "papad", "खाद्य", "नमकीन", "बिस्कुट", "अचार"],
         "Food & Beverage", "Packaged Foods", "Snacks & Confectionery"),
        
        ("SP001", "Spices & Condiments", "Processing",
         ["spice", "masala", "turmeric", "chilli", "pepper", "garam masala", "मसाला", "हल्दी", "मिर्च"],
         "Food & Beverage", "Spices", "Ground Spices"),
        
        ("BV001", "Beverages", "Processing",
         ["juice", "beverage", "drink", "tea", "coffee", "soft drink", "जूस", "पेय", "चाय", "कॉफी"],
         "Food & Beverage", "Beverages", "Packaged Beverages"),
        
        # Agriculture
        ("AG001", "Agri Products", "Agriculture",
         ["agriculture", "seed", "grain", "fertilizer", "pulses", "wheat", "rice", "कृषि", "बीज", "अनाज"],
         "Agriculture", "Farm Inputs", "Seeds & Fertilizers"),
        
        ("OR001", "Organic Products", "Agriculture",
         ["organic", "natural", "chemical-free", "bio", "organic farming", "जैविक", "प्राकृतिक"],
         "Agriculture", "Organic Farming", "Certified Organic"),
        
        # Handicrafts & Jewelry
        ("HM001", "Handicrafts", "Crafts",
         ["handicraft", "craft", "handmade", "art", "decor", "pottery", "हस्तशिल्प", "कला", "मिट्टी के बर्तन"],
         "Home & Living", "Handicrafts", "Traditional Crafts"),
        
        ("JE001", "Jewelry & Ornaments", "Manufacturing",
         ["jewelry", "jewellery", "gold", "silver", "ornament", "necklace", "आभूषण", "सोना", "चांदी"],
         "Fashion", "Jewelry", "Fashion Jewelry"),
        
        # Electronics & Electrical
        ("EL001", "Electronics Components", "Electronics",
         ["electronics", "circuit", "pcb", "component", "resistor", "capacitor", "इलेक्ट्रॉनिक्स"],
         "Electronics", "Components", "Electronic Parts"),
        
        ("HA001", "Home Appliances", "Electronics",
         ["appliance", "fan", "mixer", "grinder", "heater", "गृह उपकरण", "पंखा", "मिक्सर"],
         "Electronics", "Home Appliances", "Small Appliances"),
        
        # Healthcare & Pharma
        ("PH001", "Pharmaceuticals", "Healthcare",
         ["pharma", "pharmaceutical", "tablet", "capsule", "medicine", "drug", "दवा", "दवाई", "टैबलेट", "कैप्सूल", "फार्मा", "औषधि"],
         "Health & Wellness", "Pharmaceuticals", "Generic Medicines"),
        
        ("AY001", "Ayurvedic Products", "Healthcare",
         ["ayurvedic", "ayurveda", "herbal", "natural medicine", "आयुर्वेद", "आयुर्वेदिक", "हर्बल", "जड़ी-बूटी"],
         "Health & Wellness", "Ayurveda", "Ayurvedic Medicines"),
        
        ("PC001", "Personal Care & Cosmetics", "FMCG",
         ["personal care", "cosmetic", "soap", "shampoo", "cream", "lotion", "साबुन", "शैम्पू", "क्रीम"],
         "Beauty & Personal Care", "Personal Care", "Skincare & Haircare"),
        
        # Chemicals & Materials
        ("CH001", "Chemicals", "Manufacturing",
         ["chemical", "chemicals", "solvent", "acid", "alkali", "रासायनिक", "सॉल्वेंट"],
         "Chemicals", "Industrial Chemicals", "Basic Chemicals"),
        
        ("PL001", "Plastics & Polymers", "Manufacturing",
         ["plastic", "polymer", "moulding", "pvc", "hdpe", "plastic product", "प्लास्टिक", "पॉलिमर"],
         "Plastics", "Plastic Products", "Moulded Plastics"),
        
        ("RU001", "Rubber Products", "Manufacturing",
         ["rubber", "latex", "tyre", "tube", "rubber product", "रबर", "लेटेक्स"],
         "Rubber", "Rubber Products", "Rubber Components"),
        
        # Metals & Engineering
        ("MT001", "Metal Works & Fabrication", "Manufacturing",
         ["metal", "steel", "iron", "forging", "fabrication", "welding", "धातु", "लोहा", "स्टील"],
         "Metals", "Metal Products", "Fabricated Metal"),
        
        ("AU001", "Auto Components", "Automotive",
         ["auto", "automotive", "spare parts", "components", "battery", "ऑटो", "पुर्जे", "बैटरी"],
         "Automotive", "Auto Parts", "Vehicle Components"),
        
        # Construction & Building
        ("CO001", "Construction Materials", "Construction",
         ["construction", "cement", "brick", "tiles", "marble", "निर्माण", "सीमेंट", "ईंट", "टाइल्स"],
         "Construction", "Building Materials", "Construction Supplies"),
        
        ("PA001", "Paints & Coatings", "Manufacturing",
         ["paint", "coating", "varnish", "enamel", "distemper", "पेंट", "रंग", "वार्निश"],
         "Construction", "Paints", "Decorative Paints"),
        
        # Wood & Furniture
        ("WO001", "Wood Products", "Manufacturing",
         ["wood", "timber", "plywood", "veneer", "लकड़ी", "प्लाईवुड"],
         "Home & Living", "Wood Products", "Timber & Plywood"),
        
        ("FU001", "Furniture", "Manufacturing",
         ["furniture", "chair", "table", "sofa", "cabinet", "bed", "फर्नीचर", "कुर्सी", "मेज"],
         "Home & Living", "Furniture", "Home Furniture"),
        
        # Packaging & Printing
        ("PK001", "Packaging Materials", "Manufacturing",
         ["packaging", "box", "carton", "label", "corrugated", "पैकेजिंग", "डिब्बा", "कार्टन"],
         "Packaging", "Packaging Materials", "Boxes & Cartons"),
        
        ("PR001", "Printing & Publishing", "Services",
         ["printing", "print", "publication", "book", "brochure", "मुद्रण", "प्रिंटिंग"],
         "Printing", "Printing Services", "Commercial Printing"),
        
        # Energy & Environment
        ("RE001", "Renewable Energy", "Energy",
         ["solar", "renewable", "wind", "inverter", "solar panel", "battery", "सौर", "नवीकरणीय ऊर्जा"],
         "Energy", "Renewable Energy", "Solar Products"),
        
        # Sports & Toys
        ("SG001", "Sports Goods", "Manufacturing",
         ["sports", "ball", "bat", "equipment", "cricket", "खेल", "गेंद", "बल्ला"],
         "Sports", "Sports Goods", "Sports Equipment"),
        
        ("TO001", "Toys & Games", "Manufacturing",
         ["toy", "toys", "game", "educational toy", "puzzle", "खिलौना", "खेल"],
         "Kids & Baby", "Toys", "Educational Toys"),
        
        # Stationery & Education
        ("ST001", "Stationery", "FMCG",
         ["stationery", "paper", "notebook", "pen", "pencil", "file", "स्टेशनरी", "कागज", "कॉपी"],
         "Stationery", "Office Supplies", "School Stationery"),
        
        # IT & Services
        ("IT001", "IT Services & Software", "Services",
         ["software", "it services", "web development", "app", "digital", "सॉफ्टवेयर", "वेब"],
         "IT Services", "Software Development", "Web & Mobile Apps"),
        
        # Glass & Ceramics
        ("GL001", "Glass & Ceramics", "Manufacturing",
         ["glass", "ceramic", "pottery", "tiles", "ceramic tiles", "कांच", "सिरेमिक"],
         "Home & Living", "Glass & Ceramics", "Ceramic Products"),
        
        # Safety & PPE
        ("SF001", "Safety Equipment & PPE", "Manufacturing",
         ["safety", "ppe", "helmet", "gloves", "mask", "safety equipment", "सुरक्षा उपकरण"],
         "Safety", "PPE", "Personal Protective Equipment"),
        
        # Agriculture Equipment
        ("AE001", "Agri Equipment & Tools", "Manufacturing",
         ["tractor", "plough", "agriculture equipment", "farm tools", "कृषि उपकरण", "हल"],
         "Agriculture", "Farm Equipment", "Agricultural Machinery"),
    ]
    
    for code, name, sector, keywords, ondc_l1, ondc_l2, ondc_l3 in categories:
        session.run(
            """
            MERGE (c:Category {code: $code})
            SET c.name = $name, 
                c.sector = $sector, 
                c.keywords = $keywords,
                c.ondc_l1 = $ondc_l1,
                c.ondc_l2 = $ondc_l2,
                c.ondc_l3 = $ondc_l3
            """,
            code=code,
            name=name,
            sector=sector,
            keywords=keywords,
            ondc_l1=ondc_l1,
            ondc_l2=ondc_l2,
            ondc_l3=ondc_l3,
        )


def seed_snps(session):
    """
    25 SNPs with enhanced metadata:
    - Certifications
    - Specialization
    - Export capability
    - Languages supported
    - Payment terms
    """
    snps = [
        {
            "id": "SNP001",
            "name": "TextileHub Bengaluru",
            "city": "Bengaluru",
            "rating": 0.92,
            "capacity": 200,
            "lat": 12.97,
            "lon": 77.59,
            "categories": ["TX001", "ST001", "AP001"],
            "certifications": ["ISO9001", "BIS"],
            "export_capable": True,
            "languages": ["en", "hi", "kn"],
            "payment_terms": "Net 30",
            "specialization": "Bulk textile manufacturing and export",
        },
        {
            "id": "SNP002",
            "name": "LeatherWorks Chennai",
            "city": "Chennai",
            "rating": 0.95,
            "capacity": 250,
            "lat": 13.08,
            "lon": 80.27,
            "categories": ["LE001", "FT001"],
            "certifications": ["ISO9001", "LWG"],
            "export_capable": True,
            "languages": ["en", "hi", "ta"],
            "payment_terms": "Net 45",
            "specialization": "Premium leather goods for export",
        },
        {
            "id": "SNP003",
            "name": "AgriConnect Pune",
            "city": "Pune",
            "rating": 0.88,
            "capacity": 180,
            "lat": 18.52,
            "lon": 73.86,
            "categories": ["AG001", "FD001", "OR001"],
            "certifications": ["FSSAI", "Organic Certified"],
            "export_capable": False,
            "languages": ["en", "hi", "mr"],
            "payment_terms": "Net 15",
            "specialization": "Organic agri products and food processing",
        },
        {
            "id": "SNP004",
            "name": "CraftLine Jaipur",
            "city": "Jaipur",
            "rating": 0.86,
            "capacity": 140,
            "lat": 26.91,
            "lon": 75.79,
            "categories": ["HM001", "JE001", "TX001"],
            "certifications": ["GI Tag", "Handicraft Mark"],
            "export_capable": True,
            "languages": ["en", "hi"],
            "payment_terms": "Net 30",
            "specialization": "Traditional Rajasthani handicrafts",
        },
        {
            "id": "SNP005",
            "name": "ElectroServe Noida",
            "city": "Noida",
            "rating": 0.91,
            "capacity": 220,
            "lat": 28.53,
            "lon": 77.39,
            "categories": ["EL001", "HA001"],
            "certifications": ["ISO9001", "BIS", "CE"],
            "export_capable": True,
            "languages": ["en", "hi"],
            "payment_terms": "Net 60",
            "specialization": "Electronics components and home appliances",
        },
        {
            "id": "SNP006",
            "name": "PharmaLink Hyderabad",
            "city": "Hyderabad",
            "rating": 0.93,
            "capacity": 210,
            "lat": 17.39,
            "lon": 78.49,
            "categories": ["PH001", "AY001"],
            "certifications": ["WHO-GMP", "ISO9001", "AYUSH License"],
            "export_capable": True,
            "languages": ["en", "hi", "te"],
            "payment_terms": "Net 45",
            "specialization": "Pharmaceuticals and Ayurvedic products",
        },
        {
            "id": "SNP007",
            "name": "ChemEdge Ankleshwar",
            "city": "Ankleshwar",
            "rating": 0.84,
            "capacity": 160,
            "lat": 21.62,
            "lon": 73.00,
            "categories": ["CH001", "PL001"],
            "certifications": ["ISO14001", "Pollution Control"],
            "export_capable": False,
            "languages": ["en", "hi", "gu"],
            "payment_terms": "Net 30",
            "specialization": "Industrial chemicals and polymers",
        },
        {
            "id": "SNP008",
            "name": "PlastoFlex Rajkot",
            "city": "Rajkot",
            "rating": 0.82,
            "capacity": 150,
            "lat": 22.30,
            "lon": 70.80,
            "categories": ["PL001", "PK001"],
            "certifications": ["BIS", "ISO9001"],
            "export_capable": False,
            "languages": ["en", "hi", "gu"],
            "payment_terms": "Net 30",
            "specialization": "Plastic products and packaging",
        },
        {
            "id": "SNP009",
            "name": "MetalForge Jamshedpur",
            "city": "Jamshedpur",
            "rating": 0.90,
            "capacity": 240,
            "lat": 22.80,
            "lon": 86.20,
            "categories": ["MT001", "AU001"],
            "certifications": ["ISO9001", "NABL"],
            "export_capable": True,
            "languages": ["en", "hi"],
            "payment_terms": "Net 45",
            "specialization": "Metal fabrication and auto components",
        },
        {
            "id": "SNP010",
            "name": "WoodCraft Mysuru",
            "city": "Mysuru",
            "rating": 0.85,
            "capacity": 130,
            "lat": 12.30,
            "lon": 76.65,
            "categories": ["WO001", "FU001"],
            "certifications": ["FSC", "ISO9001"],
            "export_capable": True,
            "languages": ["en", "hi", "kn"],
            "payment_terms": "Net 30",
            "specialization": "Premium wooden furniture",
        },
        {
            "id": "SNP011",
            "name": "PackPro Surat",
            "city": "Surat",
            "rating": 0.87,
            "capacity": 170,
            "lat": 21.17,
            "lon": 72.83,
            "categories": ["PK001", "PR001"],
            "certifications": ["ISO9001", "BIS"],
            "export_capable": False,
            "languages": ["en", "hi", "gu"],
            "payment_terms": "Net 30",
            "specialization": "Packaging and printing services",
        },
        {
            "id": "SNP012",
            "name": "AutoPart Hub Gurugram",
            "city": "Gurugram",
            "rating": 0.89,
            "capacity": 200,
            "lat": 28.46,
            "lon": 77.03,
            "categories": ["AU001", "MT001"],
            "certifications": ["TS16949", "ISO9001"],
            "export_capable": True,
            "languages": ["en", "hi"],
            "payment_terms": "Net 60",
            "specialization": "Automotive components for OEMs",
        },
        {
            "id": "SNP013",
            "name": "SolarEdge Jaipur",
            "city": "Jaipur",
            "rating": 0.83,
            "capacity": 160,
            "lat": 26.91,
            "lon": 75.79,
            "categories": ["RE001"],
            "certifications": ["BIS", "MNRE Approved"],
            "export_capable": False,
            "languages": ["en", "hi"],
            "payment_terms": "Net 30",
            "specialization": "Solar panels and renewable energy",
        },
        {
            "id": "SNP014",
            "name": "BuildMate Indore",
            "city": "Indore",
            "rating": 0.86,
            "capacity": 190,
            "lat": 22.72,
            "lon": 75.86,
            "categories": ["CO001", "PA001"],
            "certifications": ["BIS", "ISO9001"],
            "export_capable": False,
            "languages": ["en", "hi"],
            "payment_terms": "Net 30",
            "specialization": "Construction materials and paints",
        },
        {
            "id": "SNP015",
            "name": "CarePlus Lucknow",
            "city": "Lucknow",
            "rating": 0.88,
            "capacity": 150,
            "lat": 26.85,
            "lon": 80.95,
            "categories": ["PC001", "AY001"],
            "certifications": ["ISO22716", "AYUSH License"],
            "export_capable": False,
            "languages": ["en", "hi"],
            "payment_terms": "Net 30",
            "specialization": "Personal care and Ayurvedic cosmetics",
        },
        {
            "id": "SNP016",
            "name": "Sportify Meerut",
            "city": "Meerut",
            "rating": 0.84,
            "capacity": 140,
            "lat": 28.98,
            "lon": 77.70,
            "categories": ["SG001"],
            "certifications": ["ISO9001", "Sports Authority"],
            "export_capable": True,
            "languages": ["en", "hi"],
            "payment_terms": "Net 45",
            "specialization": "Cricket and sports equipment",
        },
        {
            "id": "SNP017",
            "name": "FurniCore Kochi",
            "city": "Kochi",
            "rating": 0.85,
            "capacity": 165,
            "lat": 9.93,
            "lon": 76.26,
            "categories": ["FU001", "WO001"],
            "certifications": ["ISO9001", "FSC"],
            "export_capable": True,
            "languages": ["en", "hi", "ml"],
            "payment_terms": "Net 30",
            "specialization": "Modular furniture and wood products",
        },
        {
            "id": "SNP018",
            "name": "StationeryMart Kolkata",
            "city": "Kolkata",
            "rating": 0.86,
            "capacity": 155,
            "lat": 22.57,
            "lon": 88.36,
            "categories": ["ST001", "PR001"],
            "certifications": ["ISO9001"],
            "export_capable": False,
            "languages": ["en", "hi", "bn"],
            "payment_terms": "Net 30",
            "specialization": "Stationery and printing supplies",
        },
        {
            "id": "SNP019",
            "name": "JewelCraft Mumbai",
            "city": "Mumbai",
            "rating": 0.90,
            "capacity": 175,
            "lat": 19.07,
            "lon": 72.88,
            "categories": ["JE001", "HM001"],
            "certifications": ["BIS Hallmark", "Export Certificate"],
            "export_capable": True,
            "languages": ["en", "hi", "mr"],
            "payment_terms": "Net 45",
            "specialization": "Fashion jewelry and handicrafts",
        },
        {
            "id": "SNP020",
            "name": "FreshFoods Nashik",
            "city": "Nashik",
            "rating": 0.87,
            "capacity": 160,
            "lat": 19.99,
            "lon": 73.79,
            "categories": ["FD001", "SP001", "BV001"],
            "certifications": ["FSSAI", "ISO22000"],
            "export_capable": False,
            "languages": ["en", "hi", "mr"],
            "payment_terms": "Net 15",
            "specialization": "Food processing and beverages",
        },
        # Additional 5 SNPs to reach 25
        {
            "id": "SNP021",
            "name": "ToyVillage Channapatna",
            "city": "Channapatna",
            "rating": 0.83,
            "capacity": 120,
            "lat": 12.65,
            "lon": 77.20,
            "categories": ["TO001", "WO001"],
            "certifications": ["GI Tag", "BIS"],
            "export_capable": True,
            "languages": ["en", "hi", "kn"],
            "payment_terms": "Net 30",
            "specialization": "Traditional wooden toys",
        },
        {
            "id": "SNP022",
            "name": "TechSoft Bengaluru",
            "city": "Bengaluru",
            "rating": 0.91,
            "capacity": 180,
            "lat": 12.97,
            "lon": 77.59,
            "categories": ["IT001"],
            "certifications": ["ISO27001", "CMMI Level 3"],
            "export_capable": True,
            "languages": ["en", "hi", "kn"],
            "payment_terms": "Net 30",
            "specialization": "Custom software development",
        },
        {
            "id": "SNP023",
            "name": "SafetyFirst Delhi",
            "city": "Delhi",
            "rating": 0.88,
            "capacity": 170,
            "lat": 28.61,
            "lon": 77.21,
            "categories": ["SF001"],
            "certifications": ["ISO9001", "CE", "BIS"],
            "export_capable": False,
            "languages": ["en", "hi"],
            "payment_terms": "Net 30",
            "specialization": "Industrial safety equipment and PPE",
        },
        {
            "id": "SNP024",
            "name": "CeraGlass Morbi",
            "city": "Morbi",
            "rating": 0.84,
            "capacity": 200,
            "lat": 22.81,
            "lon": 70.84,
            "categories": ["GL001", "CO001"],
            "certifications": ["ISO9001", "BIS"],
            "export_capable": True,
            "languages": ["en", "hi", "gu"],
            "payment_terms": "Net 45",
            "specialization": "Ceramic tiles and glass products",
        },
        {
            "id": "SNP025",
            "name": "AgroMachines Ludhiana",
            "city": "Ludhiana",
            "rating": 0.87,
            "capacity": 160,
            "lat": 30.90,
            "lon": 75.85,
            "categories": ["AE001", "MT001"],
            "certifications": ["ISO9001", "BIS"],
            "export_capable": False,
            "languages": ["en", "hi", "pa"],
            "payment_terms": "Net 30",
            "specialization": "Agricultural equipment and machinery",
        },
    ]
    
    for snp in snps:
        # Create SNP node with all metadata
        session.run(
            """
            MERGE (s:SNP {id: $id})
            SET s.name = $name, 
                s.city = $city, 
                s.rating = $rating,
                s.capacity = $capacity, 
                s.lat = $lat, 
                s.lon = $lon,
                s.certifications = $certifications,
                s.export_capable = $export_capable,
                s.languages = $languages,
                s.payment_terms = $payment_terms,
                s.specialization = $specialization
            """,
            **{k: v for k, v in snp.items() if k != 'categories'}
        )
        
        # Create SERVES relationships
        for code in snp['categories']:
            session.run(
                """
                MATCH (s:SNP {id: $id}), (c:Category {code: $code})
                MERGE (s)-[:SERVES]->(c)
                """,
                id=snp['id'],
                code=code,
            )


def create_indexes(session):
    """Create indexes for faster queries"""
    indexes = [
        "CREATE INDEX mse_city IF NOT EXISTS FOR (m:MSE) ON (m.city)",
        "CREATE INDEX mse_id IF NOT EXISTS FOR (m:MSE) ON (m.id)",
        "CREATE INDEX snp_city IF NOT EXISTS FOR (s:SNP) ON (s.city)",
        "CREATE INDEX snp_id IF NOT EXISTS FOR (s:SNP) ON (s.id)",
        "CREATE INDEX cat_code IF NOT EXISTS FOR (c:Category) ON (c.code)",
        "CREATE INDEX cat_sector IF NOT EXISTS FOR (c:Category) ON (c.sector)",
    ]
    for index_query in indexes:
        session.run(index_query)


def main():
    cfg = load_config()
    driver = GraphDatabase.driver(
        cfg["NEO4J_URI"], auth=(cfg["NEO4J_USER"], cfg["NEO4J_PASSWORD"])
    )
    
    with driver.session() as session:
        print("Creating indexes...")
        create_indexes(session)
        
        print("Seeding categories...")
        seed_categories(session)
        
        print("Seeding SNPs...")
        seed_snps(session)
    
    driver.close()
    print("\n✅ Successfully seeded:")
    print("   - 35 categories with ONDC mapping")
    print("   - 25 SNPs with rich metadata")
    print("   - 6 database indexes for performance")
    print("\nEnhancements:")
    print("   - Multilingual keywords (Hindi + English)")
    print("   - ONDC L1/L2/L3 taxonomy mapping")
    print("   - SNP certifications & specializations")
    print("   - Export capability flags")
    print("   - Language support per SNP")


if __name__ == "__main__":
    main()
