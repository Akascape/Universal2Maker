"""
Universal2Maker
by Akascape
Version: 1.0.0
Date: 2025-04-13
Description:
A simple GUI application to create universal wheels for Python packages.
This application allows users to input a package name, checks its availability on PyPI,
installs the package for both x86_64 and arm64 architectures, merges the wheels into a universal wheel,
and provides an option to install the universal wheel or save it to a specified location.

Dependencies:
- tk
- customtkinter
- requests
- delocate
"""

import customtkinter
from tkinter import messagebox
import requests
import os
import subprocess
import delocate
import shutil
from datetime import datetime
import platform
import threading

HEIGHT = 350
WIDTH = 400

if platform.system() != "Darwin":
    messagebox.showerror("Unsupported OS!!!", "This application is only for macOS systems.")
    exit()
    
root = customtkinter.CTk()
root.title("Universal2Maker")
root.geometry((f"{WIDTH}x{HEIGHT}"))
root.resizable(False, False)

def on_closing():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

working_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")

def install_action():
    def cleanup():
        textbox.configure(state="disabled")
        entry_entry.configure(state="normal")
        install_button.configure(state="normal")
        for file in os.listdir(working_directory):
            file_path = os.path.join(working_directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                textbox.insert("end", f"Failed to delete {file_path}. Reason: {e}\nDelete the cache folder manually.\n")
                cleanup()
                return

        root.update_idletasks()

    package_name = entry_entry.get()
    if not package_name:
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("end", "Please enter a package name.\n")
        cleanup()
        return

    entry_entry.configure(state="disabled")
    install_button.configure(state="disabled")
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")

    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            textbox.insert("end", f"{package_name} is available on PyPI.\n")
        else:
            textbox.insert("end", f"{package_name} is not available on PyPI.\n")
            cleanup()
            return
    except requests.RequestException as e:
        textbox.insert("end", f"Error checking PyPI: {e}\n")
        cleanup()
        return

    textbox.insert("end", f"Downloading {package_name} & dependencies (if available)...\n")

    if not os.path.exists(working_directory):
        os.makedirs(working_directory)
    else:
        for file in os.listdir(working_directory):
            file_path = os.path.join(working_directory, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                textbox.insert("end", f"Failed to delete {file_path}. Reason: {e}\nDelete the cache folder manually.\n")
                cleanup()
                return

    os.chdir(working_directory)

    try:
        subprocess.run(
            ["arch", "-x86_64", "python3", "-m", "pip", "wheel", package_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        textbox.insert("end", f"Error installing {package_name} for x86_64: {e.stderr.decode()}\n")
        cleanup()
        return
    
    try:
        subprocess.run(
            ["arch", "-arm64", "python3", "-m", "pip", "wheel", package_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        textbox.insert("end", f"Error installing {package_name} for arm64: {e.stderr.decode()}\n")
        cleanup()
        return

    # Store the two files in variables
    files = os.listdir(working_directory)
    whl_files = [f for f in files if f.endswith(".whl")]
    if len(whl_files) >= 2:
        # Sort files to ensure consistent order and match by starting name
        whl_files.sort()
        base_names = set(os.path.splitext(f)[0].rsplit("-", 2)[0] for f in whl_files)
        for base_name in base_names:
            matching_files = [f for f in whl_files if f.startswith(base_name)]
            if len(matching_files) >= 2:
                file1, file2 = matching_files[:2]
                textbox.insert("end", f"Wheel 1: {file1}\n")
                textbox.insert("end", f"Wheel 2: {file2}\n")
            else:
                textbox.insert("end", f"\nMatching wheels not found for base name: {base_name}. Maybe there's no specific need for x86_64 or arm64.\n")
                continue
            # Remove all previous files from the universal2_wheels folder
            universal2_wheels_path = os.path.join(working_directory, "universal2_wheels")
            if os.path.exists(universal2_wheels_path):
                for file in os.listdir(universal2_wheels_path):
                    file_path = os.path.join(universal2_wheels_path, file)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        textbox.insert("end", f"Failed to delete {file_path}. Reason: {e}\n")
                        cleanup()
                        return
            try:
                subprocess.run(
                    [
                        "delocate-merge",
                        "-w",
                        "universal2_wheels",
                        file1,
                        file2,
                    ],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                textbox.insert("end", f"Successfully merged wheels for {base_name} into universal2_wheels.\n")
            except subprocess.CalledProcessError as e:
                textbox.insert("end", f"Error merging wheels for {base_name} using Delocate: {e.stderr.decode()}\n")
                continue

            # Move the universal2_wheels folder outside of the cache folder and rename it using shutil
            try:
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                files = os.listdir(os.path.join(working_directory, "universal2_wheels"))

                wheel_file = next((f for f in files if f.endswith(".whl")), None)

                destination_path = os.path.join(
                    os.path.dirname(working_directory), f"{base_name}_universal2_{current_time}"
                )

                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)

                shutil.copy(os.path.join(working_directory, "universal2_wheels", wheel_file), destination_path)
                textbox.insert("end", f"Moving Files for {base_name}...\n")

            except Exception as e:
                textbox.insert("end", f"Error copying file for {base_name}: {e}\n")
                continue

            # Ask the user if they want to install the universal wheel now
            result = messagebox.askquestion(
                "Install Universal Wheel?", f"Do you want to install the universal wheel for {base_name} now?"
            )

            if result == "yes":
                try:
                    universal_wheel_path = os.path.join(destination_path, wheel_file)
                    subprocess.run(
                        ["pip3", "install", universal_wheel_path],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    textbox.insert("end", f"Successfully installed {wheel_file} for {base_name}.\n")
                except subprocess.CalledProcessError as e:
                    textbox.insert("end", f"Error installing universal wheel for {base_name}: {e.stderr.decode()}\n")
                    continue

                try:
                    installed_version = subprocess.run(
                        ["pip3", "show", base_name],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    ).stdout
                    version_line = next((line for line in installed_version.splitlines() if line.startswith("Version:")), None)
                    if version_line:
                        version = version_line.split(":", 1)[1].strip()
                        textbox.insert("end", f"Installed version for {base_name}: {version}\n")
                    else:
                        textbox.insert("end", f"Installed version information not found for {base_name}.\n")
                except subprocess.CalledProcessError as e:
                    textbox.insert("end", f"Error checking installed version for {base_name}: {e.stderr}\n")
            else:
                textbox.insert("end", f"Universal wheel for {base_name} saved at: {destination_path}\n")
    else:
        textbox.insert("end", "Wheels not downloaded or not valid .whl files.\n")

    cleanup()

title_label = customtkinter.CTkLabel(root, text="Universal2Maker", font=("Arial", 25))
title_label.pack(pady=10)

# Create a label and entry
entry_label = customtkinter.CTkLabel(root, text="Enter Package Name")
entry_label.pack(pady=5)
entry_entry = customtkinter.CTkEntry(root, width=300, justify="center", placeholder_text="PyPI Package")
entry_entry.pack(pady=5)

def threaded_install_action():
    threading.Thread(target=install_action).start()

install_button = customtkinter.CTkButton(root, text="Install", width=300, command=threaded_install_action)
install_button.pack(pady=10)
# Create a readonly textbox
log_label = customtkinter.CTkLabel(root, text="Logs")
log_label.pack()

textbox = customtkinter.CTkTextbox(root, width=300, height=100)
textbox.pack(pady=10)
textbox.configure(state="disabled")

info_label = customtkinter.CTkLabel(
    root, 
    text="Version: 1.0.0\nDeveloper: Akascape", 
    font=("Arial", 10), 
)
info_label.pack()

root.mainloop()
