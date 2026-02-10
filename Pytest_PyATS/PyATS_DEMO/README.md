# Network Health Validation with pyATS and Explainable AI

This project demonstrates a **schema-driven network health validation framework**
built on **pyATS** with an **AI-assisted root cause analysis (RCA) layer**.

The system is designed to be:
- Deterministic and safe at the automation layer
- Explainable and advisory at the AI layer
- Modular, extensible, and production-oriented

---

## 1. Design Philosophy

This project follows a strict separation of responsibilities:

- **Parsers** extract structured semantic facts from raw CLI/log data
- **Checkers** apply deterministic rules to identify issues
- **Operations YAML** represents machine-readable remediation intent
- **AI Analysis** correlates issues across layers and explains root causes

> **AI never affects pass/fail decisions or executes actions.**  
> It only analyzes already-validated results and provides explanations.

---

## 2. High-Level Architecture

Raw CLI / Logs
|
v
+--------------------+
| Semantic Parsers |
| (EVPN/BGP/OSPF/IF) |
+--------------------+
|
v
+--------------------+
| Deterministic |
| Checkers (Rules) |
+--------------------+
|
v
+-----------------------------+
| operation_*.yaml (Schema) |
| - device |
| - issue |
| - actions |
| - metadata |
+-----------------------------+
|
v
+-----------------------------+
| AI RCA Layer (Advisory) |
| - Cross-layer correlation |
| - Root cause identification|
| - Human-readable explanation|
+-----------------------------+


---

## 3. Core Test Orchestration

### `tests/test_network_health.py` (System Entry Point)

This file is the **single orchestration point** of the entire system.

It performs:

1. Device inventory loading
2. Protocol-level health checks
3. Operation YAML generation
4. AI-based root cause analysis (post-check)

---

## 4. File-Level Call Flow (Detailed)

### 4.1 Test Entry Point

test_network_health.py


Responsibilities:
- Calls all protocol checkers
- Aggregates results
- Generates operation YAML
- Triggers AI analysis at the end

---

### 4.2 Semantic Parsing Layer

src/semantic_parser/
├── evpn_parser.py
├── bgp_parser.py
├── ospf_parser.py
├── interface_parser.py


Each parser:
- Has **one single parse function**
- Outputs a **frozen semantic schema**
- Does NOT contain any judgment logic

Example output:
```python
{
  "neighbors": {
    "10.10.0.1": {
      "up": False,
      "uptime": None,
      "fsm_state": "Idle"
    }
  }
}
4.3 Deterministic Checker Layer
src/checkers/
├── evpn.py
├── bgp.py
├── ospf.py
├── interface.py
Each checker:

Consumes semantic facts only

Applies deterministic rules

Never parses raw logs

Produces structured issue results

Output structure:

{
  "has_issue": True,
  "protocol": "EVPN",
  "issue_summary": [...],
  "issue_detail": {...},
  "affected_peers": [...],
  "actions": [...]
}
4.4 Operation YAML Generation
yaml/
├── issue_actions_*.yaml
├── operation_schema.yaml
Operation YAML files are generated into:

operations/
├── leaf4_evpn_operation.yaml
├── spine1_interface_operation.yaml
├── ...
Each operation file strictly follows operation_schema.yaml:

device: leaf4
role: leaf

issue:
  protocol: INTERFACE
  summary:
    - INTERFACE_DOWN
  detail:
    interfaces:
      Ethernet1/1:
        oper_up: false

actions:
  - "check interface Ethernet1/1 counters"

metadata:
  generated_by: pyATS
This schema is the contract between automation and AI.

5. AI-Assisted RCA Layer
Location
src/ai/
├── issue_loader.py
├── correlator.py
├── explainer.py
├── ai_analyzer.py
AI Responsibilities
The AI layer:

Reads only operations/*.yaml

Never reads raw logs

Never alters automation results

It performs:

Cross-device correlation

Cross-layer dependency analysis

Root cause identification

Human-readable explanation generation

Example AI Output
ai_analysis:
- device: leaf4
  root_cause:
    protocol: INTERFACE
    summary:
      - INTERFACE_DOWN
  explanation: >
    Interface Ethernet1/1 is down due to CRC errors.
    This interface failure caused OSPF adjacency loss
    and EVPN neighbor down events.
  impacted_protocols:
    - OSPF
    - EVPN
6. Why This Design Matters
This project demonstrates:

Safe automation (rules before AI)

Explainable AI (evidence-based reasoning)

Clear system boundaries

Production-aligned architecture

AI is advisory, explainable, and auditable, not authoritative.

7. Technologies Used
Python

pyATS / aetest

YAML (schema-driven design)

Rule-based analysis

Explainable AI concepts (non-ML)

8. Intended Use
Network validation demos

Automation architecture reference

Explainable AI experiments in infrastructure

Interview / portfolio project

9. Future Extensions
Confidence scoring

Evidence summarization

Visualization layer

Additional protocols (ISIS, MPLS)

10. Summary
This project shows how deterministic automation and AI analysis
can coexist safely and effectively in network operations.


---

# 文件 & YAML 调用逻辑图（围绕 test_network_health.py）

test_network_health.py
│
├─ load_devices_from_testbed()
│
├─ EVPN / BGP / OSPF / Interface checks
│ │
│ ├─ semantic_parser/.py
│ │ ↑
│ │ raw logs / routing summary
│ │
│ └─ checkers/.py
│ │
│ └─ issue_actions_.yaml
│
├─ generate_operation_yaml()
│ │
│ ├─ operation_schema.yaml
│ └─ operations/_operation.yaml
│
└─ ai_rca_analysis (final step)
│
├─ issue_loader.py → load operations/*.yaml
├─ correlator.py → root cause logic
├─ explainer.py → explanation text
└─ ai_analysis.yaml (output)

