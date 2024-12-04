import os
import time
import numpy as np
import subprocess
from sk_env import DonkeyKongEnv

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
        self.expected_frame = 0  # Track what frame we expect to see



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
                        
            # Update frames
            frame = state.get('Frame', 0)
            # Only report actual sync issues (not expected 10-frame jumps)
            if frame != self.expected_frame and abs(frame - self.expected_frame) != 10:
                print(f"Frame sync issue - Expected: {self.expected_frame}, Got: {frame}")
            self.expected_frame = frame
            
            self.current_frame = frame
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
        #for file in [self.state_file, self.command_file, self.status_file]:
            #Eif file.exists():
                #file.unlink()

def test_controller():
    """Test the controller functionality"""
    controller = DonkeyKongController()
    
    try:
        print("Starting MAME...")
        controller.start_mame()
        
        print("Running test sequence...")
        for _ in range(5000):  
            state = controller.read_state()
            if state:
                print(f"Python frame: {controller.expected_frame}, MAME frame: {state.get('Frame', 0)}")
                
                # Test different movement patterns
                if controller.expected_frame % 100 < 20:  # Right for 20 frames
                    action = 1  # Right
                elif controller.expected_frame % 100 < 40:  # Left for 20 frames
                    action = 2  # Left
                elif controller.expected_frame % 100 < 50:  # Jump for 10 frames
                    action = 5  # Jump
                elif controller.expected_frame % 100 < 65:  # Right+Jump for 15 frames
                    action = 6  # Right+Jump
                elif controller.expected_frame % 100 < 80:  # Left+Jump for 15 frames
                    action = 7  # Left+Jump
                elif controller.expected_frame % 100 < 90:  # Up for 10 frames
                    action = 3  # Up
                elif controller.expected_frame % 100 < 100:  # Down for 10 frames
                    action = 4  # Down
                
                controller.send_action(action)
            
            time.sleep(0.016)  # ~60fps
            
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        controller.close()

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import os
import time
from sk_env import DonkeyKongEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

if __name__ == "__main__":
    controller = DonkeyKongController()
    controller.start_mame()

    # Create the environment
    vec_env = make_vec_env(lambda: DonkeyKongEnv(controller), n_envs=1)

    # Initialize PPO with MultiInputPolicy
    model = PPO("MultiInputPolicy", vec_env, verbose=1)

    start_time = time.time()
    model.learn(total_timesteps=108000)
    end_time = time.time()
    print(f"Training took {end_time - start_time:.2f} seconds")
    model.save("ppo_donkey_kong")

    # Test the agent
    obs = vec_env.reset()
    for _ in range(1000):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = vec_env.step(action)
        if done:
            obs = vec_env.reset()


