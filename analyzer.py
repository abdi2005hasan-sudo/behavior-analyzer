import psutil
import time
import json
from datetime import datetime
from pathlib import Path
import tempfile
import os


# CONFIGURATION

LOG_FILE = "behavior_log.json"
CPU_WARNING = 80
MEMORY_WARNING = 80
DISK_WARNING = 85
TOP_PROCESS_COUNT = 5


# HELPER FUNCTIONS

def get_timestamp():
    """ Returns current date and time as a readble string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



def get_cpu_usage():
    """ Returns CPU usage percentage."""
    return psutil.cpu_percent(interval = 1)


def get_memory_usage():
    """ Returns memory information as a dictionary."""
    memory = psutil.virtual_memory()
    return {
        "percent" : memory.percent,
        "used_gb" : round(memory.used / (1024 ** 3), 2),
        "total_gb": round(memory.total / (1024 ** 3), 2)
    }



def get_disk_usage():
    """ Returns disk usage information as a dictionary."""
    disk = psutil.disk_usage("/")
    return {
        "percent" : disk.percent,
        "used_gb" : round(disk.used / (1024 ** 3), 2),
        "total_gb": round(disk.total / (1024 ** 3), 2) 
    }



def get_battery_info():
    """ Returns battery information if available."""
    battery = psutil.sensors_battery()

    if battery is None:
        return {
            "available" : False,
            "message"  : "Battery information not available on this system."
        }


    return {
        "available" : True,
        "percent" : battery.percent,
        "plugged_in" : battery.power_plugged,
        "seconds_left" : battery.secsleft
    }



def get_top_processes(limit = 5):
    """ Returns the top CPU-consuming processes."""
    process_list = []

    # First call does not return solid information because interval = None, it starts monitering immdiately so the second calling records well
    for process in psutil.process_iter(['pid', 'name']):
        try:
            process.cpu_percent(interval = None)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    time.sleep(1)

    for process in psutil.process_iter(['pid', 'name']):
        try:
            process_info = {
                'pid' : process.info['pid'],
                'name' : process.info['name'],
                'cpu_percent' : process.cpu_percent(interval = None),
                'memory_percent' : round(process.memory_percent(),2)

            }

            process_list.append(process_info)


        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    process_list.sort(key = lambda p: p['cpu_percent'], reverse = True)
    return process_list[:limit]


def analyze_behavior(cpu, memory, disk, top_processes):
    """ Analyze system behavior and return warnings."""
    warnings = []

    if cpu >= CPU_WARNING:
        warnings.append(f"High CPU usage detected: {cpu}%")

    if memory ['percent'] >= MEMORY_WARNING:
        warnings.append(f"High memory usage detected: {memory['percent']}%")

    if disk ['percent'] >= DISK_WARNING:
        warnings.append(f"High disk usage detected: {disk['percent']}%")

    if not warnings:
        warnings.append("System behavior is normal.")

    return warnings





def build_report():
    """ Collect all system information and build report."""
    timestamp = get_timestamp()
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()
    battery = get_battery_info()
    top_processes = get_top_processes(TOP_PROCESS_COUNT)
    warnings = analyze_behavior(cpu, memory, disk, top_processes)

    report = {
        "timestamp": timestamp,
        "cpu_usage_percent": cpu,
        "memory": memory,
        "disk": disk,
        "battery": battery,
        "top_processes": top_processes,
        "analysis": warnings
    }

    return report




def save_report(report, filename=LOG_FILE):
    """Save the report into a JSON log file."""
    log_path = Path(filename)

    if log_path.exists():
        try:
            with open(log_path, "r") as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    existing_data.append(report)

    with open(log_path, "w") as file:
        json.dump(existing_data, file, indent=4)






def print_report(report):
    """Print a clean report in the terminal."""
    print("\n" + "=" * 50)
    print("        BEHAVIOR ANALYZER REPORT")
    print("=" * 50)
    print(f"Time: {report['timestamp']}")
    print(f"CPU Usage: {report['cpu_usage_percent']}%")
    print(
        f"Memory Usage: {report['memory']['percent']}% "
        f"({report['memory']['used_gb']} GB / {report['memory']['total_gb']} GB)"
    )
    print(
        f"Disk Usage: {report['disk']['percent']}% "
        f"({report['disk']['used_gb']} GB / {report['disk']['total_gb']} GB)"
    )

    battery = report["battery"]
    if battery["available"]:
        print(f"Battery: {battery['percent']}% | Plugged In: {battery['plugged_in']}")
    else:
        print(f"Battery: {battery['message']}")

    print("\nTop Processes:")
    for process in report["top_processes"]:
        print(
            f"  - {process['name']} (PID {process['pid']}) | "
            f"CPU: {process['cpu_percent']}% | "
            f"Memory: {process['memory_percent']}%"
        )

    print("\nAnalysis:")
    for item in report["analysis"]:
        print(f"  - {item}")

    print("=" * 50)
    print("Report saved successfully.\n")
    print("Bye")


# =========================
# MAIN PROGRAM
# =========================
def main():
    """Run the Behavior Analyzer."""
    print("Starting Behavior Analyzer...")
    report = build_report()
    save_report(report)
    print_report(report)


if __name__ == "__main__":
    main()


    























    