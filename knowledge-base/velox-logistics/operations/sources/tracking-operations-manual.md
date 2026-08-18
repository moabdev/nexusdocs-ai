# Velox Logistics - Tracking Operations Manual

## Document Control

- **Document ID:** KB-005
- **Version:** 4.2
- **Status:** ACTIVE
- **Classification:** INTERNAL
- **Owner:** Operations Department
- **Effective Date:** 2026-03-15
- **Related Documents:** Shipping Policy v3.0 (KB-003); Claims & Refund Policy v2.1 (KB-004)

## 1. Purpose
This manual defines operational rules for shipment tracking events, event validation, delivery evidence, exception handling, tracing, and escalation.

## 2. Scope
Applies to domestic shipments processed by Velox Logistics distribution centers, transportation operations, and last-mile delivery teams.

## 3. Tracking Event Model
- `PICKED_UP`: shipment accepted into the network.
- `IN_TRANSIT`: shipment moving between operational facilities or service areas.
- `AT_DISTRIBUTION_CENTER`: shipment scanned at a Velox distribution center.
- `OUT_FOR_DELIVERY`: shipment assigned to the last-mile route.
- `DELIVERED`: delivery completion recorded.
- `DELIVERY_EXCEPTION`: event prevented normal delivery progression.
- `RETURN_TO_SENDER`: shipment entered an authorized return flow.

Events must reflect the best available operational evidence and may be corrected when demonstrably inaccurate.

## 4. Event Ordering
Tracking systems should preserve chronological event history. Corrective events must not silently erase prior operational evidence. Corrections should retain the original event, corrected event, reason, timestamp, and responsible process or operator.

## 5. PICKED_UP
`PICKED_UP` confirms physical custody. A label creation event alone does not establish physical custody.

## 6. IN_TRANSIT
Repeated `IN_TRANSIT` events are valid when they represent distinct scans, transfers, or route progression. Absence of tracking progression must be evaluated against the loss threshold established by the ACTIVE Shipping Policy.

## 7. AT_DISTRIBUTION_CENTER
This event confirms receipt at a Velox facility. Unexpected dwell time may trigger internal exception monitoring before a shipment qualifies for formal loss investigation.

## 8. OUT_FOR_DELIVERY
This event indicates assignment to a last-mile route. Failure to complete delivery does not automatically indicate loss.

## 9. DELIVERED
Available proof of delivery may include timestamp, location or route evidence, recipient confirmation, delivery scan, authorized photograph, courier record, or other permitted evidence. A `DELIVERED` event may be corrected if evidence establishes an erroneous completion scan.

## 10. Delivered but Not Received Procedure
When a customer reports non-receipt while tracking shows `DELIVERED`, Customer Experience must advise the customer to allow **24 hours from the recorded delivery timestamp** before a formal non-delivery investigation is opened.

During this waiting period, the customer may be asked to verify the delivery address, check with household members or reception, inspect safe delivery locations, and review delivery notifications.

If the shipment remains unlocated after 24 hours, Customer Experience may open a non-delivery case under the Claims & Refund Policy. Operations must then review proof-of-delivery evidence and operational records.

**The 24-hour waiting rule does not extend the claim filing deadline established by the ACTIVE Shipping Policy.**

## 11. DELIVERY_EXCEPTION
Examples include recipient unavailable, inaccessible destination, incorrect address, weather disruption, damaged shipment requiring review, route disruption, or security restriction.

## 12. RETURN_TO_SENDER
Typical causes include repeated failed delivery attempts, invalid address, recipient refusal, prohibited delivery condition, or an authorized operational decision. Return status does not itself determine refund or compensation eligibility.

## 13. Missing Tracking Progression
Operations should investigate unusual gaps using facility scans, route records, transfer evidence, and other operational data. A shipment becomes eligible for potential loss classification only after the threshold defined by the ACTIVE Shipping Policy is reached.

## 14. Operational Trace
An operational trace may include validation of the latest reliable scan, facility records, transfer and route data, responsible-team confirmation, proof-of-delivery review, and documentation of the result. Operations owns the trace result; Customer Experience owns claimant communication unless another authorized process applies.

## 15. Event Correction
Corrections should record the shipment identifier, original event, corrected event, reason, correction timestamp, and responsible system, process, or operator. Event correction must preserve auditability.

## 16. Escalation
Cases should be escalated when operational evidence is materially inconsistent, theft or security concerns exist, multiple shipments show a correlated anomaly, or the case exceeds standard authority. Potential claim fraud follows the Claims & Refund Policy.

## 17. Relationship with Claims
This manual determines tracking interpretation and operational investigation procedures. The Claims & Refund Policy determines claim administration, evidence requirements, eligibility review, and resolution workflow. The ACTIVE Shipping Policy determines service windows, claim filing deadlines, operational loss thresholds, and standard compensation ceilings.

## 18. Auditability
Tracking and tracing records must preserve sufficient evidence to reconstruct the shipment's operational history and material decisions.

## 19. Revision History
| Version | Effective date | Status | Summary |
|---|---|---|---|
| 4.2 | 2026-03-15 | ACTIVE | Standardized tracking states, 24-hour delivered-but-not-received procedure, trace workflow, event correction, and cross-policy responsibilities. |

---
**Synthetic data notice:** Velox Logistics is fictional. This document exists exclusively for NexusDocs AI development and RAG evaluation.
