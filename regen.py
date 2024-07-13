import os
import argparse
import world
import json
import datetime

def record_regions(dimension: str, processed_region_files: dict):
    output_directory: str = os.path.join("world", "project-regen")
    output_path: str = os.path.join(output_directory, "%s.jsonl" % dimension.replace(":", "_"))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(output_path, mode="w") as file:
        for key in processed_region_files:
            region = processed_region_files[key]
            file.write("%s\n" % json.dumps(region))
            # print(json.dumps(region))

def get_region_file_coordinates(path: str):
    base = path.split("/")[-1]
    split = base.split(".")

    return int(split[1]), int(split[2])

if __name__ == "__main__":
    dimensions = {
        "minecraft:the_nether": "world/DIM-1/region",
        "minecraft:the_end": "world/DIM1/region",
        "minecraft:overworld": "world/region"
    }

    hidden_blocks = ["minecraft:air"]

    # Mark Primary Regions as Safe
    for dimension in dimensions:
        # Get Region Folder Path
        region_folder_paths = dimensions[dimension]

        # Table of Region Files
        processed_region_files = {}

        region_files_paths: list[str] = world.get_files(folder_path=region_folder_paths)

        # Mark Primary Regions as Safe
        print("Scanning for primary regions...")
        print("-"*40)
        for region_file_path in region_files_paths:
            mark_safe: bool = False
            mark_description: list[dict] = []
            for block_x, block_y, block_z, block, block_entity in world.get_block_entities(region_file_path=region_file_path, hidden_blocks=hidden_blocks):
                # print("Block Entity: %s - %s" % (block_entity["id"], type(block_entity["id"])))
                if str(block_entity["id"]) == "waystones:sharestone":
                    # print("‣ Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))
                    print("‣ Region: %s - Block: (%i, %i, %i): %s" % (region_file_path, block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id)))
                    mark_safe = True
                    mark_description.append({
                        "comment": "Marked safe cause of sharestone at (%i, %i, %i) in region file" % (block_x, block_y, block_z),
                        "meta": {
                            "x": block_x,
                            "y": block_y,
                            "z": block_z,
                            "name": "%s:%s" % (block.namespace, block.id)
                        }
                    })

                    # Speed up processing since we only need one
                    break

                if str(block_entity["id"]) == "waystones:waystone":
                    if str(block.properties["origin"]) == "player":
                        # print("‣ Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))
                        print("‣ Region: %s - Block: (%i, %i, %i): %s" % (region_file_path, block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id)))
                        mark_safe = True
                        mark_description.append({
                            "comment": "Marked safe cause of player placed waystone at at (%i, %i, %i) in region file" % (block_x, block_y, block_z),
                            "meta": {
                                "x": block_x,
                                "y": block_y,
                                "z": block_z,
                                "name": "%s:%s" % (block.namespace, block.id)
                            }
                        })

                        # Speed up processing since we only need one
                        break

                # Check for Chunkloaders
                chunkloader_ids = [
                    # "createchunkloading:chunk_loader",  # Doesn't have a block entity
                    "chunkloaders:single_chunk_loader_tile",
                    "chunkloaders:basic_chunk_loader_tile",
                    "chunkloaders:advanced_chunk_loader_tile",
                    "chunkloaders:ultimate_chunk_loader_tile",
                    "techreborn:chunk_loader"
                ]
                if str(block_entity["id"]) in chunkloader_ids:
                    print("‣ Region: %s - Block: (%i, %i, %i): %s" % (region_file_path, block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id)))
                    mark_safe = True
                    mark_description.append({
                        "comment": "Marked safe cause of chunk loader at at (%i, %i, %i) in region file" % (block_x, block_y, block_z),
                        "meta": {
                            "x": block_x,
                            "y": block_y,
                            "z": block_z,
                            "name": "%s:%s" % (block.namespace, block.id)
                        }
                    })

            # Get current timezone aware datetime
            timestamp = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")

            region_x, region_z = get_region_file_coordinates(path=region_file_path)
            processed_region_files["(%i, %i)" % (region_x, region_z)] = {
                "timestamp": timestamp,
                "path": region_file_path,
                "x": int(region_x),
                "z": int(region_z),
                "safe": mark_safe,
                "reason": "primary" if mark_safe else "secondary",
                "description": mark_description,
                "force_safe": False,
                "force_unsafe": False
            }
        print("-"*40)
        print()

        # Mark Secondary Regions as Safe
        print("Scanning for secondary regions...")
        print("-"*40)
        temp_region_list = processed_region_files
        for processed_region_file in processed_region_files:
            processed_region = processed_region_files[processed_region_file]

            # Ensure only primary regions are used as a base for scanning nearby regions
            if processed_region["reason"] != "primary":
                continue

            # Only process secondary regions when a primary region is safe
            if processed_region["safe"] == False and processed_region["force_safe"] == False:
                continue

            for x in range(-1, 2):
                for z in range(-1, 2):
                    key = "(%i, %i)" % (int(processed_region["x"])+x, int(processed_region["z"])+z)

                    # Neighboring Region Files are Not Guaranteed to Exist
                    if key not in temp_region_list:
                        continue

                    # Don't Edit Primary Regions
                    if temp_region_list[key]["reason"] == "primary":
                        continue

                    if x == 0 and z == 0:
                        continue
                    
                    temp_region_list[key]["safe"] = True
                    temp_region_list[key]["description"].append({
                        "comment": "Marked safe by being a neighbor to %s region (%i, %i)" % (processed_region["reason"], processed_region["x"], processed_region["z"]),
                        "meta": {
                            "x": processed_region["x"],
                            "z": processed_region["z"]
                        }
                    })
        
        processed_region_files = temp_region_list
        print("-"*40)
        print()

        # Record Regions to File
        print("Recording region data...")
        print("-"*40)
        record_regions(dimension=dimension, processed_region_files=processed_region_files)
        print("-"*40)
