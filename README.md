# genpark-return-prevention-skill

> **GenPark AI Agent Skill** -- Predict order return risk and generate proactive interventions to prevent returns before they happen.

## Features

- Multi-factor risk scoring: customer return rate, shipping delays, product attributes, order value, satisfaction history
- Risk tiers: Critical (75+) / High (50-74) / Medium (25-49) / Low (<25)
- Category-specific base return rates (clothing 30%, beauty 8%, etc.)
- 20+ pre-built intervention templates per risk tier
- Days-to-act urgency flag
- Batch prediction for post-purchase queue management

## Quick Start

```python
from client import ReturnPreventionClient

client = ReturnPreventionClient()
result = client.predict(
    order={"product_category": "clothing", "order_value": 120, "shipping_days": 10},
    customer={"past_returns": 3, "past_orders": 8},
    product={"size_sensitive": True},
)
print(f"Risk: {result['return_risk_score']}/100 ({result['risk_tier']})")
for action in result["interventions"]:
    print(f"  -> {action}")
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
