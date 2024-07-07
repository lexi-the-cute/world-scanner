import os
import argparse
import world
import json

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
        "minecraft:the_end": "world/DIM1/region",
        # "minecraft:the_nether": "world/DIM-1/region",
        # "minecraft:overworld": "world/region",
    }

    hidden_blocks = ["minecraft:air"]

    # Mark Primary Regions as Safe
    for dimension in dimensions:
        # Get Region Folder Path
        region_folder_paths = dimensions[dimension]

        # Table of Region Files
        processed_region_files = {}

        region_files_paths: list[str] = world.get_region_files(region_folder_path=region_folder_paths)

        # Mark Primary Regions as Safe
        print("Scanning for primary regions...")
        print("-"*40)
        for region_file_path in region_files_paths:
            mark_safe: bool = False
            for block_x, block_y, block_z, block, block_entity in world.get_block_entities(region_file_path=region_file_path, hidden_blocks=hidden_blocks):
                # print("Block Entity: %s - %s" % (block_entity["id"], type(block_entity["id"])))
                if str(block_entity["id"]) == "waystones:sharestone":
                    # print("‣ Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))
                    print("‣ Region: %s - Block: (%i, %i, %i): %s" % (region_file_path, block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id)))
                    mark_safe = True
                    break

                if str(block_entity["id"]) == "waystones:waystone":
                    if str(block.properties["origin"]) == "player":
                        # print("‣ Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))
                        print("‣ Region: %s - Block: (%i, %i, %i): %s" % (region_file_path, block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id)))
                        mark_safe = True
                        break

            region_x, region_z = get_region_file_coordinates(path=region_file_path)
            processed_region_files["(%i, %i)" % (region_x, region_z)] = {
                "path": region_file_path,
                "x": int(region_x),
                "z": int(region_z),
                "safe": mark_safe,
                "reason": "primary" if mark_safe else "secondary",
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
            for x in range(-1, 1):
                for z in range(-1, 1):
                    key = "(%i, %i)" % (int(processed_region["x"])+x, int(processed_region["z"])+z)

                    # Neighboring Region Files are Not Guaranteed to Exist
                    if key not in temp_region_list:
                        continue

                    # Don't Edit Primary Regions
                    if temp_region_list[key]["reason"] == "primary":
                        continue

                    if x != 0 and z != 0:
                        temp_region_list[key]["safe"] = True
        processed_region_files = temp_region_list
        print("-"*40)
        print()

        # Record Regions to File
        print("Recording region data...")
        print("-"*40)
        record_regions(dimension=dimension, processed_region_files=processed_region_files)
        print("-"*40)
