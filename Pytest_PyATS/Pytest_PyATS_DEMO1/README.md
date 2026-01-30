## Overview

This project is a rule-driven network automation demo designed to analyze post-migration
routing protocol states, including OSPF, BGP, and EVPN.

Instead of directly applying configuration changes, the system evaluates protocol health
and generates structured operation recommendations in YAML format. These outputs are
intended for review, validation, or integration with downstream automation workflows.

The project emphasizes modular design, clear data boundaries, and extensibility,
providing a foundation for future multi-vendor and AI-assisted automation.

## Workflow Overview

The system follows a layered and deterministic workflow to evaluate routing protocol health
and generate operation recommendations:

```text
Routing Protocol Outputs (Post-Migration)
        ↓
Raw Parsing (CLI / log based)
        ↓
Semantic Parsing (Protocol-Level Facts)
        ↓
Rule-Based Health Evaluation
        ↓
Operation Recommendation (YAML)

## ③ Design Rationale: Semantic Parsing Layer

## Design Rationale: Semantic Parsing Layer

This project intentionally introduces a semantic parsing layer rather than relying solely
on YAML-driven rules or direct raw CLI parsing.

The primary goal of this design is to establish a protocol-centric and vendor-agnostic
data model that decouples protocol semantics from device-specific formats and automation logic.

By normalizing raw routing protocol outputs into semantic facts, the system ensures that:

1. Protocol health evaluation logic remains independent of CLI formats  
2. YAML rules operate on structured facts instead of raw text  
3. Multi-vendor support can be introduced by adding new raw parsers without modifying
   existing checkers or orchestration logic  

While YAML is used to describe expected states and remediation actions, it is intentionally
positioned above the semantic layer rather than acting as the primary parsing mechanism.
This allows the system to evolve beyond static rule matching and toward more flexible
automation and AI-assisted workflows.


1.Topology:
                               Spine1 (RID 10.10.0.1)            Spine2 (RID 10.10.0.2)
                             ┌───────────────────────┐        ┌───────────────────────┐
                             │        OSPF/BGP       │        │        OSPF/BGP       │
                             │   Underlay Control    │        │   Underlay Control    │
                             │   EVPN over BGP AF    │        │   EVPN over BGP AF    │
                             └───────────┬───────────┘        └─────────────┬─────────┘
                                         │                                  │
     ────────────────────────────────────┼──────────── Underlay IP Fabric   ┼───────────────────────────────────
                                         │               (OSPF + BGP)       │
     ────────────────────────────────────┼──────────────────────────────────┼───────────────────────────────────
           │                             │                │                  │                                  
     ┌─────┴─────┐                 ┌─────┴─────┐    ┌─────┴─────┐   ┌─────┴─────┐
     │   Leaf1   │                 │   Leaf2   │    │   Leaf3   │   │   Leaf4   │
     │ RID 10.10 │                 │ RID 10.10 │    │ RID 10.10 │   │ RID 10.10 │
     │   0.3     │                 │   0.4     │    │   0.5     │   │   0.6     │
     └─────┬─────┘                 └─────┬─────┘    └─────┬─────┘   └─────┬─────┘
           │                             │                │               │
           │  (All OK)                   │  (Issue to S2) │(EVPN issue to S2)│ (Uplink issue to S1)
           │                             │                │                 │
           │                             │                │                 │
     Links to Spine1/2:             Link to Spine2:    Link to Spine2:     Link to Spine1:
     OSPF FULL                      BGP Idle/Down      EVPN Down           OSPF Down
     BGP Established                EVPN Down          (underlay OK)       BGP Idle/Down
     EVPN Up                                                                EVPN Down


2.Address Plan
OSPF Check
  → Same as BGP Underlay Router-ID

BGP Underlay Check
  → Uses Underlay BGP Router-ID (10.10.0.x)
  → Session state must be Established

EVPN Check
  → Neighbor state must be Up

Failure Summary (Demo Scenario)

The following table summarizes the intentional failure scenarios used in this demo.
Each issue is designed to illustrate a specific control-plane failure pattern in a spine–leaf fabric.

| Leaf  | Affected Spine | OSPF Status | BGP Underlay Status | EVPN Status | Failure Description                                                    |
| ----- | -------------- | ----------- | ------------------- | ----------- | -----------------------------------------------------------------------|
| leaf1 | spine1, spine2 | FULL        | Established         | Up          | **Baseline** – fully healthy leaf, used as a control reference         |
| leaf2 | spine2         | FULL        | **Idle / Down**     | **Down**    | BGP underlay failure toward spine2, causing EVPN to be unavailable     |
| leaf3 | spine2         | FULL        | Established         | **Down**    | EVPN address-family issue toward spine2 while underlay remains healthy |
| leaf4 | spine1         | **Down**    | **Idle / Down**     | **Down**    | Single uplink failure toward spine1 affecting all control planes       |


3.Project Directory Structure and Function
//Future

4.run order commands:
step1:pyats run job job.py    

5. git recording:
1/29/2026:
1.content:
Added a semantic parser for EVPN neighbor data
Separated EVPN parsing from checking logic
Updated EVPN data schema documentation
Cleaned up runtime-generated artifacts

WorkFlow:
Routing Summary Log (CLI output)
        ↓
Raw Parser (CLI / regex based)
        ↓
EVPN Semantic Parser
        ↓
Protocol-Level Facts (vendor-agnostic)
        ↓
EVPN Checker (rule-based evaluation)
        ↓
Operation YAML (remediation plan)


