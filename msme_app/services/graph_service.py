"""
Enhanced Graph Service with Rich Metadata Support
Updated for IndiaAI Innovation Challenge 2026
"""
import json


def setup_knowledge_graph(driver):
    """Legacy function - use seed_graph.py instead"""
    with driver.session() as session:
        session.run(
            "MERGE (c:Category {code: 'TX001', name: 'Textiles', sector: 'Manufacturing'})"
        )
        session.run(
            "MERGE (c:Category {code: 'LE001', name: 'Leather Goods', sector: 'Manufacturing'})"
        )
        session.run(
            """
            MERGE (s1:SNP {id: 'SNP001', name: 'TextileHub Bengaluru', city: 'Bengaluru',
                          rating: 0.92, capacity: 200, lat: 12.97, lon: 77.59})
            """
        )
        session.run(
            """
            MERGE (s2:SNP {id: 'SNP002', name: 'LeatherWorks Chennai', city: 'Chennai',
                          rating: 0.95, capacity: 250, lat: 13.08, lon: 80.27})
            """
        )
        session.run(
            "MATCH (s:SNP {id: 'SNP001'}), (c:Category {code: 'TX001'}) MERGE (s)-[:SERVES]->(c)"
        )
        session.run(
            "MATCH (s:SNP {id: 'SNP002'}), (c:Category {code: 'LE001'}) MERGE (s)-[:SERVES]->(c)"
        )


def _normalize_address(address):
    if address is None:
        return None
    if isinstance(address, dict):
        return json.dumps(address, ensure_ascii=True)
    return address


def _normalize_list(value):
    if value is None:
        return None
    if isinstance(value, list):
        return value
    return [value]


def save_mse(
    driver,
    mse_id,
    name,
    city,
    products,
    category,
    category_name=None,
    urn=None,
    mobile=None,
    email=None,
    enterprise_type=None,
    activity=None,
    social_category=None,
    incorporation_date=None,
    commencement_date=None,
    registration_date=None,
    address=None,
    state=None,
    pin=None,
    unit_names=None,
    nic_5_digit_codes=None,
    nic_activity=None,
    source=None,
):
    with driver.session() as session:
        props = {
            "name": name,
            "city": city,
            "products": products,
            "urn": urn,
            "mobile": mobile,
            "email": email,
            "type": enterprise_type,
            "activity": activity,
            "social_category": social_category,
            "incorporation_date": incorporation_date,
            "commencement_date": commencement_date,
            "registration_date": registration_date,
            "address": _normalize_address(address),
            "state": state,
            "pin": pin,
            "unit_names": _normalize_list(unit_names),
            "nic_5_digit_codes": _normalize_list(nic_5_digit_codes),
            "nic_activity": nic_activity,
            "source": source,
        }
        session.run(
            """
            MERGE (m:MSE {id: $id})
            ON CREATE SET m.created_at = timestamp()
            SET m += $props
            MERGE (c:Category {code: $cat})
            SET c.name = coalesce(c.name, $cat_name)
            MERGE (m)-[:OFFERS]->(c)
            """,
            id=mse_id,
            cat=category,
            cat_name=category_name,
            props=props,
        )


