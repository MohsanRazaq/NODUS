
import unittest

from nodus.monitor.process_monitor import ProcessMonitor


def make_process(pid, ppid, starttime):
    return {
        "PID": pid,
        "PPID": ppid,
        "Name": f"process-{pid}",
        "starttime_ticks": starttime,
        "process_identity": (pid, starttime),
    }


def make_snapshot(processes, unreadable_pids=None, complete=True):
    return {
        "processes": processes,
        "unreadable_pids": set(unreadable_pids or []),
        "complete": complete,
    }


class TestAgentMonitorIntegration(unittest.TestCase):

    def test_monitor_compares_agent_descendants(self):
        monitor = ProcessMonitor()

        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
            make_process(200, 10, 1200),
        ])

        result = monitor.compare_agent_descendants(
            10,
            previous,
            current
        )

        self.assertEqual(result["agent_event"], "active")

        self.assertEqual(
            {
                p["process_identity"]
                for p in result["new"]
            },
            {(200, 1200)}
        )

        self.assertEqual(
            {
                p["process_identity"]
                for p in result["persistent"]
            },
            {(100, 1100)}
        )

        self.assertEqual(result["exited"], [])
        self.assertEqual(result["detached"], [])
        self.assertEqual(result["unknown"], [])


if __name__ == "__main__":
    unittest.main()
