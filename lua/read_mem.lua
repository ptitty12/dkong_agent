-- Initialize hardware interfaces
local cpu = manager.machine.devices[":maincpu"]
local mem = cpu.spaces["program"]
local ioport = manager.machine.ioport
local screen = manager.machine.screens[":screen"]

-- Get input ports
local in2 = ioport.ports[":IN2"]
local in0 = ioport.ports[":IN0"]
local start_button = in2.fields["1 Player Start"]
local move_right = in0.fields["P1 Right"]
local move_left = in0.fields["P1 Left"]
local move_up = in0.fields["P1 Up"]
local move_down = in0.fields["P1 Down"]
local move_jump = in0.fields["P1 Button 1"]

-- File paths
local state_file_path = "C:\\Users\\Patrick Taylor\\PycharmProjects\\dk2\\state_log.txt"
local command_file_path = "C:\\Users\\Patrick Taylor\\PycharmProjects\\dk2\\command.txt"
local status_file_path = "C:\\Users\\Patrick Taylor\\PycharmProjects\\dk2\\mame_status.txt"

-- Barrel base addresses
local barrel_addresses = {0x6700, 0x6720, 0x6740, 0x6760, 0x6780, 0x67A0, 0x67C0, 0x67E0}

-- Initialize counters and state
local frame_counter = 0
local skip_active = false
local death_frame = 0
local death_cooldown = 30

function write_status(status)
    local file = io.open(status_file_path, "w")
    if file then
        file:write(status)
        file:close()
    end
end

function read_command()
    local file = io.open(command_file_path, "r")
    if not file then return 0 end
    
    local action = tonumber(file:read("*line")) or 0
    file:close()
    return action
end

function apply_command(action)
    -- Reset all inputs
    move_right:set_value(0)
    move_left:set_value(0)
    move_up:set_value(0)
    move_down:set_value(0)
    move_jump:set_value(0)
    
    -- Apply new action
    if action == 1 then  -- Right
        move_right:set_value(1)
    elseif action == 2 then  -- Left
        move_left:set_value(1)
    elseif action == 3 then  -- Up
        move_up:set_value(1)
    elseif action == 4 then  -- Down
        move_down:set_value(1)
    elseif action == 5 then  -- Jump
        move_jump:set_value(1)
    elseif action == 6 then  -- Right+Jump
        move_right:set_value(1)
        move_jump:set_value(1)
    elseif action == 7 then  -- Left+Jump
        move_left:set_value(1)
        move_jump:set_value(1)
    end
end

function start_game()
    -- Press start button
    start_button:set_value(1)
    
    -- Skip intro by modifying mode values
    if mem:read_u8(0x6227) == 0 then  -- If we're at intro/start screen
        mem:write_u8(0x6227, 1)  -- Set to level 1
        mem:write_u8(0x6228, 3)  -- Set lives to 3
    end
    
    -- Skip the climbing animation
    if mem:read_u8(0x6005) == 3 and mem:read_u8(0x600A) == 7 then
        manager.machine.video.throttled = false
        manager.machine.video.frameskip = 8
        skip_active = true
    elseif skip_active then
        manager.machine.video.throttled = true
        manager.machine.video.frameskip = 0
        skip_active = false
    end
end

-- Initialize on startup
emu.add_machine_reset_notifier(function()
    local file = io.open(state_file_path, "w")
    if file then
        file:close()
    end
    write_status("STARTING")
    start_game()
end)

-- Main update function
emu.register_frame_done(function()
    frame_counter = frame_counter + 1
    
    -- Check for death and manage lives
    if mem:read_u8(0x6228) < 3 then
        if death_frame == 0 then  -- Just died
            death_frame = frame_counter  -- Mark when death occurred
        elseif (frame_counter - death_frame) >= death_cooldown then
            -- Wait period is over, reset lives
            mem:write_u8(0x6228, 3)
            death_frame = 0  -- Reset death frame counter
        end
    end
    
    -- Apply command from Python
    local action = read_command()
    apply_command(action)
    
    -- Log every 10 frames
    if frame_counter % 10 == 0 then
        local file = io.open(state_file_path, "w")  -- Use "w" instead of "a" to avoid growing file
        if file then
            -- Add frame number first
            file:write("Frame: " .. frame_counter .. "\n")
            
            -- Mario state
            file:write("Mario_Alive: " .. mem:read_u8(0x6200) .. "\n")
            file:write("Mario_X: " .. mem:read_u8(0x6203) .. "\n")
            file:write("Mario_Y: " .. mem:read_u8(0x6205) .. "\n")
            file:write("Mario_OnLadder: " .. mem:read_u8(0x6215) .. "\n")
            file:write("Mario_Jumping: " .. mem:read_u8(0x6216) .. "\n")
            file:write("Mario_Hammer: " .. mem:read_u8(0x6217) .. "\n")
            
            -- Game state
            file:write("Level: " .. mem:read_u8(0x6227) .. "\n")
            file:write("Lives: " .. mem:read_u8(0x6228) .. "\n")
            file:write("Stage: " .. mem:read_u8(0x6229) .. "\n")
            file:write("Timer: " .. mem:read_u8(0x638C) .. "\n")
            file:write("Bonus: " .. mem:read_u8(0x62B1) .. "\n")
            
            -- Score
            file:write("Score_High: " .. mem:read_u8(0x60B2) .. "\n")
            file:write("Score_Mid: " .. mem:read_u8(0x60B3) .. "\n")
            file:write("Score_Low: " .. mem:read_u8(0x60B4) .. "\n")
            
            -- Barrels
            for i, addr in ipairs(barrel_addresses) do
                if mem:read_u8(addr) ~= 0 then
                    file:write("Barrel_" .. i .. "_Status: " .. mem:read_u8(addr) .. "\n")
                    file:write("Barrel_" .. i .. "_Crazy: " .. mem:read_u8(addr + 1) .. "\n")
                    file:write("Barrel_" .. i .. "_Motion: " .. mem:read_u8(addr + 2) .. "\n")
                    file:write("Barrel_" .. i .. "_X: " .. mem:read_u8(addr + 3) .. "\n")
                    file:write("Barrel_" .. i .. "_Y: " .. mem:read_u8(addr + 5) .. "\n")
                end
            end
            
            file:write("\n")
            file:close()
            
            -- Update status
            write_status("RUNNING:" .. frame_counter)
        end
    end
    
    -- Reset frameskip if we went into skip mode
    if skip_active and mem:read_u8(0x600A) ~= 7 then
        manager.machine.video.throttled = true
        manager.machine.video.frameskip = 0
        skip_active = false
    end
end, "frame")