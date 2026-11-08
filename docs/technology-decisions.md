# NODUS — Technology Decision Record

**Version:** 0.1  
**Status:** Proposed  
**Project:** NODUS

## 1. Core Technology

- Language: Python 3
- Operating System: Ubuntu Linux
- Version Control: Git
- Environment Management: Python virtual environment

## 2. Agent Instrumentation

**Proposed approach:** Python-based instrumentation adapter.

Purpose:
- Capture agent tool invocations.
- Record execution context.
- Associate tool requests with execution identifiers.
- Support future agent framework integration.

Initial scope: One Python-based agent framework.

## 3. Operating-System Monitoring

**Proposed approach:** Linux process and filesystem telemetry, with network activity monitoring.

Initial focus:
- Process execution.
- Parent-child process relationships.
- File access events.
- Network connection events.

Future extension: eBPF-based kernel telemetry.

## 4. Security Enforcement

**Proposed approach:** Independent operating-system security controls.

Technologies under evaluation:
- Linux permissions.
- Unprivileged execution.
- AppArmor.
- Sandboxing and network restrictions.

Security enforcement must not depend exclusively on agent instrumentation.

## 5. Event Storage

**Selected technology:** SQLite.

Purpose:
- Store structured security events.
- Maintain event relationships.
- Support incident investigation.
- Provide local persistence.

## 6. Detection

**Initial approach:** Deterministic security rules.

Future extension:
- Local ML anomaly detection using scikit-learn.
- Behavioral sequence analysis.

## 7. Optional Intelligence

LLM integration is optional and reserved for advanced investigation and explanation.

Core monitoring and enforcement must operate without external LLM APIs.

## 8. Deferred Technologies

The following technologies are deliberately postponed:

- eBPF implementation.
- ML anomaly detection.
- FastAPI service.
- Streamlit dashboard.
- Multi-agent framework support.

They will be introduced when the architecture and requirements justify them.

## 9. Selection Principles

Technology choices must prioritize:

1. Security and reliability.
2. Local execution.
3. Low operational cost.
4. Testability.
5. Maintainability.
6. Compatibility with the initial research scope.

## 10. Decision Status

These choices are proposed for the initial prototype. Final decisions will be confirmed after evaluating the selected agent framework, Linux enforcement capabilities and telemetry sources.