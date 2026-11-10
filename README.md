# NODUS

**Linux Runtime Security Monitoring for Autonomous AI Agents**

NODUS is a Linux-based runtime security project focused on monitoring the process activity of autonomous AI agents. Its goal is to establish process-level visibility, correlate process activity with agent execution, and eventually identify suspicious behavior originating from agent workloads.

The project is currently under active development.

## Project Goals

- Monitor Linux processes and their lifecycle.
- Track process creation, termination, and PID reuse.
- Reconstruct process trees and parent-child relationships.
- Attribute descendant processes to monitored AI agents.
- Detect descendants that survive after losing their relationship with an agent.
- Establish a foundation for future runtime behavior analysis and security enforcement.

## Current Implementation

### Process Monitoring

NODUS collects process metadata through Linux `/proc`, including:

- PID and PPID
- Process name and state
- User IDs
- Process start time
- CPU time counters
- Virtual memory and resident memory information
- Process identity using `(PID, starttime_ticks)`

### Process Identity and Lifecycle Detection

Linux can reuse PIDs after processes terminate. NODUS therefore identifies processes using both PID and start time.

The snapshot comparator currently classifies:

- New processes
- Exited processes
- Persistent processes
- PID reuse
- Uncertain observations

### Process Tree Analysis

NODUS reconstructs parent-child relationships and supports:

- Process tree construction
- Ancestor-chain discovery
- Descendant discovery using breadth-first search

### Agent Process Attribution

NODUS compares process descendants across snapshots to identify:

- Newly observed descendants
- Persistent descendants
- Exited descendants
- Detached descendants
- Agent startup, termination, and replacement

Detached descendants are particularly important: a child process can survive after its parent terminates and become reparented to another process.

### Snapshot Reliability

Reading `/proc` is not an atomic operation. Processes can terminate or become inaccessible during collection.

NODUS therefore tracks:

- Successfully collected process records
- Unreadable PIDs
- Whether `/proc` enumeration completed
- Uncertain lifecycle observations

This helps avoid treating every missing process record as confirmed termination.

### CPU Telemetry

NODUS calculates CPU utilization from process CPU-time counter differences between snapshots, using monotonic elapsed time.

## Project Structure

```text
NODUS/
├── nodus/
│   ├── __init__.py
│   └── monitor/
│       ├── __init__.py
│       ├── proc_reader.py
│       ├── process_tree.py
│       ├── snapshot_comparator.py
│       ├── agent_comparator.py
│       └── process_monitor.py
├── tests/
│   ├── __init__.py
│   ├── test_agent_comparator.py
│   ├── test_agent_monitor_integration.py
│   └── manual_reparenting_test.py
├── main.py
├── test.py
├── testing.jsonl
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

## Requirements

- Linux
- Python 3
- Access to Linux `/proc`
- Python virtual environment recommended

## Getting Started

Clone the repository:

```bash
git clone https://github.com/MohsanRazaq/NODUS.git
cd NODUS
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install project dependencies if required:

```bash
pip install -r requirements.txt
```

Run NODUS:

```bash
python main.py
```

The monitor collects two process snapshots, compares them, calculates CPU utilization, and records events in `testing.jsonl`.

## Testing

Run the unit and integration tests:

```bash
python -m unittest discover -s tests -v
```

Run the manual Linux process-reparenting experiment:

```bash
python -m tests.manual_reparenting_test
```

Compile-check the project:

```bash
python -m compileall nodus tests
```

## Development Roadmap

The project is being developed incrementally.

- [x] Linux `/proc` process collection
- [x] Process identity and PID reuse detection
- [x] Process tree construction
- [x] Ancestor and descendant discovery
- [x] Snapshot comparison
- [x] CPU utilization telemetry
- [x] Agent descendant attribution
- [x] Detached descendant detection
- [x] Snapshot uncertainty tracking
- [ ] Agent execution behavior telemetry
- [ ] Suspicious behavior identification
- [ ] Runtime security policy engine
- [ ] Security enforcement mechanisms

## Design Direction

NODUS is intended to evolve from process-level monitoring into an agent-aware runtime security system.

The central design principle is to understand the relationship between an autonomous agent and the processes it creates, then use that context to identify potentially suspicious runtime behavior.

## Project Status

**Active development — MVP foundations in progress.**

NODUS is not yet a production-ready security enforcement system. Detection, policy evaluation, and enforcement capabilities remain under development.

## License

See [LICENSE](LICENSE).
