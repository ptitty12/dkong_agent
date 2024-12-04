-- Define hardware interfaces and screen device
local ioport = manager.machine.ioport
local screen = manager.machine.screens[":screen"]
local in0 = ioport.ports[":IN0"]

-- Define movement and action fields
local move_right = in0.fields["P1 Right"]
local move_left = in0.fields["P1 Left"]
local move_up = in0.fields["P1 Up"]
local move_down = in0.fields["P1 Down"]
local move_jump = in0.fields["P1 Button 1"]

-- File paths
local command_file_path = "C:\\Users\\Patrick Taylor\\PycharmProjects\\donkey_kong\\command.txt"
local screenshot_directory = "C:\\Users\\Patrick Taylor\\PycharmProjects\\donkey_kong\\hold_frames\\"
local memory_log_path = "C:\\Users\\Patrick Taylor\\PycharmProjects\\donkey_kong\\memory_log.txt"

-- Initialize frame counter
local frame_counter = 0

-- Function to read command from file
function read_command()
    local file = io.open(command_file_path, "r")
    if file then
        local action = file:read("*line") or "None"
        file:close()
        return action
    else
        print("[Lua] Could not open command file.")
        return "None"
    end
end

-- Function to apply direction and jump based on the command
function apply_command(command)
    move_right:set_value(0)
    move_left:set_value(0)
    move_up:set_value(0)
    move_down:set_value(0)
    move_jump:set_value(0)
    
    if command == "Right" then
        move_right:set_value(1)
    elseif command == "Left" then
        move_left:set_value(1)
    elseif command == "Up" then
        move_up:set_value(1)
    elseif command == "Down" then
        move_down:set_value(1)
    elseif command == "Jump" then
        move_jump:set_value(1)
    elseif command == "Right+Jump" then
        move_right:set_value(1)
        move_jump:set_value(1)
    elseif command == "Left+Jump" then
        move_left:set_value(1)
        move_jump:set_value(1)
  --  else
        --print("[Lua] No recognized action, neutral state")
    end
end

-- Function to capture frame and log memory values
function capture_frame_and_log_memory()
    frame_counter = frame_counter + 1
    --local filename = string.format("%sframe_%04d.png", screenshot_directory, frame_counter)
    --screen:snapshot(filename)

    local cpu = manager.machine.devices[":maincpu"]
    local mem = cpu.spaces["program"]
    
    -- Read memory values from specified addresses
    local mem_values = {
        ["6040"] = mem:read_u8(0x6040),
        ["60B3"] = mem:read_u8(0x60B3),
        ["6988"] = mem:read_u8(0x6988),
        ["6203"] = mem:read_u8(0x6203),
        ["6228"] = mem:read_u8(0x6228)
    }

    -- Check if 6040 or 6228 is below 3 and set them to 3 if necessary
    if mem_values["6040"] < 3 then
        mem:write_u8(0x6040, 3)
        print("[Lua] 6040 was below 3, setting to 3.")
    end

    if mem_values["6228"] < 3 then
        mem:write_u8(0x6228, 3)
        print("[Lua] 6228 was below 3, setting to 3.")
    end

    -- Log the values to a file
    --local file = io.open(memory_log_path, "a")
    --file:write(string.format("Frame %04d: 6040=%02X, 60B3=%02X, 6988=%02X, 6203=%02X\n",
                             --frame_counter, mem_values["6040"], mem_values["60B3"],
                            -- mem_values["6988"], mem_values["6203"]))
    --file:close()
end

-- Register the function to run each frame
emu.register_frame_done(function()
    local command = read_command()
    apply_command(command)
    capture_frame_and_log_memory()
end, "frame")
