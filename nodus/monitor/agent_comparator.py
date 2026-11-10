
from nodus.monitor.process_tree import get_descendants


def find_agent(agent_pid, processes):
    return next(
        (p for p in processes if p["PID"] == agent_pid),
        None
    )


def empty_result(agent_event, agent_identity=None):
    return {
        "agent_event": agent_event,
        "agent_identity": agent_identity,
        "new": [],
        "exited": [],
        "detached": [],
        "persistent": [],
        "unknown": [],
    }


def make_unknown(process, direction):
    return {
        "process": process,
        "direction": direction,
    }


def classify_previous_descendants(previous_descendants, current):
    """Classify descendants after their original agent disappears."""
    result = empty_result("unknown")

    current_ids = {
        p["process_identity"]
        for p in current["processes"]
    }

    for process in previous_descendants:
        identity = process["process_identity"]
        pid = process["PID"]

        if identity in current_ids:
            result["detached"].append(process)

        elif (
            not current["complete"]
            or pid in current["unreadable_pids"]
        ):
            result["unknown"].append(
                make_unknown(process, "possibly_exited")
            )

        else:
            result["exited"].append(process)

    return result


def compare_agent_descendants(agent_pid, previous, current):
    previous_processes = previous["processes"]
    current_processes = current["processes"]

    previous_agent = find_agent(agent_pid, previous_processes)
    current_agent = find_agent(agent_pid, current_processes)

    # Neither snapshot contains the agent.
    if previous_agent is None and current_agent is None:
        if (
            not previous["complete"]
            or not current["complete"]
            or agent_pid in previous["unreadable_pids"]
            or agent_pid in current["unreadable_pids"]
        ):
            return empty_result("unknown")

        return empty_result("not_found")

    # Agent is present now but was not observed previously.
    if previous_agent is None:
        if current_agent is None:
            return empty_result("unknown")

        current_identity = current_agent["process_identity"]

        if (
            not previous["complete"]
            or agent_pid in previous["unreadable_pids"]
        ):
            result = empty_result("unknown", current_identity)

            result["unknown"] = [
                make_unknown(process, "possibly_new")
                for process in get_descendants(
                    agent_pid, current_processes
                )
            ]

            return result

        result = empty_result("started", current_identity)
        result["new"] = get_descendants(
            agent_pid, current_processes
        )
        return result

    previous_identity = previous_agent["process_identity"]

    # Agent existed previously but is not currently observable.
    if current_agent is None:
        if (
            not current["complete"]
            or agent_pid in current["unreadable_pids"]
        ):
            result = empty_result("unknown", previous_identity)

            previous_descendants = get_descendants(
                agent_pid, previous_processes
            )

            result["unknown"] = [
                make_unknown(process, "possibly_exited_or_detached")
                for process in previous_descendants
            ]

            return result

        result = empty_result("terminated", previous_identity)

        previous_descendants = get_descendants(
            agent_pid, previous_processes
        )

        classified = classify_previous_descendants(
            previous_descendants, current
        )

        for category in ("exited", "detached", "unknown"):
            result[category] = classified[category]

        return result

    assert current_agent is not None
    current_identity = current_agent["process_identity"]

    # The same PID now belongs to another process.
    if previous_identity != current_identity:
        result = empty_result("replaced", previous_identity)

        previous_descendants = get_descendants(
            agent_pid, previous_processes
        )

        classified = classify_previous_descendants(
            previous_descendants, current
        )

        for category in ("exited", "detached", "unknown"):
            result[category] = classified[category]

        return result

    # The same agent instance exists in both snapshots.
    previous_descendants = get_descendants(
        agent_pid, previous_processes
    )

    current_descendants = get_descendants(
        agent_pid, current_processes
    )

    previous_map = {
        p["process_identity"]: p
        for p in previous_descendants
    }

    current_map = {
        p["process_identity"]: p
        for p in current_descendants
    }

    previous_ids = set(previous_map)
    current_ids = set(current_map)

    new_ids = current_ids - previous_ids
    no_longer_descendants = previous_ids - current_ids
    persistent_ids = previous_ids & current_ids

    current_all_ids = {
        p["process_identity"]
        for p in current_processes
    }

    result = empty_result("active", current_identity)

    # A newly observed descendant might already have existed
    # in an incomplete or partially unreadable previous scan.
    for identity in new_ids:
        pid = identity[0]

        if (
            not previous["complete"]
            or pid in previous["unreadable_pids"]
        ):
            result["unknown"].append(
                make_unknown(current_map[identity], "possibly_new")
            )
        else:
            result["new"].append(current_map[identity])

    for identity in no_longer_descendants:
        process = previous_map[identity]
        pid = process["PID"]

        if identity in current_all_ids:
            result["detached"].append(process)

        elif (
            not current["complete"]
            or pid in current["unreadable_pids"]
        ):
            result["unknown"].append(
                make_unknown(
                    process,
                    "possibly_exited_or_detached"
                )
            )

        else:
            result["exited"].append(process)

    result["persistent"] = [
        current_map[identity]
        for identity in persistent_ids
    ]

    return result
