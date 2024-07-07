import os
import argparse
import world

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='World Scanner', description='Scans Minecraft worlds saved in the anvil format', epilog='Uses fork of anvil-parser at https://github.com/lexi-the-cute/anvil-parser')
    parser.add_argument('-wrf', '--world-root-folder', dest='world_folder_root', default='world')
    parser.add_argument('--hide-blocks', dest='hidden_blocks', default=["minecraft:air"])

    args = parser.parse_args()

    dimension_folder_root = os.path.join(args.world_folder_root, "dimensions")
    region_folders_paths: list[str] = world.get_region_folders(world_folder_root=args.world_folder_root, dimension_folder_root=dimension_folder_root)
    hidden_blocks = args.hidden_blocks

    # Get Blocks From a Specific Region File
    # for block_x, block_y, block_z, block, block_entity in world.get_blocks(region_file_path="world/region/r.0.0.mca", hidden_blocks=args.hidden_blocks):
    #     print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))

    # Get Blocks From All Region Files
    # for region_folder_paths in region_folders_paths:
    #     region_files_paths: list[str] = world.get_region_files(region_folder_path=region_folder_paths)

    #     for region_files_path in region_files_paths:
    #         print("Reading Region file: %s" % region_file_path)
    #         print("-"*40)
    #         for block_x, block_y, block_z, block, block_entity in world.get_blocks(region_file_path=region_files_path, hidden_blocks=args.hidden_blocks):
    #             print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))
    #         print("-"*40)

    # Get Block Entities From a Specific Region File
    # TODO: (Test Fix) Main Coordinates: (3, 84, 40) - Chunk Block Debug: (3, 4, 8)
    # TODO: (Test Fix) Block: (3, 84, 40): minecraft:air - BlockEntity: {TAG_Int('z'): 40, TAG_Int('x'): 3, TAG_String('id'): minecraft:chest, TAG_Int('y'): 84, TAG_List('Items'): [1 TAG_Compound(s)], TAG_Byte('keepPacked'): 0} - Properties: {}
    # for block_x, block_y, block_z, block, block_entity in world.get_block_entities(region_file_path="world/region/r.3.3.mca", hidden_blocks=args.hidden_blocks):
    #     print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))

    # Get Block Entities From All Region Files
    for region_folder_paths in region_folders_paths:
        region_files_paths: list[str] = world.get_region_files(region_folder_path=region_folder_paths)

        for region_files_path in region_files_paths:
            print("Reading Region file: %s" % region_file_path)
            print("-"*40)
            for block_x, block_y, block_z, block, block_entity in world.get_block_entities(region_file_path=region_files_path, hidden_blocks=args.hidden_blocks):
                print("Block: (%i, %i, %i): %s - BlockEntity: %s - Properties: %s" % (block_x, block_y, block_z, "%s:%s" % (block.namespace, block.id), block_entity, block.properties))
            print("-"*40)