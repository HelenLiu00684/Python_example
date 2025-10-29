import psutil
import datetime

# ================================
# CPU INFORMATION
# ================================

# Get the overall CPU usage percentage (average over 1 second)
print("CPU Usage (%):", psutil.cpu_percent(interval=1))

# Get the per-core CPU usage percentage
print("Per-core CPU Usage (%):", psutil.cpu_percent(interval=1, percpu=True))

# Get the number of logical CPUs (includes hyper-threaded cores)
print("Logical CPU count:", psutil.cpu_count())

# Get the number of physical CPU cores (no hyper-threading)
print("Physical CPU count:", psutil.cpu_count(logical=False))

# Get detailed CPU time statistics (user/system/idle)
print("CPU Times:", psutil.cpu_times())

# Get CPU frequency information (current, min, max MHz)
print("CPU Frequency:", psutil.cpu_freq())


# ================================
# MEMORY INFORMATION
# ================================

# Get virtual memory usage statistics
mem = psutil.virtual_memory()
print("Total memory (GB):", mem.total / (1024 ** 3))
print("Used memory (GB):", mem.used / (1024 ** 3))
print("Available memory (GB):", mem.available / (1024 ** 3))
print("Memory usage (%):", mem.percent)


# ================================
# DISK INFORMATION
# ================================

# Get disk partitions (list of mounted devices)
print("Disk Partitions:", psutil.disk_partitions())

# Get disk usage for the root directory
print("Disk Usage ('/'): ", psutil.disk_usage('/'))

# Get total disk read/write counters
print("Disk I/O Counters:", psutil.disk_io_counters())


# ================================
# NETWORK INFORMATION
# ================================

# Get network interface addresses (IP, MAC)
print("Network Interfaces:", psutil.net_if_addrs())

# Get total network I/O statistics
print("Network I/O Counters:", psutil.net_io_counters())

# Get per-network interface I/O statistics
print("Network I/O (per interface):", psutil.net_io_counters(pernic=True))


# ================================
# SYSTEM INFORMATION
# ================================

# Get the system boot time (returns a timestamp)
boot_timestamp = psutil.boot_time()

# Convert the timestamp to a readable datetime
boot_time = datetime.datetime.fromtimestamp(boot_timestamp)
print("System boot time:", boot_time)

# Get current logged-in users
print("System users:", psutil.users())


# ================================
# PROCESS INFORMATION
# ================================

# List all running processes with PID, name, and user
for proc in psutil.process_iter(['pid', 'name', 'username']):
    print(proc.info)

# Example: get detailed information for the current Python process
p = psutil.Process()
print("Current process name:", p.name())
print("CPU usage of this process:", p.cpu_percent(interval=1))
print("Memory info of this process:", p.memory_info())
print("Process status:", p.status())