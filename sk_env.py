import gymnasium as gym
import numpy as np
from gymnasium import spaces
import time

class DonkeyKongEnv(gym.Env):
    def __init__(self, controller):
        super().__init__()
        
        # Store the controller that interfaces with MAME
        self.controller = controller
        
        # Define action space (8 possible actions)
        self.action_space = spaces.Discrete(8)
        
        self.observation_space = spaces.Dict({
            "mario_x": spaces.Box(low=0, high=255, shape=(1,), dtype=np.uint8),  # Scalar as 1D array
            "mario_y": spaces.Box(low=0, high=255, shape=(1,), dtype=np.uint8),  # Scalar as 1D array
            "mario_on_ladder": spaces.Discrete(2),
            "mario_jumping": spaces.Discrete(2),
            "mario_hammer": spaces.Discrete(2),
            "barrels": spaces.Box(low=0, high=255, shape=(8, 5), dtype=np.uint8),  # Already multi-dimensional
            "level": spaces.Discrete(5),
            "lives": spaces.Discrete(4),
            "score_high": spaces.Discrete(100),
            "score_mid": spaces.Discrete(100),
            "score_low": spaces.Discrete(100),
        })


        # Initialize tracking variables
        self.height_checkpoints = set()  # Track reached height milestones
        self.last_score = 0
        self.last_state = None

    def _calculate_score(self, state):
        """Convert the three score components into a single number"""
        high = state.get('Score_High', 0)
        mid = state.get('Score_Mid', 0)
        low = state.get('Score_Low', 0)
        return high * 10000 + mid * 100 + low

    def _get_height_reward(self, current_y):
        """Calculate reward for climbing based on checkpoints"""
        # Convert Y position to checkpoint (every 10 pixels)
        checkpoint = (255 - current_y) // 10  # Invert Y since lower value means higher in DK
        reward = 0
        
        # If this is a new checkpoint, give reward
        if checkpoint not in self.height_checkpoints:
            self.height_checkpoints.add(checkpoint)
            reward = 10  # Reward for reaching new height
            
        return reward

    def _get_obs(self, state):
        """Convert raw state to flattened observation space format"""
        mario_x = np.array([state.get('Mario_X', 0)], dtype=np.uint8)
        mario_y = np.array([state.get('Mario_Y', 0)], dtype=np.uint8)
        mario_on_ladder = state.get('Mario_OnLadder', 0)
        mario_jumping = state.get('Mario_Jumping', 0)
        mario_hammer = state.get('Mario_Hammer', 0)

        barrels = np.zeros((8, 5), dtype=np.uint8)
        for i in range(8):
            barrel_base = f'Barrel_{i+1}'
            if f'{barrel_base}_Status' in state:
                barrels[i] = [
                    state[f'{barrel_base}_Status'],
                    state[f'{barrel_base}_Crazy'],
                    state[f'{barrel_base}_Motion'],
                    state[f'{barrel_base}_X'],
                    state[f'{barrel_base}_Y']
                ]

        return {
            "mario_x": mario_x,
            "mario_y": mario_y,
            "mario_on_ladder": mario_on_ladder,
            "mario_jumping": mario_jumping,
            "mario_hammer": mario_hammer,
            "barrels": barrels,
            "level": state.get('Level', 1),
            "lives": state.get('Lives', 3),
            "score_high": state.get('Score_High', 0),
            "score_mid": state.get('Score_Mid', 0),
            "score_low": state.get('Score_Low', 0),
        }


    def _get_reward(self, state):
        """Calculate reward based on state"""
        reward = 0
        
        # Height reward
        current_y = state.get('Mario_Y', 0)
        reward += self._get_height_reward(current_y)
        
        # Score reward
        current_score = self._calculate_score(state)
        if self.last_score is not None:
            score_difference = current_score - self.last_score
            if score_difference > 0:
                reward += score_difference / 100  # Scale the score reward
        self.last_score = current_score
        
        # Jump penalty
        if state.get('Mario_Jumping', 0) == 1:
            reward -= 0.2  # Assuming the barrel jump reward is 10, penalty is half
        
        # Alive bonus
        if state.get('Mario_Alive', 1) == 1:
            reward += 0.1
        
        # Death penalty
        if state.get('Mario_Alive', 1) == 0:
            reward -= 50
            
        return reward

    def reset(self, seed=None):
        """Reset the environment for a new episode"""
        super().reset(seed=seed)
        
        # Reset tracking variables
        self.height_checkpoints.clear()
        self.last_score = 0
        
        # Wait for valid state with lives = 3 and Mario alive
        state = None
        while True:
            state = self.controller.read_state()
            if state and state.get('Lives', 0) == 3 and state.get('Mario_Alive', 1) == 1:
                # Optionally, add position check
                mario_x = state.get('Mario_X', 0)
                mario_y = state.get('Mario_Y', 0)
                if mario_x > 0 and mario_y > 0:  # Ensure Mario is in a valid position
                    break
            time.sleep(0.016)  # Wait for the game to stabilize
        
        print(f"Reset complete - Lives: {state.get('Lives')}, Mario position: ({state.get('Mario_X')}, {state.get('Mario_Y')})")    
        self.last_state = state
        return self._get_obs(state), {}

    def step(self, action):
        """Execute action and return new state."""
        # Send action to MAME
        self.controller.send_action(action)

        # Get new state
        new_state = self.controller.read_state()

        # Calculate reward
        reward = self._get_reward(new_state)

        # Episode ends if Mario dies
        done = new_state.get('Mario_Alive', 1) == 0

        # Handle truncation (e.g., max steps per episode if defined)
        max_steps = 5000  # Define your max step limit
        truncated = self.controller.current_frame >= max_steps

        # Update last state
        self.last_state = new_state

        return self._get_obs(new_state), reward, done, truncated, {}



    def close(self):
        """Clean up resources"""
        self.controller.close()
