"""
ONDC Integration Layer (Mock for Stage 1, Live in Stage 2)
Demonstrates understanding of ONDC architecture
"""
import requests
from typing import List, Dict

class ONDCClient:
    def __init__(self, subscriber_id: str, signing_key: str):
        self.base_url = "https://api.ondc.org/v1"  # Mock URL
        self.subscriber_id = subscriber_id
        self.signing_key = signing_key
    
    def search_snps(self, category: str, city: str) -> List[Dict]:
        """
        ONDC 'search' API to discover SNPs (Seller Networks)
        In Stage 2, this will be a real API call
        """
        # Mock response for demo
        return [
            {
                "provider_id": "SNP_ONDC_001",
                "provider_name": "TextileMart Network",
                "location": city,
                "categories": [category],
                "rating": 4.5,
            }
        ]
    
    def register_mse_catalog(self, mse_data: Dict) -> Dict:
        """
        ONDC 'on_search' callback to register MSE products
        Maps MSE products to ONDC catalog format
        """
        catalog_items = []
        for product in mse_data.get('products', []):
            catalog_items.append({
                "id": f"{mse_data['urn']}_{product}",
                "descriptor": {
                    "name": product,
                    "short_desc": f"{product} from {mse_data['name']}"
                },
                "category_id": mse_data['ondc_category'],
                "location_ids": [mse_data['city']],
            })
        
        payload = {
            "context": {
                "domain": "B2B",
                "action": "on_search",
                "bap_id": self.subscriber_id,
            },
            "message": {
                "catalog": {
                    "providers": [{
                        "id": mse_data['urn'],
                        "descriptor": {"name": mse_data['name']},
                        "items": catalog_items,
                    }]
                }
            }
        }
        
        # In Stage 2: POST to ONDC network
        # response = requests.post(f"{self.base_url}/on_search", json=payload)
        
        return {"status": "registered", "items": len(catalog_items)}
    
    def notify_snp_match(self, mse_urn: str, snp_id: str) -> Dict:
        """
        Notify SNP of new MSE match via ONDC messaging
        """
        # Mock for now
        return {"status": "notified", "snp_id": snp_id}

# Integration in main app
def onboard_mse_with_ondc(mse_data, graph_matched_snps):
    """
    Complete workflow: Graph matching + ONDC registration
    """
    # 1. Use graph to find best SNPs (intelligence layer)
    top_snps = graph_matched_snps[:3]
    
    # 2. Register MSE catalog in ONDC
    ondc = ONDCClient(
        subscriber_id="MSME_TEAM_PLATFORM",
        signing_key="YOUR_KEY"
    )
    
    catalog_result = ondc.register_mse_catalog(mse_data)
    
    # 3. Notify matched SNPs
    for snp in top_snps:
        ondc.notify_snp_match(mse_data['urn'], snp['snp_id'])
    
    return {
        "graph_matches": len(top_snps),
        "ondc_catalog": catalog_result,
        "status": "success"
    }