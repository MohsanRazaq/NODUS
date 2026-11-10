
def compare_snapshots(previous, current):
    previous_processes = previous["processes"]
    current_processes = current["processes"]

    previous_map = {
        process["process_identity"]: process
        for process in previous_processes
    }

    current_map = {
        process["process_identity"]: process
        for process in current_processes
    }

    previous_by_pid = {
        process["PID"]: process
        for process in previous_processes
    }

    current_by_pid = {
        process["PID"]: process
        for process in current_processes
    }

    common_pids = previous_by_pid.keys() & current_by_pid.keys()

    reuse_pid_pids = {
        pid
        for pid in common_pids
        if previous_by_pid[pid]["starttime_ticks"]
        != current_by_pid[pid]["starttime_ticks"]
    }

    reuse_new_ids = {
        current_by_pid[pid]["process_identity"]
        for pid in reuse_pid_pids
    }

    reuse_existed_ids = {
        previous_by_pid[pid]["process_identity"]
        for pid in reuse_pid_pids
    }

    new_ids = current_map.keys() - previous_map.keys()
    new_ids -= reuse_new_ids

    exited_ids = previous_map.keys() - current_map.keys()
    exited_ids -= reuse_existed_ids

    persistent_ids = previous_map.keys() & current_map.keys()

    reuse_processes = [
        {
            "previous": previous_by_pid[pid],
            "current": current_by_pid[pid]
        }
        for pid in reuse_pid_pids]
    # Processes that may be new but were not observed  in the previous snapshot.
    unknown_new_ids = {
        identity
        for identity in new_ids
        if (
            not previous["complete"]
            or identity[0] in previous["unreadable_pids"] )}

    new_ids -= unknown_new_ids

    # Processes that may have exited but could not be  confirmed in the current snapshot.
    unknown_exited_ids = {
        identity
        for identity in exited_ids
        if (
            not current["complete"]
            or identity[0] in current["unreadable_pids"] )}

    exited_ids -= unknown_exited_ids

    new_processes = [
        current_map[identity]
        for identity in new_ids
    ]

    exited_processes = [
        previous_map[identity]
        for identity in exited_ids
    ]

    persistent_processes = [
        current_map[identity]
        for identity in persistent_ids
    ]

    unknown_processes = [
        {
            "process": current_map[identity],
            "direction": "possibly_new"
        }
        for identity in unknown_new_ids
    ]

    unknown_processes.extend([
        {
            "process": previous_map[identity],
            "direction": "possibly_exited"
        }
        for identity in unknown_exited_ids
    ])

    return {
        "new": new_processes,
        "exited": exited_processes,
        "persistent": persistent_processes,
        "reuse": reuse_processes,
        "unknown": unknown_processes
    }
