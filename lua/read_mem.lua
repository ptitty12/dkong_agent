-- Initialize hardware interfaces
local cpu = manager.machine.devices[":maincpu"]
local mem = cpu.spaces["program"]
local ioport = manager.machine.ioport
local screen = manager.machine.screens[":screen"]

-- Get start button
local in2 = ioport.ports[":IN2"]
local start_button = in2.fields["1 Player Start"]

-- File path for state output
local log_file_path = "C:\\Users\\Patrick Taylor\\PycharmProjects\\dk2\\state_log.txt"

-- Barrel base addresses
local barrel_addresses = {0x6700, 0x6720, 0x6740, 0x6760, 0x6780, 0x67A0, 0x67C0, 0x67E0}

-- Initialize frame counter and state tracking
local frame_counter = 0
local skip_active = false

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

-- Use the new notifier syntax
emu.add_machine_reset_notifier(function()
    -- Clear the log file at start
    local file = io.open(log_file_path, "w")
    if file then
        file:close()
    end
    -- Start the game
    start_game()
end)

-- Main update function
emu.register_frame_done(function()
    frame_counter = frame_counter + 1
    
    -- Continue checking for skip opportunities
    start_game()
    
    -- Log every 10 frames
    if frame_counter % 10 == 0 then
        local file = io.open(log_file_path, "a")
        if file then
            -- Write frame number
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
            
            file:write("\n")  -- Blank line between frames
            file:close()
        end
    end
    
    -- Reset frameskip if we went into skip mode
    if skip_active and mem:read_u8(0x600A) ~= 7 then
        manager.machine.video.throttled = true
        manager.machine.video.frameskip = 0
        skip_active = false
    end
end, "frame")