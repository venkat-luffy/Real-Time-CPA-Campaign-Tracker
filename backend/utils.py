from_future_ import annotations
from typing import Dict

def compute_metrics(click: int,conversions: int, spend: float) -> Dict[str, float]:
    ctr = (conversions / clicks * 100.0) if clicks else 0.0
    cpc = (spend / clicks) if clicks else 0.0
    cpa = (spend / conversions) if conversions else 0.0
    roi = ((conversions * 100) - spend) / spend * 100 if spend > 0 else 0.0 
    return {
        "clicks": clicks,
        "conversions": conversions,
        "spend": round(spend, 2),
        "CTR": round(ctr, 2),
        "CPC": round(cpc, 2),
        "CPA": round(cpa, 2),
        "ROI": round(roi, 2),
    }
def simulate_outcomes(budget: float, cpc: float, conv_rate_pct: float) -> Dict[str, float]:
    if cpc <= 0:
        
        return {"error": "CPC must be > 0"}
    clicks = int(budget // cpc)
    conversions = int(clicks * (conv_rate_pct / 100.0))
    spend = clicks * cpc
    metrics = compute_metrics(clicks, conversions, spend)
    return metrics
def fraud_score(click_rate_per_min: float, unique_ip_ratio: float) -> float:
    """
    very simple heuristic:
     - Help click rate and low unique IP rati0 => suspicious
     Returns 0.100
     """
    base = 0
    if click_rate_per_min > 50:
        base +=50
    elif click_rate_per_min > 20:
        base +=25
        if unique_ip_ratio <0.5:
            base +=40
        elif unique_ip_ratio < 0.7:
            base +=20
            return min(100, base)
    





