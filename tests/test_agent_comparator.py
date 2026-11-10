
import unittest

from nodus.monitor.agent_comparator import compare_agent_descendants


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


def identities(processes):
    return {
        process["process_identity"]
        for process in processes
    }


class TestAgentDescendantComparator(unittest.TestCase):

    def test_detect_exited_and_detached_descendants(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
            make_process(200, 100, 1200),
        ])

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(200, 1, 1200),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(
            identities(result["exited"]),
            {(100, 1100)}
        )
        self.assertEqual(
            identities(result["detached"]),
            {(200, 1200)}
        )

    def test_detect_new_descendants(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
        ])

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(300, 10, 1300),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(
            identities(result["new"]),
            {(300, 1300)}
        )

    def test_detect_persistent_descendants(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(
            identities(result["persistent"]),
            {(100, 1100)}
        )

    def test_distinguish_detached_from_exited(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
            make_process(200, 10, 1200),
        ])

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(200, 1, 1200),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(
            identities(result["exited"]),
            {(100, 1100)}
        )
        self.assertEqual(
            identities(result["detached"]),
            {(200, 1200)}
        )

    def test_agent_started(self):
        previous = make_snapshot([])

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "started")
        self.assertEqual(
            identities(result["new"]),
            {(100, 1100)}
        )

    def test_agent_terminated(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot([])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "terminated")

    def test_agent_replaced(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot([
            make_process(10, 1, 2000),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "replaced")
        self.assertEqual(result["agent_identity"], (10, 1000))

    def test_agent_not_found(self):
        previous = make_snapshot([])
        current = make_snapshot([])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "not_found")

    def test_detect_agent_termination(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot([
            make_process(100, 1, 1100),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "terminated")
        self.assertEqual(
            identities(result["detached"]),
            {(100, 1100)}
        )

    def test_detect_agent_pid_reuse(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot([
            make_process(10, 1, 2000),
            make_process(100, 10, 1100),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "replaced")
        self.assertEqual(result["agent_identity"], (10, 1000))
        self.assertEqual(
            identities(result["detached"]),
            {(100, 1100)}
        )

    def test_agent_termination_with_surviving_descendant(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
            make_process(200, 100, 1200),
        ])

        current = make_snapshot([
            make_process(200, 1, 1200),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "terminated")
        self.assertEqual(
            identities(result["exited"]),
            {(100, 1100)}
        )
        self.assertEqual(
            identities(result["detached"]),
            {(200, 1200)}
        )

    def test_unreadable_agent_is_not_reported_terminated(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot(
            [],
            unreadable_pids={10},
        )

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "unknown")

    def test_incomplete_previous_scan_does_not_confirm_started(self):
        previous = make_snapshot([], complete=False)

        current = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "unknown")
        self.assertEqual(
            len(result["unknown"]),
            1
        )
        self.assertEqual(
            result["unknown"][0]["direction"],
            "possibly_new"
        )

    def test_unreadable_descendant_is_unknown_not_exited(self):
        previous = make_snapshot([
            make_process(10, 1, 1000),
            make_process(100, 10, 1100),
        ])

        current = make_snapshot(
            [make_process(10, 1, 1000)],
            unreadable_pids={100},
        )

        result = compare_agent_descendants(10, previous, current)

        self.assertEqual(result["agent_event"], "active")
        self.assertEqual(result["exited"], [])
        self.assertEqual(len(result["unknown"]), 1)
        self.assertEqual(
            result["unknown"][0]["direction"],
            "possibly_exited_or_detached"
        )


if __name__ == "__main__":
    unittest.main()
