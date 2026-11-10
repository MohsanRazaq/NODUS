
import os
import signal
import subprocess
import time

from nodus.monitor.proc_reader import get_snapshot, parse_proc_status
from nodus.monitor.agent_comparator import compare_agent_descendants


def find_process(pid, snapshot):
    return next(
        (
            process
            for process in snapshot["processes"]
            if process["PID"] == pid
        ),
        None
    )


agent_pid = os.getpid()
bash = None
sleep_pid = None
sleep_identity = None

try:
    # Bash launches Sleep and remains alive waiting for it.
    bash = subprocess.Popen(
        ["bash", "-c", "sleep 60 & echo $!; wait"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    assert bash.stdout is not None, "Bash stdout is unavailable"

    sleep_pid = int(bash.stdout.readline().strip())

    time.sleep(0.2)

    previous = get_snapshot()

    assert previous["complete"], (
        "Initial /proc snapshot was incomplete"
    )

    bash_process = find_process(bash.pid, previous)
    sleep_process = find_process(sleep_pid, previous)
    agent_process = find_process(agent_pid, previous)

    assert agent_process is not None, "Agent was not found"
    assert bash_process is not None, "Bash was not found"
    assert sleep_process is not None, "Sleep was not found"

    sleep_identity = sleep_process["process_identity"]

    print("BEFORE:")
    print(f"Agent: {agent_pid}")
    print(f"Bash: {bash.pid}, PPID: {bash_process['PPID']}")
    print(f"Sleep: {sleep_pid}, PPID: {sleep_process['PPID']}")

    # Terminate Bash only. Sleep should survive.
    bash.terminate()
    bash.wait(timeout=5)

    # Wait until Sleep is observable with a different parent.
    current = None
    sleep_after = None
    deadline = time.monotonic() + 5

    while time.monotonic() < deadline:
        current = get_snapshot()

        sleep_after = find_process(sleep_pid, current)

        if (
            current["complete"]
            and sleep_after is not None
            and sleep_after["process_identity"] == sleep_identity
            and sleep_after["PPID"] != bash.pid
        ):
            break

        time.sleep(0.1)

    assert current is not None, "No current snapshot was obtained"
    assert current["complete"], "Final /proc snapshot was incomplete"
    assert sleep_after is not None, "Sleep disappeared"
    assert sleep_after["process_identity"] == sleep_identity, (
        "Sleep PID was reused"
    )
    assert sleep_after["PPID"] != bash.pid, (
        "Sleep was not reparented before timeout"
    )

    result = compare_agent_descendants(
        agent_pid,
        previous,
        current
    )

    print("\nAFTER:")
    print("Agent event:", result["agent_event"])
    print("New:", [p["PID"] for p in result["new"]])
    print("Exited:", [p["PID"] for p in result["exited"]])
    print("Detached:", [p["PID"] for p in result["detached"]])
    print("Persistent:", [p["PID"] for p in result["persistent"]])
    print(
        "Unknown:",
        [
            (item["process"]["PID"], item["direction"])
            for item in result["unknown"]
        ]
    )

    detached_ids = {
        process["process_identity"]
        for process in result["detached"]
    }

    assert sleep_identity in detached_ids, (
        "Sleep was not detected as detached"
    )

    print(
        "\nSUCCESS: Sleep remained alive but was no longer "
        "a descendant of the agent."
    )

finally:
    # Clean up the surviving Sleep process.
    if sleep_pid is not None and sleep_identity is not None:
        current_sleep = parse_proc_status(str(sleep_pid))

        if (
            current_sleep is not None
            and current_sleep["process_identity"] == sleep_identity
        ):
            os.kill(sleep_pid, signal.SIGTERM)

    if bash is not None:
        if bash.poll() is None:
            bash.kill()
            bash.wait()

        if bash.stdout is not None:
            bash.stdout.close()
