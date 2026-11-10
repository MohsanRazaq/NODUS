
from collections import deque


def build_process_tree(processes):
    process_tree = {}

    for process in processes:
        parent_pid = process["PPID"]
        process_tree.setdefault(parent_pid, []).append(process)

    return process_tree


def get_ancestor_chain(pid, processes):
    process_map = {
        process["process_identity"]: process
        for process in processes
    }

    pid_map = {
        process["PID"]: process["process_identity"]
        for process in processes
    }

    identity = pid_map.get(pid)

    if identity is None:
        return []

    current = process_map.get(identity)
    chain = []
    visited = {identity}

    while current:
        parent_pid = current["PPID"]

        if parent_pid is None or parent_pid == 0:
            break

        parent_identity = pid_map.get(parent_pid)

        if parent_identity is None or parent_identity in visited:
            break

        parent = process_map.get(parent_identity)

        if parent is None:
            break

        chain.append(parent)
        visited.add(parent_identity)
        current = parent

    return chain


def get_descendants(agent_pid, processes):
    descendants = []
    process_tree = build_process_tree(processes)

    queue = deque([agent_pid])
    visited = {agent_pid}

    while queue:
        current_pid = queue.popleft()

        for child in process_tree.get(current_pid, []):
            child_pid = child["PID"]

            if child_pid not in visited:
                descendants.append(child)
                visited.add(child_pid)
                queue.append(child_pid)

    return descendants
