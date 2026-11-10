from nodus.monitor.process_monitor import ProcessMonitor


def main():
    monitor = ProcessMonitor()

    changes = monitor.run_once(interval=5)

    for event, processes in changes.items():
        print(f"{event}: {len(processes)}")


if __name__ == "__main__":
    main()