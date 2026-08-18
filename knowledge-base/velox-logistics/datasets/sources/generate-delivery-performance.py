"""Generate the synthetic Velox Logistics delivery-performance dataset.

The generator is deterministic: the same seed and code produce the same CSV.
Synthetic data only; no real customers or shipments are represented.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260818
ROWS = 2500

REGIONS = {
    "Southeast": [("Sao Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG")],
    "South": [("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Florianopolis", "SC")],
    "Northeast": [("Recife", "PE"), ("Salvador", "BA"), ("Fortaleza", "CE")],
    "Central-West": [("Brasilia", "DF"), ("Goiania", "GO"), ("Cuiaba", "MT")],
    "North": [("Manaus", "AM"), ("Belem", "PA"), ("Porto Velho", "RO")],
}

CENTERS = {
    "Southeast": ["DC-SP-01", "DC-RJ-01", "DC-MG-01"],
    "South": ["DC-PR-01", "DC-RS-01"],
    "Northeast": ["DC-PE-01", "DC-BA-01", "DC-CE-01"],
    "Central-West": ["DC-DF-01", "DC-GO-01"],
    "North": ["DC-AM-01", "DC-PA-01"],
}

def weighted_choice(rng, items):
    values, weights = zip(*items)
    return rng.choices(values, weights=weights, k=1)[0]

def generate(output: Path) -> None:
    rng = random.Random(SEED)
    start = date(2026, 1, 1)
    rows = []

    for i in range(1, ROWS + 1):
        order_date = start + timedelta(days=rng.randrange(0, 229))
        region = weighted_choice(rng, [
            ("Southeast", 34), ("South", 19), ("Northeast", 23),
            ("Central-West", 13), ("North", 11)
        ])
        origin_region = weighted_choice(rng, [
            ("Southeast", 45), ("South", 18), ("Northeast", 17),
            ("Central-West", 12), ("North", 8)
        ])
        destination_city, destination_state = rng.choice(REGIONS[region])
        origin_city, origin_state = rng.choice(REGIONS[origin_region])
        service = weighted_choice(rng, [("STANDARD", 72), ("EXPRESS", 28)])
        customer_segment = weighted_choice(
            rng, [("RETAIL", 68), ("SMB", 22), ("ENTERPRISE", 10)]
        )
        center = rng.choice(CENTERS[region])

        base_estimated = 2 if service == "EXPRESS" else 5
        regional_extra = {"Southeast": 0, "South": 0, "Northeast": 1,
                          "Central-West": 1, "North": 2}[region]
        estimated_days = base_estimated + regional_extra + rng.choice([0, 0, 0, 1])

        distance = {
            "Southeast": (80, 1100), "South": (100, 1300),
            "Northeast": (150, 1900), "Central-West": (180, 1700),
            "North": (250, 2400)
        }[region]
        distance_km = rng.randint(*distance)

        # Intentional analytical signals for RAG/evaluation.
        delay_probability = {
            "Southeast": .12, "South": .14, "Northeast": .20,
            "Central-West": .18, "North": .24
        }[region]

        # Q2 Northeast disruption: deliberately raises delay severity.
        q2_northeast = region == "Northeast" and 4 <= order_date.month <= 6
        if q2_northeast:
            delay_probability += .22

        # DC-PE-01 deliberately concentrates delivery exceptions in Q2.
        exception_probability = .025
        if center == "DC-PE-01" and 4 <= order_date.month <= 6:
            exception_probability = .16

        # Express performs better overall.
        if service == "EXPRESS":
            delay_probability -= .05

        roll = rng.random()
        if roll < .012:
            status = "LOST"
            delay_days = rng.randint(7, 14)
        elif roll < .012 + exception_probability:
            status = "DELIVERY_EXCEPTION"
            delay_days = rng.randint(2, 7)
        elif rng.random() < delay_probability:
            status = "DELIVERED_LATE"
            delay_days = rng.randint(1, 4) + (rng.randint(1, 3) if q2_northeast else 0)
        else:
            status = "DELIVERED_ON_TIME"
            delay_days = rng.choice([-1, 0, 0, 0])

        actual_days = max(1, estimated_days + delay_days)
        delivery_date = order_date + timedelta(days=actual_days)

        rows.append({
            "shipment_id": f"VLX-2026-{i:06d}",
            "order_date": order_date.isoformat(),
            "delivery_date": delivery_date.isoformat(),
            "region": region,
            "origin": f"{origin_city}/{origin_state}",
            "destination": f"{destination_city}/{destination_state}",
            "service_type": service,
            "delivery_status": status,
            "estimated_days": estimated_days,
            "actual_days": actual_days,
            "delay_days": max(0, delay_days),
            "distance_km": distance_km,
            "distribution_center": center,
            "customer_segment": customer_segment,
        })

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "delivery-performance.csv")
