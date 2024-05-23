#!/usr/bin/python

import sys
import csv

from datetime import datetime

import psutil

script_start = datetime.now()
field_names = [
    "timestamp",
    "timedelta_seconds",
    "cpu_usage_percentage",
    "cpus_usage_percentage",
    "cpu_time_user",
    "cpu_time_system",
    "cpu_time_idle",
    "cpu_time_iowait",
    "cpu_time_irq",
    "cpu_time_softirq",
    "cpu_time_steal",
    "cpu_ctx_switches",
    "cpu_interrupts",
    "cpu_soft_interrupts",
    "cpu_syscalls",
    "cpu_freq_current",
    "cpu_freq_min",
    "cpu_freq_max",
    "sys_load_1min",
    "sys_load_5min",
    "sys_load_15min",
    "mem_total",
    "mem_available",
    "mem_usage_percentage",
    "mem_used",
    "mem_free",
    "mem_active",
    "mem_inactive",
    "mem_buffers",
    "mem_cached",
    "mem_shared",
    "swap_total",
    "swap_used",
    "swap_free",
    "swap_usage_percentage",
    "swap_sin",
    "swap_sout",
    "disk_read",
    "disk_write",
    "disk_read_rate",
    "disk_write_rate",
    "disk_usage",
    "net_sent",
    "net_recv",
    "net_send_rate",
    "net_recv_rate",
    "users",
    "processes"
]

with open(f"sysstats_{datetime.now().isoformat()}.csv", "w", newline="",
          encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    writer.writeheader()

    io_lastread = 0
    io_lastwrite = 0

    net_lastsend = 0
    net_lastrecv = 0

    while True:
        try:
            cpu_usage_percentage = psutil.cpu_percent(interval=1)
            cpu_times = psutil.cpu_times()
            cpu_stats = psutil.cpu_stats()
            cpu_freq = psutil.cpu_freq()
            sys_load = psutil.getloadavg()
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            io = psutil.disk_io_counters()

            disk_usage = {}
            for disk in psutil.disk_partitions():
                disk_usage[disk.mountpoint] = psutil.disk_usage(disk.mountpoint).percent

            net = psutil.net_io_counters()

            processes = []
            monitored_processes = [ "postgre", "pgsql", "spacewalk", "uyuni", "tomcat", "salt" ]
            all_processes = psutil.process_iter()
            for proc in all_processes:
                for monproc in monitored_processes:
                    if monproc in proc.name().lower():
                        process_details = {}
                        process_details["name"] = proc.name()
                        pid = proc.pid
                        monproc_obj = psutil.Process(pid)
                        process_details["cpu_usage"] = monproc_obj.cpu_percent()
                        process_details["mem_usage"] = monproc_obj.memory_percent()
                        process_details["status"] = monproc_obj.status()
                        process_details["user"] = monproc_obj.username()
                        process_details["create_time"] = monproc_obj.create_time()
                        process_details["io_counters"] = monproc_obj.io_counters()
                        process_details["cpu_times"] = monproc_obj.cpu_times()
                        process_details["open_files"] = monproc_obj.open_files()
                        process_details["num_threads"] = monproc_obj.num_threads()
                        process_details["cmdline"] = monproc_obj.cmdline()
                        processes.append(process_details)


            writer.writerow(
                {
                    field_names[0]: datetime.now(),
                    field_names[1]: (datetime.now() - script_start).total_seconds(),
                    field_names[2]: cpu_usage_percentage,
                    field_names[3]: psutil.cpu_percent(percpu=True),
                    field_names[4]: cpu_times.user,
                    field_names[5]: cpu_times.system,
                    field_names[6]: cpu_times.idle,
                    field_names[7]: cpu_times.iowait,
                    field_names[8]: cpu_times.irq,
                    field_names[9]: cpu_times.softirq,
                    field_names[10]: cpu_times.steal,
                    field_names[11]: cpu_stats.ctx_switches,
                    field_names[12]: cpu_stats.interrupts,
                    field_names[13]: cpu_stats.soft_interrupts,
                    field_names[14]: cpu_stats.syscalls,
                    field_names[15]: cpu_freq.current,
                    field_names[16]: cpu_freq.min,
                    field_names[17]: cpu_freq.max,
                    field_names[18]: sys_load[0],
                    field_names[19]: sys_load[1],
                    field_names[20]: sys_load[2],
                    field_names[21]: memory.total,
                    field_names[22]: memory.available,
                    field_names[23]: memory.percent,
                    field_names[24]: memory.used,
                    field_names[25]: memory.free,
                    field_names[26]: memory.active,
                    field_names[27]: memory.inactive,
                    field_names[28]: memory.buffers,
                    field_names[29]: memory.cached,
                    field_names[30]: memory.shared,
                    field_names[31]: swap.total,
                    field_names[32]: swap.used,
                    field_names[33]: swap.free,
                    field_names[34]: swap.percent,
                    field_names[35]: swap.sin,
                    field_names[36]: swap.sout,
                    field_names[37]: io.read_bytes,
                    field_names[38]: io.write_bytes,
                    field_names[39]: io.read_bytes - io_lastread,
                    field_names[40]: io.write_bytes - io_lastwrite,
                    field_names[41]: disk_usage,
                    field_names[42]: net.bytes_sent,
                    field_names[43]: net.bytes_recv,
                    field_names[44]: net.bytes_sent - net_lastsend,
                    field_names[45]: net.bytes_recv - net_lastrecv,
                    field_names[46]: len(psutil.users()),
                    field_names[47]: processes
                }
            )

            io_lastread = io.read_bytes
            io_lastwrite = io.write_bytes

            net_lastsend = net.bytes_sent
            net_lastrecv = net.bytes_recv
        except KeyboardInterrupt:
            sys.exit(0)
        except psutil.NoSuchProcess:
            print("ERROR - Process doesn't exist")
            continue
        except Exception as e:
            # only print the exception, but do not exit
            print(f"ERROR - General exception: {e}")
            continue
