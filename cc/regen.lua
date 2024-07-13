-- Map Regen Files to Dynmap worlds
local regen_files = {
    ["minecraft_the_end.jsonl"] = "DIM1",
    ["minecraft_the_nether.jsonl"] = "DIM-1",
    ["minecraft_overworld.jsonl"] = "world"
}

-- Map Minecraft worlds to Dynmap worlds
local worlds = {
    ["DIM1"] = "minecraft:the_end",
    ["DIM-1"] = "minecraft:the_nether",
    ["world"] = "minecraft:overworld"
}

-- Colors 
-- Primary Regions (Have Protected Blocks)
local primary_shading = "#648FCC"  -- #0000CC (Blue)
local primary_border = "#648FFF"  -- #0000FF (Blue)

-- Secondary Regions (Borders Primary Regions)
local secondary_shading = "#785EF0"  -- #CC00CC (Purple)
local secondary_border = "#785EFF"  -- #FF00FF (Purple)

-- Regen Regions (To Be Deleted For Regeneration)
local regen_shading = "#DC267F"  -- #CC0000 (Red)
local regen_border = "#DC26FF"  -- #FF0000 (Red)

-- Where to download the regen files from
local download_base_path = "https://mc.foxgirl.land/regen/"

-- https://github.com/jonko0493/ComputerCartographer/wiki/Guide#addrectanglemarker
local cart = peripheral.wrap("cartographer_1")

-- Clear out old marker sets
cart.removeMarkerSet("regen")
cart.removeMarkerSet("noregen")

-- Add marker set
cart.addMarkerSet("regen", "Regions to Regenerate")
cart.addMarkerSet("noregen", "Regions to Keep")

for regen_file, dynmap_world in pairs(regen_files) do
    -- Get Regen file and process
    local url = download_base_path .. regen_file
    local request = http.get(url)

    -- Skip if Regen file not found
    if request == nil then
        print("Failed to obtain \"" .. regen_file .. "\"! Skipping...")
        goto continue
    end

    -- Change Dynmap map
    print("Setting map to: " .. worlds[dynmap_world])
    cart.setCurrentMap(dynmap_world)

    -- Read through line by line
    local line = request.readLine()
    while line do
        -- Sleep for 2 game ticks
        os.sleep(0.1)  -- 0.05 is 1 game tick?

        -- Debug contents
        -- print(line)

        -- Convert line to JSON data
        local data = textutils.unserializeJSON(line)

        -- Get Region Coordinates
        local region_x = data["x"]
        local region_z = data["z"]

        -- Lower Bound Block Coordinates
        local lower_x = region_x * 16 * 32
        local lower_z = region_z * 16 * 32

        -- Upper Bound Block Coordinates
        local upper_x = lower_x + (16 * 32)
        local upper_z = lower_z + (16 * 32)

        -- Add Rectangle Marker to represent region
        local coordinate = "(" .. region_x .. ", " .. region_z .. ")"
        local marker_key = dynmap_world .. "-" .. coordinate

        -- Mark regions on map
        if data["safe"] == true or data["force_safe"] == true then
            local shading_color = primary_shading
            local border_color = primary_border
            local description = nil
            if data["reason"] == "secondary" then
                shading_color = secondary_shading
                border_color = secondary_border
            end

            -- Check if a description was provided and add the first one to the marker
            if #data["description"] > 0 then
                for _, v in ipairs(data["description"]) do
                    description = v["comment"]
                end
            end

            -- Add Marker to map
            local success = cart.addRectangleMarker("noregen", marker_key, "Region " .. coordinate, description, shading_color, 0.8, border_color, 0.4, 2, lower_x, lower_z, upper_x, upper_z)

            -- Print Log
            if not success then
                local bounding = "(" .. lower_x .. ", " .. lower_z .. ", " .. upper_x .. ", " .. upper_z .. ")"
                print("Keep Region: " .. coordinate .. " at " .. worlds[dynmap_world] .. " Bounding: " .. bounding .. " - Added: " .. tostring(success))
            end
        else
            local description = "Region to regenerate..."
            -- Check if a description was provided and add the first one to the marker
            for _, v in ipairs(data["description"]) do
                description = v["comment"]
            end

            -- Add Marker to map
            local success = cart.addRectangleMarker("regen", marker_key, "Region " .. coordinate, description, regen_shading, 0.8, regen_border, 0.4, 2, lower_x, lower_z, upper_x, upper_z)

            -- Print Log
            if not success then
                local bounding = "(" .. lower_x .. ", " .. lower_z .. ", " .. upper_x .. ", " .. upper_z .. ")"
                print("Regen Region: " .. coordinate .. " at " .. worlds[dynmap_world] .. " Bounding: " .. bounding .. " - Added: " .. tostring(success))
            end
        end

        line = request.readLine()
    end

    ::continue::
end
