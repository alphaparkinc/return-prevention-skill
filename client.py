"""
return-prevention-skill: Client SDK
Predict return risk and generate proactive interventions to prevent returns.
"""
from __future__ import annotations
from typing import Optional

CATEGORY_RETURN_RATES = {
    "clothing": 0.30, "footwear": 0.25, "electronics": 0.20,
    "beauty": 0.08, "furniture": 0.10, "toys": 0.05,
    "accessories": 0.12, "food": 0.02, "sports": 0.15, "default": 0.12,
}

RISK_FACTORS_CONFIG = [
    ("high_customer_return_rate", 25, "Customer has historically high return rate"),
    ("size_sensitive_product",    20, "Size or fit products have higher return risk"),
    ("late_delivery",             18, "Delayed shipping increases dissatisfaction"),
    ("high_value_order",          12, "High-value orders have stricter buyer scrutiny"),
    ("new_product",               10, "New products have unknown quality perception"),
    ("complex_setup",             10, "Complex or technical products may disappoint"),
    ("fragile_product",            8, "Fragile products risk damage-related returns"),
    ("first_time_buyer",           7, "First-time customers have higher uncertainty"),
    ("high_category_rate",        15, "Product category has above-average return rate"),
]

INTERVENTIONS = {
    "critical": [
        "Send a personalized 'How to get the best results' guide within 24 hours of delivery.",
        "Proactively call or message the customer to confirm satisfaction on day 3.",
        "Offer an immediate exchange option before the customer initiates a return.",
        "Send size/fit assistance video or measurement guide if applicable.",
        "Activate a 'return rescue' chatbot flow triggered by low satisfaction signals.",
    ],
    "high": [
        "Send a post-purchase educational email with usage tips and FAQs on day 2.",
        "Include a QR code with the package linking to setup/styling video.",
        "Request satisfaction feedback on day 5 -- address issues before day 7.",
        "Offer a partial store credit as an alternative to full return.",
        "Send product care instructions for fragile or technical items.",
    ],
    "medium": [
        "Send a standard post-purchase follow-up email with product tips.",
        "Display 'how to use' content in the customer account portal.",
        "Include a satisfaction survey at day 7 post-delivery.",
        "Retarget with complementary accessories to increase product attachment.",
    ],
    "low": [
        "Standard post-purchase thank you email with review request.",
        "No immediate action required -- monitor for standard return window.",
    ],
}


class ReturnPreventionClient:
    """
    SDK for predicting order return risk and generating proactive prevention interventions.
    """

    def predict(
        self,
        order: dict,
        customer: Optional[dict] = None,
        product: Optional[dict] = None,
    ) -> dict:
        """
        Predict return risk for an order.

        Args:
            order:    Order context:
                      - order_id (str)
                      - product_category (str)
                      - order_value (float)
                      - days_since_purchase (int)
                      - shipping_days (int, actual vs. promised)
                      - customer_segment (str)
            customer: Customer history:
                      - past_returns (int)
                      - past_orders (int)
                      - satisfaction_score (float 0-10)
            product:  Product attributes (booleans):
                      - size_sensitive, fragile, high_price, new_product, complex_setup

        Returns:
            dict with return_risk_score, risk_tier, risk_factors, interventions
        """
        cust = customer or {}
        prod = product or {}

        risk_score = 0.0
        triggered_factors = []

        # Base category rate
        cat = str(order.get("product_category", "default")).lower()
        cat_rate = CATEGORY_RETURN_RATES.get(cat, CATEGORY_RETURN_RATES["default"])
        base = cat_rate * 40  # Scale to 0-40 base
        if cat_rate > 0.15:
            triggered_factors.append({"factor": "high_category_rate", "score": round(base), "detail": f"{cat} category return rate: {cat_rate*100:.0f}%"})
        risk_score += base

        # Customer return rate
        past_ret = int(cust.get("past_returns", 0))
        past_ord = int(cust.get("past_orders", 1))
        cust_return_rate = past_ret / max(past_ord, 1)
        if cust_return_rate > 0.2:
            contribution = min(cust_return_rate * 50, 25)
            risk_score += contribution
            triggered_factors.append({"factor": "high_customer_return_rate", "score": round(contribution), "detail": f"Customer return rate: {cust_return_rate*100:.0f}%"})

        # Late delivery
        shipping_days = int(order.get("shipping_days", 0))
        if shipping_days > 7:
            contribution = min((shipping_days - 7) * 3, 18)
            risk_score += contribution
            triggered_factors.append({"factor": "late_delivery", "score": round(contribution), "detail": f"Delivery took {shipping_days} days"})

        # High value
        order_value = float(order.get("order_value", 0))
        if order_value > 100:
            contribution = min((order_value - 100) / 50 * 3, 12)
            risk_score += contribution
            triggered_factors.append({"factor": "high_value_order", "score": round(contribution), "detail": f"Order value: ${order_value:.2f}"})

        # Product attributes
        if prod.get("size_sensitive"):
            risk_score += 20
            triggered_factors.append({"factor": "size_sensitive_product", "score": 20, "detail": "Size/fit product"})
        if prod.get("new_product"):
            risk_score += 10
            triggered_factors.append({"factor": "new_product", "score": 10, "detail": "New product, unproven satisfaction"})
        if prod.get("complex_setup"):
            risk_score += 10
            triggered_factors.append({"factor": "complex_setup", "score": 10, "detail": "Complex or technical setup"})
        if prod.get("fragile"):
            risk_score += 8
            triggered_factors.append({"factor": "fragile_product", "score": 8, "detail": "Fragile item -- shipping damage risk"})

        # First-time buyer
        if past_ord <= 1:
            risk_score += 7
            triggered_factors.append({"factor": "first_time_buyer", "score": 7, "detail": "First or second purchase"})

        # Satisfaction score reduction
        sat = float(cust.get("satisfaction_score", 8.0))
        if sat < 7.0:
            risk_score += (7.0 - sat) * 3
            triggered_factors.append({"factor": "low_satisfaction_score", "score": round((7-sat)*3,1), "detail": f"Satisfaction: {sat}/10"})

        risk_score = round(min(risk_score, 100.0), 1)

        if risk_score >= 75: tier = "critical"
        elif risk_score >= 50: tier = "high"
        elif risk_score >= 25: tier = "medium"
        else: tier = "low"

        triggered_factors.sort(key=lambda x: x["score"], reverse=True)
        interventions = INTERVENTIONS.get(tier, INTERVENTIONS["low"])

        return {
            "order_id": order.get("order_id", "unknown"),
            "return_risk_score": risk_score,
            "risk_tier": tier,
            "risk_factors": triggered_factors[:5],
            "interventions": interventions[:3],
            "days_to_act": 3 if tier == "critical" else 5 if tier == "high" else 7,
        }

    def batch_predict(self, orders: list[dict]) -> list[dict]:
        results = [self.predict(**o) for o in orders]
        results.sort(key=lambda x: x["return_risk_score"], reverse=True)
        return results
