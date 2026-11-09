def compare_snapshots(previous,current):
    #dicts
    previous_map={process["process_identity"]:process  for process in previous}
    current_map={process["process_identity"]:process for process in current}
    previous_by_pid={process['PID']: process for process in previous}
    current_by_pid={process["PID"]:process for process in current}
    common_pids=previous_by_pid.keys()&current_by_pid.keys()
    reuse_pid_pids={ pid for pid in common_pids if previous_by_pid[pid]["starttime_ticks"]!=current_by_pid[pid]["starttime_ticks"] }    
    
    reuse_new_ids={ current_by_pid[pid]["process_identity"] for pid in reuse_pid_pids}
    reuse_existed_ids={ previous_by_pid[pid]["process_identity"] for pid in reuse_pid_pids}
    
    
    new_ids=current_map.keys()-previous_map.keys()
    new_ids=new_ids-reuse_new_ids
    exited_ids = previous_map.keys() - current_map.keys()
    exited_ids=exited_ids-reuse_existed_ids
    persistent_ids=previous_map.keys()&current_map.keys()




    #list
    reuse_processes=[
        {"previous":previous_by_pid[pid],
        "current":current_by_pid[pid]} for pid in reuse_pid_pids ]
    
    new_processes=[current_map[identity] for identity in new_ids]
    exited_processes = [previous_map[identity] for identity in exited_ids]
    persistent_processes=[current_map[identity] for identity in persistent_ids]
    
    return {
            "new":new_processes,
            "exited":exited_processes,
            "persistent": persistent_processes,
            "reuse":reuse_processes
            }