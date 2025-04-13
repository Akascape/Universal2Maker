# Universal2Maker for Mac 🍎
A simple GUI application to create universal wheels for Python packages in MacOS.
This application allows users to input a package name, checks its availability on PyPI, installs the package for both x86_64 and arm64 architectures, merges the wheels into a universal wheel, and provides an option to install the universal wheel or save it to a specified location.

![Screenshot](https://github.com/user-attachments/assets/3f1ae609-d4d3-4bf1-a771-7f7b84effedd)

## Why use this tool?
While converting a Python application to executable binaries using PyInstaller, some non-pure Python packages behave differently on both x86_64 (Intel) and arm64 (Apple Silicon). To ensure a universal app that runs on both architectures, we need to use the universal version of these packages.

To create a universal version of the Python app, we use the `—target-architecture “universal2”` option in PyInstaller. If not specified, the device’s native architecture is used. For instance, if your app is arm64-based, it may not work on an x86_64 Mac (unless Rosetta is used). Therefore, it’s recommended to use the universal2 target.

During the conversion process, some packages may display errors because they are distributed separately for both Intel and Apple Silicon. To resolve this issue, we need to obtain the universal version (non-binary) of the package. Not all packages come with universal bindings, for example, Pillow.

To fix this, we can download both wheels for Intel and Silicon, then combine them into a single universal wheel using the [delocate](https://pypi.org/project/delocate/) package. Finally, we can install the universal version to ensure compatibility across all machines.

Universal2Maker is a simple application that automates this process. Simply enter the package name, and it will generate and install the universal package for you in seconds.

## How to install
- Make sure you are using python3 universal version
- Download the source code:
### [<img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/Akascape/Universal2Maker?&color=white&label=Download%20Source%20Code&logo=Python&logoColor=yellow&style=for-the-badge"  width="400">](https://github.com/Akascape/Universal2Maker/archive/refs/heads/main.zip)

- Download the dependencies using **pip3**:
  - tk
  - customtkinter
  - delocate
  - requests
- Run the *universal2maker.py*
- Type the package name and click on `Install` button

Follow me for more stuff like this: [`Akascape`](https://github.com/Akascape/)
### That's all, hope it will help!






