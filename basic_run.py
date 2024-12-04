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

import os
import time
from pathlib import Path
import subprocess

class DonkeyKongController:
    # Action mappings
    ACTIONS = {
        0: "NOOP",
        1: "Right",
        2: "Left",
        3: "Up",
        4: "Down",
        5: "Jump",
        6: "Right+Jump",
        7: "Left+Jump"
    }
    
    def __init__(self):
        self.base_path = Path("C:/Users/Patrick Taylor/PycharmProjects/dk2")
        self.state_file = self.base_path / "state_log.txt"
        self.command_file = self.base_path / "command.txt"
        self.status_file = self.base_path / "mame_status.txt"
        self.mame_process = None
        self.current_frame = 0
        self.last_state = None

    def start_mame(self):
        """Launch MAME with the Lua script"""
        mame_path = r"C:\Users\Patrick Taylor\Emulation\mame"
        rom_path = r"C:\Users\Patrick Taylor\Emulation\roms"
        lua_script = self.base_path / "lua" / "read_mem.lua"
        
        mame_command = [
            mame_path,
            "dkong",
            "-window",
            "-rompath", rom_path,
            "-autoboot_script", str(lua_script),
          #  '-debug'
        ]
        
        self.mame_process = subprocess.Popen(mame_command, shell=True)
        time.sleep(2)  # Wait for MAME to start
        
        # Wait for MAME to be ready
        while not self.is_mame_ready():
            time.sleep(0.1)

    def is_mame_ready(self):
        """Check if MAME is running and ready"""
        if not self.status_file.exists():
            return False
            
        with open(self.status_file, 'r') as f:
            status = f.read().strip()
            return status.startswith("RUNNING:")

    def read_state(self):
        """Read and parse the current game state"""
        if not self.state_file.exists():
            return None
            
        try:
            with open(self.state_file, 'r') as f:
                lines = f.readlines()
                
            state = {}
            for line in lines:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    try:
                        state[key.strip()] = int(value.strip())
                    except ValueError:
                        continue
                        
            # Update current frame
            self.current_frame = state.get('Frame', 0)
            self.last_state = state
            return state
        except Exception as e:
            print(f"Error reading state: {e}")
            return None

    def send_action(self, action):
        """Send action to MAME"""
        if action not in self.ACTIONS:
            print(f"Invalid action: {action}")
            return
            
        try:
            with open(self.command_file, 'w') as f:
                f.write(str(action))
        except Exception as e:
            print(f"Error sending action: {e}")

    def close(self):
        """Clean up resources"""
        if self.mame_process:
            self.mame_process.terminate()
            
        # Clean up files
        for file in [self.state_file, self.command_file, self.status_file]:
            if file.exists():
                file.unlink()

def test_controller():
    """Test the controller functionality"""
    controller = DonkeyKongController()
    
    try:
        print("Starting MAME...")
        controller.start_mame()
        
        print("Running test sequence...")
        frame = 0
        for _ in range(5000):  
            state = controller.read_state()
            if state:
                frame += 1
                #print(f"Frame: {state.get('Frame', 0)} Mario pos: ({state.get('Mario_X', 0)}, {state.get('Mario_Y', 0)})")
                
                # Test different movement patterns
                if frame % 100 < 20:  # Right for 20 frames
                    action = 1  # Right
                elif frame % 100 < 40:  # Left for 20 frames
                    action = 2  # Left
                elif frame % 100 < 50:  # Jump for 10 frames
                    action = 5  # Jump
                elif frame % 100 < 65:  # Right+Jump for 15 frames
                    action = 6  # Right+Jump
                elif frame % 100 < 80:  # Left+Jump for 15 frames
                    action = 7  # Left+Jump
                elif frame % 100 < 90:  # Up for 10 frames
                    action = 3  # Up
                elif frame % 100 < 100:  # Down for 10 frames
                    action = 4  # Down
                
                controller.send_action(action)
            
            time.sleep(0.016)  # ~60fps
            
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        controller.close()

if __name__ == "__main__":
    test_controller()

if __name__ == "__main__":
    test_controller()