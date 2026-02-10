## Semantic Parsing–Driven Network Health Validation PyATS + AI 
Semantic Parsing–Driven Network Health Validation (pyATS Demo)
This repository contains a network automation demo focused on post-migration protocol validation for OSPF, BGP, and EVPN, built with pyATS and Python.
Instead of driving automation directly from raw CLI outputs or hard-coded rules, the project introduces a semantic parsing layer that normalizes protocol state into vendor-agnostic facts.
This design decouples protocol logic from device-specific formats and provides a clean foundation for rule-based validation and higher-level reasoning.
Raw CLI / logs
 → Semantic parsing (protocol facts)
 → Rule-based protocol checks
 → Operation YAML (suggested actions only)
 → Cross-protocol correlation (root cause inference)
The goal of this demo is to explore clean architecture and semantic modeling in network automation, not to build a full remediation or telemetry system.