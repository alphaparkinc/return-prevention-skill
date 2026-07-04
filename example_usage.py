"""
example_usage.py -- Demonstrates the ReturnPreventionClient SDK.
"""
from client import ReturnPreventionClient

def main():
    client = ReturnPreventionClient()

    print("[1] High-Risk Order -- Return Prevention")
    result = client.predict(
        order={
            "order_id": "ORD-2026-8841",
            "product_category": "clothing",
            "order_value": 145.00,
            "shipping_days": 12,
            "customer_segment": "new",
        },
        customer={
            "past_returns": 3,
            "past_orders": 8,
            "satisfaction_score": 6.5,
        },
        product={
            "size_sensitive": True,
            "fragile": False,
            "new_product": True,
            "complex_setup": False,
        }
    )
    print(f"Order: {result['order_id']}")
    print(f"Return Risk Score: {result['return_risk_score']}/100")
    print(f"Risk Tier: {result['risk_tier'].upper()}")
    print(f"Act within: {result['days_to_act']} days")
    print(f"\nRisk Factors:")
    for f in result["risk_factors"]:
        print(f"  [{f['score']}pts] {f['factor']}: {f['detail']}")
    print(f"\nInterventions:")
    for action in result["interventions"]:
        print(f"  -> {action}")

    print("\n[2] Batch Risk Scoring")
    orders = [
        {"order": {"order_id":"O1","product_category":"clothing","order_value":120,"shipping_days":10},"customer":{"past_returns":4,"past_orders":10},"product":{"size_sensitive":True}},
        {"order": {"order_id":"O2","product_category":"beauty","order_value":45,"shipping_days":3},"customer":{"past_returns":0,"past_orders":5},"product":{}},
        {"order": {"order_id":"O3","product_category":"electronics","order_value":299,"shipping_days":5},"customer":{"past_returns":1,"past_orders":3},"product":{"complex_setup":True,"fragile":True}},
    ]
    batch = client.batch_predict(orders)
    print(f"{'Order':<8} {'Risk Score':>12} {'Tier':>10}")
    for r in batch:
        print(f"{r['order_id']:<8} {r['return_risk_score']:>12.1f} {r['risk_tier'].upper():>10}")

if __name__ == "__main__":
    main()
