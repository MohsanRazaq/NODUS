import os,json,time
from  datetime import datetime
from nodus.monitor.snapshot_comparator import compare_snapshots
output_file='testing.jsonl'

class ProcessMonitor:
    def parse_proc_status(self,pid):
        metadata={"PID":int(pid),'timestamp':datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        try:
            with open(f'/proc/{pid}/status','r',encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Name:"):
                        metadata["Name"]=line.split()[1]
                    elif line.startswith("State:"):
                        metadata["State"]=line.split()[1]
                    elif line.startswith("Uid:"):
                        parts=line.split()
                        metadata["Uids"]=[int(x) for x in parts[1:]]
                    elif line.startswith("PPid:"):
                        metadata["PPID"]=int(line.split()[1])
                        
                        
                        
                
            with open(f"/proc/{pid}/statm", "r", encoding="utf-8") as f:
                        statm_parts = f.read().split()
                        # Convert pages to bytes (usually 4096 bytes per page on Linux)
                        page_size = os.sysconf('SC_PAGE_SIZE')
                        metadata["vm_size_bytes"] = int(statm_parts[0]) * page_size
                        metadata["rss_bytes"] = int(statm_parts[1]) * page_size
            with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
                        stat_data = f.read()
                        closing_bracket=stat_data.rfind(")")  
                        rem_fields=stat_data[closing_bracket+2:].split()
                        
                        metadata["starttime_ticks"]=int(rem_fields[19])
                        metadata["cpu_user_ticks"]=int(rem_fields[11])
                        metadata["cpu_system_ticks"]=int(rem_fields[12])
                        metadata["process_identity"]=(int(pid),int(rem_fields[19]))
                        
                        
                        
                    
            return metadata
        except (FileNotFoundError, PermissionError, ProcessLookupError):
                return None
            
            
    def get_snapshot(self):
        processes = []

        for item in os.listdir("/proc"):
            if item.isdigit():
                proc_data = self.parse_proc_status(item)
                if proc_data:
                    processes.append(proc_data)

        return processes
            
        
if __name__=="__main__":
    print(f"Scanning /proc and appending metadata to {output_file}...")
    process_monitor=ProcessMonitor()
    previous = process_monitor.get_snapshot()
    time.sleep(5)
    current = process_monitor.get_snapshot()
    
    changes=compare_snapshots(previous,current)
    
    print('=='*50)
    print("NEW PROCESSES".center(60))
    print('=='*50)
    print(changes["new"])
    
    print('=='*50)
    print("EXITED PROCESSES".center(60))
    print('=='*50)
    print(changes["exited"])
    
    
    print('=='*50)
    print("PERSISTENT  PROCESSES".center(60))
    print('=='*50)
    print(changes["persistent"])
    
    print('=='*50)
    print("Reuse PROCESSES".center(60))
    print('=='*50)
    print(changes["reuse"])
    
    
    with open(output_file, "a", encoding="utf-8") as log_file:
        for event_type in ["new", "reuse","exited", "persistent"]:
            for process in changes[event_type]:
                record = {
                    "event": event_type,**process
                }
                log_file.write(json.dumps(record) + "\n")
                    
    print("Tracking snapshot complete.")
            
            