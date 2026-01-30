This project is a network health check demo built on pyATS.
It analyzes post migration routing protocol states (OSPF, BGP, EVPN), evaluates protocol health, generates operation recommendation automatially and output YAMLs instead of execute changes manually.

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
network_qa_demo1/------>main folder
│
├── job.py------>pyATS job entry point
│   
│
├── tests/test_network_health.py
│
│       └─ Protocol-agnostic orchestration layer
│
├── src/
│   └── utils/
│       ├── check_ospf_bgp_evpn.py
│       │   └─ Protocol health evaluation logic
│       │
│       ├── routing_summary_parser.py
│       │   └─ CLI text parsing utilities
│       │
│       ├── load_input_expected.py
│       │   └─ Rule loading and operation YAML generation
│       │
│       └── testbed_loader.py
│           └─ Device inventory loader
│
├── yaml/
│   ├── expected_nodes.yaml
│   │   └─ Expected topology or node references
│   │
│   ├── issue_actions_ospf.yaml
│   ├── issue_actions_bgp.yaml
│   ├── issue_actions_evpn.yaml
│   ├── issue_actions_interface.yaml
│   │   └─ Issue-to-action mapping rules
│   │
│   └── operation_schema.yaml
│       └─ Output schema definition
│
├── data/
│   ├── routing_summary/
│   │   └─ Pre-collected routing summaries
│   │
│   └── logs/
│       └─ Execution and debug logs
│
├── operations/
│   └─ Generated operation recommendation YAML files
│
├── testbed.yaml
│   └─ Device inventory and role definitions
│
├── requirements.txt
│   └─ Python dependencies
│
└── README.md
    └─ Project documentation

4.run order commands:
step1:pyats run job job.py    

