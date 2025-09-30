import requests
import time
import json
from datetime import datetime
import threading

class SimpleLotterySystem:
    def __init__(self):
        self.system_active = True
        self.current_numbers = ["", "", "", ""]
        self.last_fetch_time = None
        self.api_status = "Loading..."
        self.firebase_url = "https://nagydbushklams-default-rtdb.firebaseio.com"
        self.top_number_saved = False  # ржЯржк ржирж╛ржорзНржмрж╛рж░ ржПржХржмрж╛рж░ржЗ рж╕рзЗржн рж╣ржмрзЗ
        
    def update_timer(self):
        """Update timer and check if it's time to fetch new numbers"""
        while self.system_active:
            now = datetime.now()
            seconds = now.second
            remaining_seconds = 30 - (seconds % 30)
            
            # Display timer
            print(f"\rTimer: 00:{remaining_seconds:02d}", end="", flush=True)
            
            # Check if it's time to fetch new numbers
            if remaining_seconds == 30:
                self.fetch_current_numbers()
            # Reset saved flag when timer reaches 1 second
            elif remaining_seconds == 1:
                self.clear_inputs()
                self.top_number_saved = False  # ржирждрзБржи рж░рж╛ржЙржирзНржбрзЗрж░ ржЬржирзНржп рж░рж┐рж╕рзЗржЯ
                
            time.sleep(1)
    
    def fetch_current_numbers(self):
        """Fetch current numbers from API"""
        if not self.system_active:
            return
            
        try:
            self.api_status = "Fetching data..."
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {self.api_status}")
            
            # Add timestamp to avoid caching
            timestamp = int(time.time() * 1000)
            url = f'https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json?ts={timestamp}'
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Extract latest 4 numbers
            latest_numbers = []
            for item in data['data']['list'][:4]:
                try:
                    num = int(item['number'])
                    latest_numbers.append(num)
                except (ValueError, KeyError):
                    latest_numbers.append('')
            
            # Update current numbers
            for i in range(4):
                if i < len(latest_numbers):
                    self.current_numbers[i] = latest_numbers[i]
                else:
                    self.current_numbers[i] = ''
            
            self.last_fetch_time = datetime.now()
            self.api_status = "Data loaded successfully"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.api_status}: {self.current_numbers}")
            
            # рж╢рзБржзрзБржорж╛рждрзНрж░ ржПржХржмрж╛рж░ ржЯржк ржирж╛ржорзНржмрж╛рж░ рж╕рзЗржн ржХрж░ржмрзЗ
            if not self.top_number_saved and self.current_numbers[0] != "":
                self.save_top_number_to_firebase()
                self.top_number_saved = True  # ржПржХржмрж╛рж░ рж╕рзЗржн ржХрж░рзЗржЗхБЬцнв
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Top number already saved or empty, skipping...")
            
        except Exception as error:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetch error: {error}")
            self.api_status = "Error loading data"
    
    def clear_inputs(self):
        """Clear all number inputs"""
        self.current_numbers = ["", "", "", ""]
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Inputs cleared")
    
    def save_top_number_to_firebase(self):
        """Save only the top (first) number to Firebase database - ONLY ONCE"""
        try:
            if not self.current_numbers or self.current_numbers[0] == "":
                print("No valid top number to save")
                return
            
            top_number = self.current_numbers[0]
            
            # Create data structure with only the top number
            data_to_save = {
                "top_number": top_number,
                "timestamp": datetime.now().isoformat(),
                "api_status": "TOP NUMBER SAVED ONCE",
                "full_numbers": self.current_numbers  # рж░рзЗржлрж╛рж░рзЗржирзНрж╕рзЗрж░ ржЬржирзНржп рж╕ржм ржирж╛ржорзНржмрж╛рж░
            }
            
            # Save to Firebase using REST API
            url = f"{self.firebase_url}/fhfhhfhfufuucuvhjgjjgufj/lottery_data.json"
            response = requests.post(url, json=data_to_save)
            
            if response.status_code == 200:
                print(f"ЁЯОп [{datetime.now().strftime('%H:%M:%S')}] TOP NUMBER SAVED TO FIREBASE: {top_number}")
                print(f"тЬЕ ржПржЗ ржирж╛ржорзНржмрж╛рж░ржЯрж┐ рж╢рзБржзрзБржорж╛рждрзНрж░ ржПржХржмрж╛рж░ржЗ рж╕рзЗржн ржХрж░рж╛ рж╣рзЯрзЗржЫрзЗ: {top_number}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Firebase save failed: {response.status_code}")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Firebase save error: {e}")
    
    def start_system(self):
        """Start the lottery prediction system"""
        print("ЁЯО░ Lottery Prediction System Started")
        print("ЁЯЯв System: ACTIVE")
        print("ЁЯТ╛ Mode: TOP number saved ONLY ONCE per round")
        print("=" * 50)
        
        # Start timer in a separate thread
        timer_thread = threading.Thread(target=self.update_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Initial fetch
        self.fetch_current_numbers()
        
        # Keep the main thread alive
        try:
            while self.system_active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nЁЯЫС Stopping system...")
            self.system_active = False
    
    def stop_system(self):
        """Stop the lottery prediction system"""
        self.system_active = False
        print("ЁЯФ┤ System: INACTIVE")

# Main execution
if __name__ == "__main__":
    lottery_system = SimpleLotterySystem()
    
    try:
        lottery_system.start_system()
    except Exception as e:
        print(f"System error: {e}")
    finally:
        lottery_system.stop_system()
