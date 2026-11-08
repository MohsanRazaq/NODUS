# NODUS — Threat Model

**Version:** 0.1  
**Status:** Initial Draft  
**Project:** NODUS  
**Platform:** Linux  
**Primary Language:** Python

## 1. System Overview

NODUS is a runtime security system designed to protect autonomous AI agents against malicious manipulation and unauthorized activities.

It monitors agent-level actions and operating-system behavior, identifies suspicious activities, and enforces security policies independently of the agent's decision-making.

NODUS is designed to remain operational without requiring a continuously running Large Language Model (LLM).

Future versions will incorporate eBPF for kernel-level runtime visibility and lightweight Machine Learning (ML) for behavioral anomaly detection.

## 2. Security Objectives

NODUS has the following primary security objectives:

- **SO-01 — File Access Protection:** Prevent unauthorized access to sensitive files and resources.
- **SO-02 — Command Execution Control:** Restrict unauthorized or dangerous command execution.
- **SO-03 — Data Exfiltration Prevention:** Detect and prevent unauthorized transmission of sensitive information.
- **SO-04 — Behavioral Threat Detection:** Identify suspicious sequences of agent actions and operating-system activities.
- **SO-05 — Runtime Visibility:** Maintain visibility into agent operations, process execution, filesystem activity and network communication.
- **SO-06 — Independent Enforcement:** Enforce security policies even when an AI agent has been manipulated or compromised.
- **SO-07 — Evidence Preservation:** Maintain security event records for investigation and incident analysis.

## 3. Protected Assets

NODUS initially focuses on protecting:

| Asset | Security concern |
|---|---|
| SSH private keys | Credential theft |
| API keys and tokens | Unauthorized access |
| Environment variables | Exposure of secrets |
| User documents | Confidentiality |
| Source code | Intellectual property theft |
| System files | Unauthorized modification |
| Network connections | Data exfiltration |
| Agent execution environment | Unauthorized operations |

## 4. System Components

The planned NODUS architecture contains the following components:

1. **Agent Instrumentation:** Observes agent tool calls and execution context.
2. **Telemetry Collector:** Collects relevant runtime events.
3. **Policy Enforcement Engine:** Evaluates authorization and security policies.
4. **Behavioral Correlation Engine:** Connects agent-level actions with actual operating-system activities.
5. **Detection Engine:** Identifies suspicious activities using deterministic rules and, eventually, ML.
6. **Response Engine:** Handles blocking, alerts and incident recording.
7. **eBPF Monitoring Layer (Future):** Provides additional kernel-level runtime telemetry.

## 5. Threat Actors

The initial threat model considers:

- External attackers attempting to manipulate autonomous agents.
- Malicious users supplying adversarial prompts.
- Attackers introducing malicious documents or webpages.
- Malicious content designed to exploit indirect prompt injection.
- Attackers attempting to misuse an agent's legitimate tools.

## 6. Attacker Capabilities

We assume an attacker may:

- Submit malicious instructions through prompts.
- Place malicious instructions inside documents or webpages.
- Manipulate an agent into ignoring its original task.
- Attempt to access files outside the agent's authorized workspace.
- Attempt unauthorized command execution.
- Attempt to transmit sensitive information externally.
- Exploit excessive permissions granted to an AI agent.

The initial threat model does not assume that the attacker already controls the Linux kernel or has root privileges.

## 7. Attack Scenarios

### AS-01: Direct Jailbreak

An attacker manipulates an agent through adversarial instructions, attempting to bypass its intended restrictions.

**NODUS objective:** Restrict unauthorized actions independently of the agent's own safety reasoning.

### AS-02: Indirect Prompt Injection

An attacker places malicious instructions inside a document or webpage that the agent processes.

**NODUS objective:** Prevent unauthorized operations resulting from manipulated agent behavior.

### AS-03: Unauthorized File Access

A manipulated agent attempts to access sensitive files, such as SSH private keys or API credentials.

**NODUS objective:** Enforce file-access restrictions.

### AS-04: Unauthorized Command Execution

An agent attempts to execute unexpected shell commands or launch unauthorized processes.

**NODUS objective:** Apply command and process execution controls.

### AS-05: Data Exfiltration

An agent attempts to transmit sensitive information to an unauthorized external destination.

**NODUS objective:** Detect and prevent unauthorized outbound data transmission.

### AS-06: Suspicious Process Activity

An agent launches unexpected child processes or produces unusual process execution patterns.

**NODUS objective:** Monitor process relationships and identify suspicious execution behavior.

## 8. Trust Boundaries

NODUS must distinguish between:

- **Agent-level information:** What the agent intends or reports.
- **Tool-level activity:** What operations the agent requests.
- **Operating-system activity:** What processes actually execute and what resources they access.
- **Security enforcement:** What NODUS independently authorizes or blocks.

The agent must not be treated as the sole source of truth about its own behavior.

Operating-system permissions and independent enforcement mechanisms must remain effective even when agent-level security controls fail.

## 9. Security Assumptions

The initial design assumes:

1. NODUS operates in a Linux environment.
2. The AI agent executes within a controlled environment.
3. Agent tool invocations can be instrumented.
4. The monitoring process has sufficient permissions to collect relevant telemetry.
5. The attacker does not initially possess root privileges or kernel control.
6. Security policies are defined independently of agent instructions.
7. External AI services are not required for core security enforcement.

## 10. Out-of-Scope Threats

The initial prototype will not attempt to:

- Prevent every possible jailbreak or prompt injection.
- Eliminate vulnerabilities in underlying LLM models.
- Defend against an attacker with complete kernel or root control.
- Provide protection against every form of operating-system compromise.
- Support every autonomous AI framework.
- Replace enterprise SIEM, EDR or cloud security platforms.
- Guarantee detection of every unknown malicious behavior.

## 11. Security Requirements

The following requirements define the minimum security capabilities for NODUS v0.1.

| ID | Requirement |
|---|---|
| N-01 | Record relevant agent tool invocations with unique operation identifiers. |
| N-02 | Monitor process execution and relevant parent-child process relationships. |
| N-03 | Restrict agent filesystem access to explicitly authorized resources using OS-enforced controls. |
| N-04 | Restrict process execution to explicitly authorized operations where technically enforceable. |
| N-05 | Restrict outbound network connections to explicitly authorized destinations. |
| N-06 | Correlate agent operations with observed OS activity using operation identifiers and process metadata. |
| N-07 | Detect suspicious sequences using deterministic security rules. |
| N-08 | Record security events, policy decisions, and enforcement outcomes. |
| N-09 | Ensure enforcement does not depend on an external LLM. |
| N-10 | Define safe behavior when monitoring, policy evaluation, or enforcement fails. |
| N-11 | Minimize collection and storage of sensitive information. |
| N-12 | Keep ML anomaly detection and eBPF integration outside the initial implementation scope. |

The initial prototype focuses on enforcing filesystem and outbound network restrictions within a controlled agent environment. It does not claim universal prevention of prompt injection or content-aware detection of all data exfiltration.