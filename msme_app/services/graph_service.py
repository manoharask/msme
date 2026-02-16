import json


def setup_knowledge_graph(driver):
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
    type=None,
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
            "type": type,
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
    with driver.session() as session:
        return list(
            session.run(
                """
                MATCH (m:MSE {id: $mse})-[:OFFERS]->(c:Category)
                MATCH (s:SNP)-[:SERVES]->(c)
                WHERE toLower(s.city) CONTAINS toLower($city) OR s.rating > 0.85
                WITH s, c, m,
                     (CASE
                        WHEN s.city = m.city THEN 1.0
                        ELSE 0.2 END) AS geo,
                     s.rating AS sla,
                     CASE WHEN s.capacity > 150 THEN 0.9 ELSE 0.0 END AS capacity,
                     COUNT { (s)-[:SERVES]->(:Category) } * 0.1 AS network
                RETURN s.name AS snp, s.city AS location,
                       round((geo*0.6 + sla*0.2 + capacity*0.1 + network*0.1)*100) AS score,
                       round(geo*100) AS geo_pct,
                       round(sla*100) AS sla_pct,
                       round(capacity*100) AS cap_pct
                ORDER BY score DESC LIMIT 2
                """,
                mse=mse_id,
                city=city,
            )
        )


def fetch_stats(driver):
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


def fetch_recent_mses(driver, limit=10):
    with driver.session() as session:
        return list(
            session.run(
                """
                MATCH (m:MSE)
                OPTIONAL MATCH (m)-[:OFFERS]->(c:Category)
                RETURN m.id AS id,
                       properties(m) AS props,
                       c.code AS category_code,
                       c.name AS category_name
                ORDER BY m.id DESC
                LIMIT $limit
                """,
                limit=limit,
            )
        )


def fetch_mse_by_id(driver, mse_id):
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


def fetch_categories(driver, limit=None):
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


def fetch_cities(driver):
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
