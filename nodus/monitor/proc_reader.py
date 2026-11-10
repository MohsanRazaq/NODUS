
import os
from datetime import datetime


def parse_proc_status(pid):
    metadata = {
        "PID": int(pid),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open(f"/proc/{pid}/status", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Name:"):
                    metadata["Name"] = line.partition(":")[2].strip()

                elif line.startswith("State:"):
                    metadata["State"] = line.split()[1]

                elif line.startswith("Uid:"):
                    parts = line.split()
                    metadata["Uids"] = [int(x) for x in parts[1:]]

                elif line.startswith("PPid:"):
                    metadata["PPID"] = int(line.split()[1])

        with open(f"/proc/{pid}/statm", "r", encoding="utf-8") as f:
            statm_parts = f.read().split()
            page_size = os.sysconf("SC_PAGE_SIZE")

            metadata["vm_size_bytes"] = int(statm_parts[0]) * page_size
            metadata["rss_bytes"] = int(statm_parts[1]) * page_size

        with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
            stat_data = f.read()
            closing_bracket = stat_data.rfind(")")
            rem_fields = stat_data[closing_bracket + 2:].split()

            metadata["starttime_ticks"] = int(rem_fields[19])
            metadata["cpu_user_ticks"] = int(rem_fields[11])
            metadata["cpu_system_ticks"] = int(rem_fields[12])

            metadata["process_identity"] = (
                int(pid),
                metadata["starttime_ticks"]
            )

        return metadata

    except (OSError, ValueError, IndexError):
        return None



def get_snapshot():
    processes = []
    unreadable_pids = set()

    try:
        proc_entries = os.listdir("/proc")

        for item in proc_entries:
            if not item.isdigit():
                continue

            proc_data = parse_proc_status(item)

            if proc_data is None:
                unreadable_pids.add(int(item))
            else:
                processes.append(proc_data)

    except OSError:
        return {
            "processes": processes,
            "unreadable_pids": unreadable_pids,
            "complete": False,
        }

    return {
        "processes": processes,
        "unreadable_pids": unreadable_pids,
        "complete": True,
    }
