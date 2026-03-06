import time
import csv
import os
from datetime import datetime
from monitor_ping import PingMonitor
from monitor_docsis import DocsisCrawler
from dotenv import load_dotenv
load_dotenv()

FILE_ALL = os.getenv("FILE_ALL")
FILE_ALERT = os.getenv("FILE_ALERT")
ROUTER_USERNAME = os.getenv("ROUTER_USERNAME")
ROUTER_PASSWORD = os.getenv("ROUTER_PASSWORD")
CRAWLER_INIT_INTERVAL = int(os.getenv("CRAWLER_INIT_INTERVAL"))

def create_csv(filename, headers):
    with open(filename, mode='w', newline='') as file:
        csv.writer(file).writerow(headers)

def write_to_csv(filename, data):
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

if __name__ == "__main__":
    ping_monitor = None
    try:
        ping_monitor = PingMonitor(FILE_ALL, FILE_ALERT, "192.168.0.1", "8.8.8.8", 5.0, 30.0)
        ping_monitor.run()
        

        # print("Initializing...")
        # running_seconds = 0
        # crawler = DocsisCrawler("http://192.168.0.1", ROUTER_USERNAME, ROUTER_PASSWORD, headless=True)
        # crawler.init()
        
        # headers = ["Timestamp"] + monitor_network.get_headers() + crawler.get_headers()
        # create_csv(FILE_ALL, headers)
        # create_csv(FILE_ALERT, headers)
        
        # print("Monitoring started...")
        # while True:
        #     start_time = time.time()

        #     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     docsis_results = crawler.get_results()
        #     network_results, is_alert = monitor_network.get_results("192.168.0.1", "8.8.8.8", 5.0, 30.0)
        #     write_to_csv(FILE_ALL, [now] + network_results + docsis_results)
        #     if is_alert:
        #         write_to_csv(FILE_ALERT, [now] + network_results + docsis_results)

        #     running_seconds += 1
        #     if running_seconds % 60 == 0:
        #         print(f"Monitoring for {running_seconds} seconds...")
        #     if running_seconds % CRAWLER_INIT_INTERVAL == 0:
        #         print(f"Re-initializing crawler ({CRAWLER_INIT_INTERVAL} seconds elapsed)...")
        #         crawler.quit()
        #         crawler.init()

        #     sleep_time = 1 - (time.time() - start_time)
        #     time.sleep(sleep_time if sleep_time > 0 else 0)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if ping_monitor:
            ping_monitor.quit()
