import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DocsisCrawler:
    def __init__(self, url, username=None, password=None, headless=False):
        self.url = url
        self.username = username
        self.password = password
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
    
    def init(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.url)
        self.login(self.username, self.password)

    def login(self, username, password):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='login_password' or @type='password' or contains(translate(@name, 'PASS', 'pass'), 'pass')]"))
            )
            
            if username:
                user_fields = self.driver.find_elements(By.XPATH, "//input[@name='login_username' or @type='text' and (contains(translate(@name, 'USER', 'user'), 'user') or contains(translate(@id, 'USER', 'user'), 'user') or contains(translate(@class, 'USER', 'user'), 'user') or contains(translate(@name, 'LOGIN', 'login'), 'log'))]")
                if not user_fields:
                    user_fields = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                if user_fields:
                    user_fields[0].clear()
                    user_fields[0].send_keys(username)
            
            if password:
                pass_fields = self.driver.find_elements(By.XPATH, "//input[@name='login_password' or @type='password' or contains(translate(@name, 'PASS', 'pass'), 'pass')]")
                if pass_fields:
                    pass_fields[0].clear()
                    pass_fields[0].send_keys(password)
            
            login_buttons = self.driver.find_elements(By.XPATH, "//input[@name='login_button' or @type='submit' or @value='登入' or contains(translate(@value, 'LOGIN', 'login'), 'login') or contains(@class, 'Login')] | //button[@type='submit' or contains(translate(text(), 'LOGIN', 'login'), 'login') or contains(text(), '登入')]")
            if login_buttons:
                self.driver.execute_script("arguments[0].removeAttribute('disabled'); arguments[0].click();", login_buttons[0])
            elif password and pass_fields:
                import selenium.webdriver.common.keys as Keys
                pass_fields[0].send_keys(Keys.Keys.RETURN)
            elif username and user_fields:
                import selenium.webdriver.common.keys as Keys
                user_fields[0].send_keys(Keys.Keys.RETURN)
                
            time.sleep(3) # Wait for login redirect/Ajax
            
        except Exception as e:
            print(f"Auto-login failed or fields not found: {e}")

    def get_data(self) -> dict:
        js_script = """
        var callback = arguments[arguments.length - 1];
        try {
            if (typeof AjaxGet === 'undefined') {
                callback('{"error": "AjaxGet not defined yet (page still loading or not logged in)"}');
                return;
            }
            AjaxGet("HttpGetDOCSIS", "", function(JSON_data) {
                callback(JSON_data);
            });
        } catch (e) {
            callback(JSON.stringify({error: e.toString()}));
        }
        """
        self.driver.set_script_timeout(5)
        try:
            data = self.driver.execute_async_script(js_script)
            
            # Ensure the response is a dictionary
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    data = {"raw_response": data}
            
            if data is None:
                return {"error": "No data returned from JS"}
                
            if isinstance(data, list):
                # If there are multiple items, format it as a dict to fit the CSV columns easily
                return {"data_list": json.dumps(data)}
                
            if not isinstance(data, dict):
                return {"value": data}
                
            return data
            
        except Exception as e:
            return {"error": str(e)}

    def get_headers(self) -> list:
        return ["CM_STATUS", "WAN_IP", "AVG_DS_SNR", "AVG_DS_POWER", "DS_UNCORRECT_SUM", "MAX_US_POWER"]

    def get_results(self) -> [str, str, float, float, int, float]:
        data = self.get_data()
        
        ds_snr_avg, ds_pow_avg, ds_uncorrect_sum, us_pow_max = 0.0, 0.0, 0, 0.0
        cm_status, wan_ipv4 = "Unknown", "Unknown"
        
        try:
            if "DeviceInfo" in data:
                cm_status = data["DeviceInfo"].get("CMStatus", "Unknown")
                wan_ipv4 = data["DeviceInfo"].get("WAN_IPv4", "Unknown")
                
            if "Downstream" in data:
                ds = data["Downstream"].values()
                ds_snrs = [float(v["SNRLevel"]) for v in ds if "SNRLevel" in v]
                ds_powers = [float(v["PowerLevel"]) for v in ds if "PowerLevel" in v]
                ds_uncorrect_sum = sum([int(v["Uncorrectables"]) for v in ds if "Uncorrectables" in v])
                
                if ds_snrs: ds_snr_avg = round(sum(ds_snrs) / len(ds_snrs), 2)
                if ds_powers: ds_pow_avg = round(sum(ds_powers) / len(ds_powers), 2)
                
            if "Upstream" in data:
                us = data["Upstream"].values()
                us_powers = [float(v["PowerLevel"]) for v in us if "PowerLevel" in v]
                if us_powers: us_pow_max = round(max(us_powers), 2)
        except Exception as e:
            print(f"Error parsing DOCSIS data: {e}")

        return [cm_status, wan_ipv4, ds_snr_avg, ds_pow_avg, ds_uncorrect_sum, us_pow_max]

    def quit(self):
        try:
            self.driver.quit()
        except:
            pass
