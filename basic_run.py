import os
import time
import numpy as np
import subprocess


# Paths
mame_path = r"C:\Users\Patrick Taylor\Emulation\mame"
rom_path = r"C:\Users\Patrick Taylor\Emulation\roms"
lua_script_path = r"C:\Users\Patrick Taylor\PycharmProjects\donkey_kong\frame_capture.lua"
command_file_path = r"C:\Users\Patrick Taylor\PycharmProjects\donkey_kong\command.txt"
frame_path_in = r"C:/Users/Patrick Taylor/PycharmProjects/donkey_kong/hold_frames"
lua_script_path = r"C:\Users\Patrick Taylor\PycharmProjects\donkey_kong\ram_searching.lua"
lua_script_path = r"C:\Users\Patrick Taylor\PycharmProjects\dk2\lua\read_mem.lua"

#lua_script_path = r"C:\Users\Patrick Taylor\PycharmProjects\donkey_kong\infinite_lives.lua"
import os
import time
import numpy as np
import subprocess
import json
from pathlib import Path

# Paths
mame_path = r"C:\Users\Patrick Taylor\Emulation\mame"
rom_path = r"C:\Users\Patrick Taylor\Emulation\roms"
lua_script_path = r"C:\Users\Patrick Taylor\PycharmProjects\dk2\lua\read_mem.lua"
state_file_path = r"C:\Users\Patrick Taylor\PycharmProjects\dk2\state.json"


# Launch MAME
def launch_mame():
    mame_command = [
        mame_path,
        "dkong",
        "-window",
        "-rompath", rom_path,
        "-autoboot_script", lua_script_path,
        #'-debug'
    ]
    try:
        print(f"[Python] Launching MAME with command: {' '.join(mame_command)}")
        mame_process = subprocess.Popen(mame_command, shell=True)
        print("[Python] MAME launched successfully")
        return mame_process
    except Exception as e:
        print(f"[Python] Error launching MAME: {e}")
        return None
    

launch_mame()
