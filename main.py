import os
import anvil
import argparse

from typing import Union, List

def get_dimension_folders(dimension_folder_root: str) -> list[str]:
    if not os.path.exists(dimension_folder_root):
        return []

    dimensions: list[str] = []
    for namespace in os.listdir(dimension_folder_root):
        namespace_path: str = os.path.join(dimension_folder_root, namespace)
        for path in os.listdir(namespace_path):
            dimensions.append(os.path.join(namespace_path, path))

    return dimensions

def get_region_folder(world_folder: str) -> str:
    return os.path.join(world_folder, "region")

# this is an ease of use function
def get_region_folders(world_folder_root: str, dimension_folder_root: str) -> list[str]:
    region_paths: list[str] = []

    # main world folder
    world_region_path: str = get_region_folder(world_folder_root)
    region_paths.append(world_region_path)

    # dimension folder paths
    dimensions: list[str] = get_dimension_folders(dimension_folder_root)
    for dimension_path in dimensions:
        region_paths.append(get_region_folder(dimension_path))

    return region_paths

def get_region_files(region_folder_path: str) -> list[str]:
    if not os.path.exists(region_folder_path):
        return []

    region_files_paths: list[str] = []
    for files in os.listdir(region_folder_path):
        region_files_paths.append(os.path.join(region_folder_path, files))

    return region_files_paths

def get_blocks_in_chunk(chunk: anvil.Chunk):
    # Read Palette Test
    # for section_y in range(chunk.lowest_y, chunk.highest_y):
    #     print("Palette %i: %s" % (section_y, chunk.get_palette(section_y)))

    for block_y in range(chunk.lowest_y*16, (chunk.highest_y*16)+15):
        for block_z in range(16):
            for block_x in range(16):
                yield chunk.get_block(block_x, block_y, block_z), block_x, block_y, block_z

def get_blocks(region_file_path: str, hidden_blocks: List[str] = []):
    print("Reading Region file: %s" % region_file_path)
    print("-"*40)

    try:
        region = anvil.Region.from_file(region_file_path)

        split_filename: List[str] = region_file_path.split("/")[-1].split(".")
        region_x: int = int(split_filename[1])
        region_z: int = int(split_filename[2])
        # print("Region: (%s, %s)" % (region_x, region_z))
    except anvil.errors.EmptyRegionFile as e:
        return

    for chunk_x in range(32):
        for chunk_z in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                for block, block_x, block_y, block_z in get_blocks_in_chunk(chunk):
                    if ("%s:%s" % (block.namespace, block.id)) not in hidden_blocks:
                        region_chunk_x: int = (32*region_x)+chunk_x
                        region_chunk_z: int = (32*region_z)+chunk_z

                        global_block_x: int = (16*region_chunk_x)+block_x
                        global_block_z: int = (16*region_chunk_z)+block_z

                        block_entity = chunk.get_block_entity(global_block_x, block_y, global_block_z)

                        yield global_block_x, block_y, global_block_z, block, block_entity
            except anvil.errors.ChunkNotFound as e:
                pass
            except anvil.errors.OutOfBoundsCoordinates as e:
                print("OutOfBoundsCoordinates: %s" % e)
            # except Exception as e:
            #     pass
            #     print("Exception: %s" % e)
    
    # print("")
    print("-"*40)

def get_block_entities(region_file_path: str, hidden_blocks: List[str] = []):
    print("Reading Region file: %s" % region_file_path)
    print("-"*40)

    try:
        region = anvil.Region.from_file(region_file_path)
    except anvil.errors.EmptyRegionFile as e:
        return

    for chunk_x in range(32):
        for chunk_z in range(32):
            try:
                chunk = anvil.Chunk.from_region(region, chunk_x, chunk_z)
                for block_entity in chunk.block_entities:
                    block_x: int = block_entity["x"].value
                    block_y: int = block_entity["y"].value
                    block_z: int = block_entity["z"].value
                    block: anvil.Block = chunk.get_block(x=(block_x % 16), y=block_y, z=(block_z % 16))

                    if ("%s:%s" % (block.namespace, block.id)) not in hidden_blocks:
                        yield block_x, block_y, block_z, block, block_entity
            except anvil.errors.ChunkNotFound as e:
                pass
            except anvil.errors.OutOfBoundsCoordinates as e:
                print("OutOfBoundsCoordinates: %s" % e)
            # except Exception as e:
            #     pass
            #     print("Exception: %s" % e)
    
    # print("")
    print("-"*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='World Scanner', description='Scans Minecraft worlds saved in the anvil format', epilog='Uses fork of anvil-parser at https://github.com/lexi-the-cute/anvil-parser')
    parser.add_argument('-wrf', '--world-root-folder', dest='world_folder_root', default='world')
    parser.add_argument('--hide-blocks', dest='hidden_blocks', default=["minecraft:air"])

    args = parser.parse_args()

    dimension_folder_root = os.path.join(args.world_folder_root, "dimensions")
    region_folders_paths: list[str] = get_region_folders(world_folder_root=args.world_folder_root, dimension_folder_root=dimension_folder_root)
    hidden_blocks = args.hidden_blocks

    # Get Blocks From a Specific Region File
    # for block_x, block_y, block_z, block, block_entity in get_blocks(region_file_path="world/region/r.0.0.mca", hidden_blocks=args.hidden_blocks):
    #     print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))

    # Get Blocks From All Region Files
    # for region_folder_paths in region_folders_paths:
    #     region_files_paths: list[str] = get_region_files(region_folder_path=region_folder_paths)

    #     for region_files_path in region_files_paths:
    #         for block_x, block_y, block_z, block, block_entity in get_blocks(region_file_path=region_files_path, hidden_blocks=args.hidden_blocks):
    #             print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))

    # Get Block Entities From a Specific Region File
    # for block_x, block_y, block_z, block, block_entity in get_block_entities(region_file_path="world/region/r.0.0.mca", hidden_blocks=args.hidden_blocks):
    #     print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))

    # Get Block Entities From All Region Files
    for region_folder_paths in region_folders_paths:
        region_files_paths: list[str] = get_region_files(region_folder_path=region_folder_paths)

        for region_files_path in region_files_paths:
            for block_x, block_y, block_z, block, block_entity in get_block_entities(region_file_path=region_files_path, hidden_blocks=args.hidden_blocks):
                print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))