import pygame
import re
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 256  # Original DK screen width
SCREEN_HEIGHT = 256  # Original DK screen height
SCALE = 2  # Scale factor to make it bigger
MARIO_SIZE = 8
BARREL_SIZE = 6
FRAME_ADVANCE_SPEED = 1  # How many frames to advance when holding right

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE, SCREEN_HEIGHT * SCALE))
pygame.display.set_caption("Donkey Kong State Replay")

def parse_state_log(filename):
    states = []
    current_state = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_state:
                    states.append(current_state.copy())  # Use copy() to prevent reference issues
                    current_state = {}
                continue
                
            if ":" in line:
                key, value = line.split(":", 1)
                try:
                    current_state[key.strip()] = int(value.strip())
                except ValueError:
                    continue
    
    if current_state:  # Don't forget the last state if file doesn't end with blank line
        states.append(current_state.copy())
    
    return states

def draw_state(state):
    screen.fill(BLACK)
    
    # Draw Mario (always draw Mario even if dead)
    mario_x = state.get('Mario_X', 0) * SCALE
    mario_y = state.get('Mario_Y', 0) * SCALE
    color = YELLOW if state.get('Mario_Hammer', 0) == 1 else RED
    pygame.draw.circle(screen, color, (mario_x, mario_y), MARIO_SIZE * SCALE)
    
    # Draw barrels
    for i in range(1, 9):  # Up to 8 barrels
        barrel_key = f'Barrel_{i}'
        if f'{barrel_key}_Status' in state and state[f'{barrel_key}_Status'] != 0:
            barrel_x = state[f'{barrel_key}_X'] * SCALE
            barrel_y = state[f'{barrel_key}_Y'] * SCALE
            color = RED if state.get(f'{barrel_key}_Crazy', 0) == 1 else BLUE
            pygame.draw.circle(screen, color, (barrel_x, barrel_y), BARREL_SIZE * SCALE)
    
    # Draw detailed HUD
    font = pygame.font.Font(None, 24)
    y_offset = 10
    line_height = 20
    
    # Basic info
    hud_lines = [
        f"Frame: {state.get('Frame', 0)}  Level: {state.get('Level', 0)}  Alive: {state.get('Mario_Alive', 1)}",
        "",
        f"Mario Status:",
        f"Position: ({state.get('Mario_X', 0)}, {state.get('Mario_Y', 0)})",
        f"On Ladder: {state.get('Mario_OnLadder', 0)}",
        f"Jumping: {state.get('Mario_Jumping', 0)}",
        f"Hammer: {state.get('Mario_Hammer', 0)}",
        "",
        f"Lives: {state.get('Lives', 0)}",
        "",
        f"Timer: {state.get('Timer', 0)}",
        f"Bonus: {state.get('Bonus', 0)}",
        f"Score: {state.get('Score_High', 0)}{state.get('Score_Mid', 0)}{state.get('Score_Low', 0)}"
    ]
    
    # Draw each line of the HUD
    for i, line in enumerate(hud_lines):
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (10, y_offset + i * line_height))

def main():
    # Load states from log file
    states = parse_state_log("C:\\Users\\Patrick Taylor\\PycharmProjects\\dk2\\state_log.txt")
    print(f"Loaded {len(states)} states")
    
    running = True
    state_index = 0
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    state_index = 0
        
        # Handle held keys for continuous movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            state_index = min(state_index + FRAME_ADVANCE_SPEED, len(states) - 1)
        if keys[pygame.K_LEFT]:
            state_index = max(state_index - FRAME_ADVANCE_SPEED, 0)
        
        if state_index < len(states):
            draw_state(states[state_index])
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()