def run_reasoning(driver, mse_id, city):
    """
    Enhanced matching with SNP metadata consideration
    Now includes certifications, export capability, and specialization
    """
    with driver.session() as session:
        return list(
            session.run(
                """
                MATCH (m:MSE {id: $mse})-[:OFFERS]->(c:Category)
                MATCH (s:SNP)-[:SERVES]->(c)
                WITH s, c, m,
                     (CASE
                        WHEN toLower(s.city) = toLower(m.city) THEN 1.0
                        ELSE 0.1 END) AS geo,
                     CASE
                        WHEN s.export_capable = true AND (s.rating + 0.05) > 1.0 THEN 1.0
                        WHEN s.export_capable = true THEN s.rating + 0.05
                        ELSE s.rating
                     END AS sla,
                     CASE WHEN s.capacity > 150 THEN 0.9 ELSE 0.5 END AS capacity,
                     size(coalesce(s.certifications, [])) * 0.02 AS cert_bonus
                WITH s, c, m, geo, sla, capacity, cert_bonus,
                     COUNT { (s)-[:SERVES]->(:Category) } AS total_cats
                WITH s, c, m, geo, sla, capacity, cert_bonus,
                     CASE WHEN total_cats > 0 THEN 1.0 / total_cats ELSE 1.0 END AS focus
                RETURN s.id AS snp_id,
                       s.name AS snp,
                       s.city AS location,
                       s.certifications AS certifications,
                       s.export_capable AS export_capable,
                       s.specialization AS specialization,
                       s.languages AS languages,
                       s.payment_terms AS payment_terms,
                       round((geo*0.6 + sla*0.15 + capacity*0.10 + focus*0.10 + cert_bonus*0.05)*100) AS score,
                       round(geo*100) AS geo_pct,
                       round(sla*100) AS sla_pct,
                       round(capacity*100) AS cap_pct,
                       size(coalesce(s.certifications, [])) AS cert_count
                ORDER BY score DESC LIMIT 3
                """,
                mse=mse_id,
                city=city,
            )
        )


def fetch_stats(driver):
    """Fetch dashboard statistics"""
    with driver.session() as session:
        return session.run(
            """
            OPTIONAL MATCH (m:MSE)
            WITH count(DISTINCT m) as mse_count
            OPTIONAL MATCH (s:SNP)
            WITH mse_count, count(DISTINCT s) as snp_count
            OPTIONAL MATCH (c:Category)
            WITH mse_count, snp_count, count(DISTINCT c) as categories
            OPTIONAL MATCH (s2:SNP)
            RETURN mse_count, snp_count, categories, coalesce(avg(s2.rating)*100, 0) as avg_sla
            """
        ).single()


def fetch_recent_mses(driver, limit=None):
    """Fetch MSEs ordered newest-first (by created_at); no limit by default."""
    with driver.session() as session:
        query = """
            MATCH (m:MSE)
            OPTIONAL MATCH (m)-[:OFFERS]->(c:Category)
            RETURN m.id AS id,
                   properties(m) AS props,
                   c.code AS category_code,
                   c.name AS category_name
            ORDER BY coalesce(m.created_at, 0) DESC
        """
        params: dict = {}
        if limit:
            query += " LIMIT $limit"
            params["limit"] = limit
        return list(session.run(query, **params))


def fetch_mse_by_id(driver, mse_id):
    """Fetch single MSE by ID with all details"""
    with driver.session() as session:
        record = session.run(
            """
            MATCH (m:MSE {id: $id})
            OPTIONAL MATCH (m)-[:OFFERS]->(c:Category)
            RETURN properties(m) AS props, c.code AS category_code, c.name AS category_name
            """,
            id=mse_id,
        ).single()
        if not record:
            return None
        props = record.get("props") or {}
        props["category_code"] = record.get("category_code")
        props["category_name"] = record.get("category_name")
        props["id"] = mse_id
        return props


def fetch_snps(driver, limit=None):
    """
    Fetch SNPs with basic information (for backward compatibility)
    Use fetch_snps_detailed() for rich metadata
    """
    with driver.session() as session:
        query = """
            MATCH (s:SNP)
            RETURN s.id AS id, s.name AS name, s.city AS city, s.rating AS rating, s.capacity AS capacity
            ORDER BY s.rating DESC
        """
        if limit:
            query += " LIMIT $limit"
            result = session.run(query, limit=limit)
        else:
            result = session.run(query)
        return list(result)


