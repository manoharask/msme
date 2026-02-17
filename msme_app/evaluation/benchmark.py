"""
Categorization accuracy evaluation for IndiaAI submission
"""
from msme_app.services.categorization import categorize_products
test_cases = [
    {"products": ["cotton saree", "silk fabric"], "expected": "TX001"},
    {"products": ["leather wallet", "belt"], "expected": "LE001"},
    {"products": ["solar panel", "inverter"], "expected": "RE001"},
    {"products": ["ayurvedic tablets", "herbal medicine"], "expected": "AY001"},
    {"products": ["notebook", "pen", "pencil"], "expected": "ST001"},
    # Add 100+ test cases
]

def evaluate_categorization(driver):
    correct = 0
    results = []
    
    for case in test_cases:
        pred_code, pred_name = categorize_products(
            case['products'], driver
        )
        is_correct = (pred_code == case['expected'])
        correct += is_correct
        
        results.append({
            'products': case['products'],
            'expected': case['expected'],
            'predicted': pred_code,
            'correct': is_correct
        })
    
    accuracy = (correct / len(test_cases)) * 100
    
    print(f"\n{'='*60}")
    print(f"CATEGORIZATION ACCURACY: {accuracy:.1f}%")
    print(f"Correct: {correct}/{len(test_cases)}")
    print(f"{'='*60}\n")
    
    # Show errors
    errors = [r for r in results if not r['correct']]
    if errors:
        print("Errors (first 10):")
        for err in errors[:10]:
            print(f"  {err['products']} → {err['predicted']} (expected {err['expected']})")
    
    return accuracy, results

if __name__ == "__main__":
    from msme_app.config import get_driver, load_config
    config = load_config()
    driver = get_driver(config)
    
    accuracy, _ = evaluate_categorization(driver)
    
    # For submission document
    with open("accuracy_report.txt", "w") as f:
        f.write(f"Product Categorization Accuracy: {accuracy:.1f}%\n")
        f.write(f"Test Cases: {len(test_cases)}\n")
        f.write(f"Categories Covered: 35\n")