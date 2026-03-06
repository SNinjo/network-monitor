import subprocess
import time
from datetime import datetime
import csv_tool as csv

class PingMonitor:
    def __init__(self, file_all, file_alert, int_ip, ext_ip, int_threshold, ext_threshold):
        self.file_all = file_all
        self.file_alert = file_alert
        self.int_ip = int_ip
        self.ext_ip = ext_ip
        self.int_threshold = int_threshold
        self.ext_threshold = ext_threshold
        self.is_running = False

    def get_headers(self) -> list:
        return ["INT_IP", "EXT_IP", "INT_LATENCY", "EXT_LATENCY"]

    def get_ping_time(self, target) -> float | str:
        try:
            output = subprocess.check_output(
                ['ping', '-c', '1', '-t', '1', target],
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            if "time=" in output:
                time_str = output.split("time=")[1].split("ms")[0].strip()
                return float(time_str)
            return "Timeout/Loss"
        except Exception as err:
            return "Packet Loss"

    def is_alert(self, time, threshold) -> bool:
        if time == "Packet Loss" or time == "Timeout/Loss":
            return True
        elif time > threshold:
            return True
        return False

    def get_results(self) -> (list, bool):
        int_time = self.get_ping_time(self.int_ip)
        ext_time = self.get_ping_time(self.ext_ip)
        is_alert = self.is_alert(int_time, self.int_threshold) or self.is_alert(ext_time, self.ext_threshold)
        return [self.int_ip, self.ext_ip, int_time, ext_time], is_alert
    
    def run(self):
        csv.create(self.file_all, self.get_headers())
        csv.create(self.file_alert, self.get_headers())

        if self.is_running:
            return
        self.is_running = True
        while self.is_running:
            int_time = self.get_ping_time(self.int_ip)
            ext_time = self.get_ping_time(self.ext_ip)
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + [self.int_ip, self.ext_ip, int_time, ext_time]
            csv.write(self.file_all, row)

            is_alert = self.is_alert(int_time, self.int_threshold) or self.is_alert(ext_time, self.ext_threshold)
            if is_alert:
                csv.write(self.file_alert, row)

            time.sleep(1)
    
    def quit(self):
        self.is_running = False