def fetch_snps_detailed(driver, limit=None):
    """
    NEW: Fetch SNPs with complete metadata including:
    - Certifications
    - Export capability
    - Languages supported
    - Payment terms
    - Specialization
    - Categories served
    """
    with driver.session() as session:
        query = """
            MATCH (s:SNP)
            OPTIONAL MATCH (s)-[:SERVES]->(c:Category)
            WITH s, collect(c.code) as category_codes, collect(c.name) as category_names
            RETURN s.id AS id, 
                   s.name AS name, 
                   s.city AS city, 
                   s.rating AS rating, 
                   s.capacity AS capacity,
                   s.certifications AS certifications,
                   s.export_capable AS export_capable,
                   s.languages AS languages,
                   s.payment_terms AS payment_terms,
                   s.specialization AS specialization,
                   category_codes,
                   category_names
            ORDER BY s.rating DESC
        """
        if limit:
            query += " LIMIT $limit"
            result = session.run(query, limit=limit)
        else:
            result = session.run(query)
        return list(result)


def fetch_categories(driver, limit=None):
    """Fetch categories with basic information"""
    with driver.session() as session:
        query = """
            MATCH (c:Category)
            RETURN c.code AS code, c.name AS name, c.sector AS sector, c.keywords AS keywords
            ORDER BY c.code ASC
        """
        if limit:
            query += " LIMIT $limit"
            result = session.run(query, limit=limit)
        else:
            result = session.run(query)
        return list(result)


def fetch_categories_detailed(driver, limit=None):
    """
    NEW: Fetch categories with ONDC mapping and SNP count
    """
    with driver.session() as session:
        query = """
            MATCH (c:Category)
            OPTIONAL MATCH (c)<-[:SERVES]-(s:SNP)
            WITH c, count(s) as snp_count
            RETURN c.code AS code, 
                   c.name AS name, 
                   c.sector AS sector, 
                   c.keywords AS keywords,
                   c.ondc_l1 AS ondc_l1,
                   c.ondc_l2 AS ondc_l2,
                   c.ondc_l3 AS ondc_l3,
                   snp_count
            ORDER BY c.code ASC
        """
        if limit:
            query += " LIMIT $limit"
            result = session.run(query, limit=limit)
        else:
            result = session.run(query)
        return list(result)


def fetch_cities(driver):
    """Fetch all unique cities from SNPs and MSEs"""
    with driver.session() as session:
        rows = session.run(
            """
            MATCH (n)
            WHERE n.city IS NOT NULL
            RETURN DISTINCT n.city AS city
            ORDER BY city ASC
            """
        )
        return [row["city"] for row in rows]


def fetch_snp_by_id(driver, snp_id):
    """Fetch a single SNP with all metadata and its category codes"""
    with driver.session() as session:
        record = session.run(
            """
            MATCH (s:SNP {id: $id})
            OPTIONAL MATCH (s)-[:SERVES]->(c:Category)
            WITH s, collect(c.code) AS category_codes
            RETURN properties(s) AS props, category_codes
            """,
            id=snp_id,
        ).single()
        if not record:
            return None
        props = dict(record["props"])
        props["category_codes"] = list(record["category_codes"])
        return props


def save_snp(
    driver,
    snp_id,
    name,
    city,
    rating,
    capacity,
    lat=None,
    lon=None,
    certifications=None,
    export_capable=False,
    languages=None,
    payment_terms=None,
    specialization=None,
    category_codes=None,
):
    """Create or update an SNP node and rebuild its SERVES relationships"""
    with driver.session() as session:
        session.run(
            """
            MERGE (s:SNP {id: $id})
            SET s.name           = $name,
                s.city           = $city,
                s.rating         = $rating,
                s.capacity       = $capacity,
                s.lat            = $lat,
                s.lon            = $lon,
                s.certifications = $certifications,
                s.export_capable = $export_capable,
                s.languages      = $languages,
                s.payment_terms  = $payment_terms,
                s.specialization = $specialization
            """,
            id=snp_id,
            name=name,
            city=city,
            rating=rating,
            capacity=capacity,
            lat=lat,
            lon=lon,
            certifications=certifications or [],
            export_capable=export_capable,
            languages=languages or [],
            payment_terms=payment_terms,
            specialization=specialization,
        )
        # Replace SERVES relationships atomically
        session.run("MATCH (s:SNP {id: $id})-[r:SERVES]->() DELETE r", id=snp_id)
        for code in (category_codes or []):
            session.run(
                """
                MATCH (s:SNP {id: $id}), (c:Category {code: $code})
                MERGE (s)-[:SERVES]->(c)
                """,
                id=snp_id,
                code=code,
            )


