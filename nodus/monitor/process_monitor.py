
import json
import os
import time
from pathlib import Path
from nodus.monitor.agent_comparator import compare_agent_descendants
from nodus.monitor.proc_reader import get_snapshot
from nodus.monitor.process_tree import (
    build_process_tree,
    get_ancestor_chain,
    get_descendants
)
from nodus.monitor.snapshot_comparator import compare_snapshots


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "testing.jsonl"


class ProcessMonitor:

    def __init__(self, output_file=DEFAULT_OUTPUT_FILE):
        self.output_file = Path(output_file)

    def get_snapshot(self):
        return get_snapshot()

    def build_process_tree(self, processes):
        return build_process_tree(processes)

    def get_ancestor_chain(self, pid, processes):
        return get_ancestor_chain(pid, processes)

    def get_descendants(self, agent_pid, processes):
        return get_descendants(agent_pid, processes)

    def compare_snapshots(self, previous, current):
        return compare_snapshots(previous, current)
    
    def compare_agent_descendants(self, agent_pid, previous, current):
        return compare_agent_descendants(agent_pid, previous, current)

    def calculate_cpu_percent(self, previous, changes, elapsed_time):
        clock_ticks = os.sysconf("SC_CLK_TCK")

        previous_map = {
            process["process_identity"]: process
            for process in previous["processes"]
        }

        for process in changes["persistent"]:
            old = previous_map.get(process["process_identity"])

            if old is None:
                continue

            cpu_delta = (
                process["cpu_user_ticks"]
                + process["cpu_system_ticks"]
                - old["cpu_user_ticks"]
                - old["cpu_system_ticks"]
            )

            process["cpu_percent"] = (
                cpu_delta / (clock_ticks * elapsed_time)) * 100

    def log_events(self, changes):
        with self.output_file.open("a", encoding="utf-8") as log_file:
            for event_type in ["new", "reuse", "exited", "persistent"]:
                for process in changes[event_type]:
                    record = {
                        "event": event_type,**process }

                    log_file.write(json.dumps(record) + "\n")

    def run_once(self, interval=5):
        previous = self.get_snapshot()

        start_time = time.monotonic()
        time.sleep(interval)

        current = self.get_snapshot()
        elapsed_time = time.monotonic() - start_time

        changes = self.compare_snapshots(previous, current)

        self.calculate_cpu_percent(previous, changes, elapsed_time)
        self.log_events(changes)

        return changes


if __name__ == "__main__":
    monitor = ProcessMonitor()

    print("Starting NODUS process monitoring...")

    changes = monitor.run_once(interval=5)

    for event_type, processes in changes.items():
        print(f"\n{event_type.upper()} PROCESSES: {len(processes)}")

    print("\nMonitoring cycle complete.")