def delete_snp(driver, snp_id):
    """Delete an SNP and all its relationships"""
    with driver.session() as session:
        session.run("MATCH (s:SNP {id: $id}) DETACH DELETE s", id=snp_id)


def fetch_category_by_id(driver, code):
    """Fetch a single Category by code"""
    with driver.session() as session:
        record = session.run(
            "MATCH (c:Category {code: $code}) RETURN properties(c) AS props",
            code=code,
        ).single()
        if not record:
            return None
        return dict(record["props"])


def save_category(driver, code, name, sector, keywords=None,
                  ondc_l1=None, ondc_l2=None, ondc_l3=None):
    """Create or update a Category node"""
    with driver.session() as session:
        session.run(
            """
            MERGE (c:Category {code: $code})
            SET c.name     = $name,
                c.sector   = $sector,
                c.keywords = $keywords,
                c.ondc_l1  = $ondc_l1,
                c.ondc_l2  = $ondc_l2,
                c.ondc_l3  = $ondc_l3
            """,
            code=code,
            name=name,
            sector=sector,
            keywords=keywords or [],
            ondc_l1=ondc_l1,
            ondc_l2=ondc_l2,
            ondc_l3=ondc_l3,
        )


def delete_category(driver, code):
    """
    Delete a Category if no MSEs currently offer it.
    Returns (success: bool, message: str).
    """
    with driver.session() as session:
        row = session.run(
            """
            MATCH (m:MSE)-[:OFFERS]->(c:Category {code: $code})
            RETURN count(m) AS mse_count
            """,
            code=code,
        ).single()
        mse_count = row["mse_count"] if row else 0
        if mse_count > 0:
            return False, f"Cannot delete — {mse_count} MSE(s) currently offer this category."
        session.run("MATCH (c:Category {code: $code}) DETACH DELETE c", code=code)
        return True, "Category deleted successfully."


def fetch_analytics_summary(driver):
    """
    NEW: Comprehensive analytics for dashboard
    """
    with driver.session() as session:
        result = session.run(
            """
            CALL () {
                MATCH (c:Category) 
                RETURN count(c) as total_categories
            }
            CALL () {
                MATCH (s:SNP) 
                RETURN count(s) as total_snps, 
                       coalesce(sum(s.capacity), 0) as total_capacity,
                       coalesce(avg(s.rating), 0) as avg_rating
            }
            CALL () {
                MATCH (m:MSE) 
                RETURN count(m) as total_mses
            }
            CALL () {
                MATCH (s:SNP) 
                WHERE s.export_capable = true 
                RETURN count(s) as export_capable_snps
            }
            CALL () {
                MATCH (s:SNP) 
                RETURN count(DISTINCT s.city) as unique_cities
            }
            CALL () {
                MATCH ()-[r:SERVES]->() 
                RETURN count(r) as total_relationships
            }
            RETURN total_categories, total_snps, total_mses, 
                   total_capacity, avg_rating, export_capable_snps,
                   unique_cities, total_relationships
            """
        ).single()
        
        return {
            "total_categories": result["total_categories"],
            "total_snps": result["total_snps"],
            "total_mses": result["total_mses"],
            "total_capacity": result["total_capacity"],
            "avg_rating": result["avg_rating"],
            "export_capable_snps": result["export_capable_snps"],
            "unique_cities": result["unique_cities"],
            "total_relationships": result["total_relationships"],
        }
