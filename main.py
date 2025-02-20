import xml.etree.ElementTree as ET
import json
import sys
from shutil import copytree as shutil_copytree
import re  # for string substitution

from settings import *


# -- Functions --
# Function to extract relevant data from DOMDocument.xml
def parse_starting_xml(root) -> dict:
    """
    Simple function to systematically move through DOMDocument.xml and extract relevant data
    Parameters
    ----------
    root : ET.Element
    The root of the DOMDocument
    """
    # Gather basic starting data
    anim_dimensions = (root.attrib["width"], root.attrib["height"])
    anim_frame_rate = root.attrib["frameRate"]

    if debug_mode and print_starting_parse_success:
        print(f"Animation frame rate: {anim_dimensions}")

    # Read through root/folders; first child
    # Store the names of relevant folders for later
    relevant_folders = []
    get_all_elements(relevant_folders, root[0], FOLDER_RELEVANT_ATTRIBUTES, FOLDER_ITEM_ID)

    if debug_mode and print_starting_parse_success:
        print(f"Relevant folders: {relevant_folders}")

        # Read through root/media; 2nd child
    # Store the name, path and data of each child
    media_items = []
    get_all_elements(media_items, root[1], MEDIA_RELEVANT_ATTRIBUTES, MEDIA_ITEM_ID)

    if debug_mode and print_starting_parse_success:
        print(f"Media items: {media_items}")

    # Read through root/symbols; 3rd child
    # Store relevant data
    symbol_items = []
    get_all_elements(symbol_items, root[2], SYMBOL_RELEVANT_ATTRIBUTES, SYMBOL_ITEM_ID)

    if debug_mode and print_starting_parse_success:
        print(f"Symbol items: {symbol_items}")

    # Read through fourth tag in root: timelines
    # Store relevant data
    timeline_items = []
    layer_section = root[3][0][0]  # root/timelines/DOMTimeline/layers
    animation_section = layer_section[0][0]  # layers/DOMLayer/frames

    get_all_elements(timeline_items, animation_section, TIMELINE_RELEVANT_ATTRIBUTES, TIMELINE_ITEM_ID)
    if debug_mode and print_starting_parse_success:
        print(f"Timeline items: {timeline_items}")

    starting_xml_parsed_data = {
        'anim_dimensions': anim_dimensions,
        'anim_frame_rate': anim_frame_rate,
        'relevant_folders': relevant_folders,
        'media_items': media_items,
        'symbol_items': symbol_items,
        'timeline_items': timeline_items
    }
    return starting_xml_parsed_data


# Used by parse_starting_xml
def get_all_elements(store_to, to_search, relevant_attributes, verification_id) -> None:
    """
    Gets all elements of a specific search location within DOMDocument.xml
    Parameters
    ----------
    store_to : list[dict]
        The list where the resulting elements are stored as dicts.
    to_search : ET.Element
        The root/starting point to search in.
    relevant_attributes : list[dict]
        The attributes of the element to be extracted. Must be a list of single key-value pair dicts.
    verification_id : str
        Used to make sure you're looking in the right location. Provide the name of the tag of the root.
    """
    for item in to_search:
        if item.tag == XML_PREFIX + verification_id:
            to_keep = {}
            # Extract relevant attributes
            for attr in relevant_attributes:
                attr_key = list(attr.keys())[0]
                attr_value = list(attr.values())[0]
                to_keep[attr_key] = item.get(attr_value)

            store_to.append(to_keep)
            if debug_mode and print_element_retrieval_success:
                print(f"SUCCESS GETTING ELEMENT IN: {to_search}; key = {item.get('name')}; vid = {verification_id}")
        else:
            if debug_mode and print_element_retrieval_success:
                print(f"ERROR GETTING ELEMENT IN: {to_search}; key = {item.get('name')}; vid = {verification_id}")


# Returns the name of the entity that has been inputted; used for file naming
def get_entity_name(root) -> str:
    name = root[1][0].attrib["name"]
    # Remove the numbers
    no_nums_name = re.sub(r'\d+', '', name)
    # Cut trailing chars: x from img and _ from split
    cut_extra_chars = no_nums_name[:len(no_nums_name) - 2]
    # Cut first 6 chars: "media/"
    entity_name = cut_extra_chars[6:]

    return entity_name


# Simple function to verify the existence of a dir, else create it
def verify_dir_exists(directory) -> None:
    try:
        os.mkdir(directory)
        print(f"Created new directory: {directory}")
    except FileExistsError:
        if debug_mode and show_file_handling_output:
            print(f"DEBUG: {directory} folder already exists")


# Func to delete contents of a directory
def delete_dir_contents(directory_path):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                # Recursive but only 1 layer deep
                delete_dir_contents(file_path)
        if debug_mode and show_file_handling_output:
            print("DEBUG: All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

# Open DOMDocument.xml
tree = ET.parse(os.path.join(INPUT_DIR, XML_PATH))
root = tree.getroot()

file_name = get_entity_name(root) + ".json"

# Parse DOMDocument.xml and save relevant data
parsed_starting_xml = parse_starting_xml(root)

if debug_mode and print_parsed_starting_xml:
    print(f"DEBUG: Parsed starting xml = {parsed_starting_xml}")

# Add formatted path data to relevant folders
for folder in parsed_starting_xml["relevant_folders"]:
    path = os.path.join(INPUT_DIR, LIB_PATH, folder["name"])
    folder["path"] = path

# Image Xml loading handling
loaded_image_xml_files = []
# Stores all the data needed to make a texture out of images
sprite_textures_data = {}
# Stores the raw image and transformation data
raw_images_data = {}
# Stores the sprite transformation data for animation
sprite_animation_data = {}

for image_xml in parsed_starting_xml["symbol_items"]:
    # Sort between image and sprite references
    href_name = image_xml["href"]

    # Load current file data
    xml_tree = ET.parse(os.path.join(INPUT_DIR, LIB_PATH, image_xml["href"]))
    xml_root = xml_tree.getroot()

    # Image include handling
    if href_name[:5] == "image":
        name = xml_root[0][0].attrib["name"]  # Search current xml file: timeline/DOMTimeline name=""
        layer_list = xml_root[0][0][0]  # timeline/DOMTimeline/layers
        frames_list = layer_list[0][0]  # layers/DOMLayer/frames

        if len(layer_list) == 1 and len(frames_list) == 1:  # This verifies it is formatted correctly
            bitmap_instance = frames_list[0][0][0]  # frames/DOMFrame/elements/DOMBitmapInstance
            image_path = bitmap_instance.get("libraryItemName")
            image_transform_matrix = bitmap_instance[0][0]
            a, b, c, d, tx, ty = (image_transform_matrix.get("a"), image_transform_matrix.get("b"),
                                  image_transform_matrix.get("c"), image_transform_matrix.get("d"),
                                  image_transform_matrix.get("tx"), image_transform_matrix.get("ty"))
            raw_images_data[name] = {
                'image_path': image_path,
                'transform_values': [a, b, c, d, tx, ty]
            }
        # Invalid format handling
        else:
            print(f"length of layer_list = {len(layer_list)} and frames_list = {len(frames_list)}")

    # Sprite data import
    elif href_name[:6] == "sprite":
        name = xml_root[0][0].attrib["name"]  # Search current xml file: timeline/DOMTimeline name=""
        layer_list = xml_root[0][0][0]  # timeline/DOMTimeline/layers
        layers_in_texture = []

        for layer in layer_list:
            layer_index = layer.attrib["name"]
            elements = layer[0][0][0]  # layers/DOMLayer/frames/elements
            # Check if elements tag has children
            if len(elements) != 0:
                # Get image texture name
                texture_name = elements[0].get("libraryItemName")
                # Get transformation matrix values
                matrix_values = elements[0][0][0]  # DOMSymbolInstance/matrix/Matrix
                a, b, c, d, tx, ty = (matrix_values.get("a"), matrix_values.get("b"), matrix_values.get("c"),
                                      matrix_values.get("d"), matrix_values.get("tx"), matrix_values.get("ty"))

                # If colour is applicable, get that too; else return 1, 1, 1, 1
                if len(elements[0]) == 2:
                    color_values = elements[0][1][0]  # DOMSymbolInstance/color/Color
                    r, g, b, a = (color_values.get("redMultiplier"), color_values.get("greenMultiplier"),
                                  color_values.get("blueMultiplier"), color_values.get("alphaMultiplier"))
                else:
                    r, g, b, a = "1.000000", "1.000000", "1.000000", "1.000000"

                transform_values = [a, b, c, d, tx, ty]
                color_transform_values = [r, g, b, a]

                if color_transform_values == ["1.000000", "1.000000", "1.000000", "1.000000"]:
                    color_transform_values = "default"

                layers_in_texture.append({
                    'texture_name': texture_name,
                    'transform_values': transform_values,
                    'color_values': color_transform_values
                })
        sprite_textures_data[name] = layers_in_texture

    # The big one: animation data, used to move sprites
    elif href_name[:5] == "label":
        name = xml_root[0][0].attrib["name"]  # timeline/DOMTimeline; name
        layers_root = xml_root[0][0][0]  # timeline/DOMTimeline/layers
        layer_count = int(xml_root[0][0][0][0].attrib["name"])  # timeline/DOMTimeline/layers/DOMLayer; name

        # Debug print the layer data
        if debug_mode and should_print_label_data:
            print(f"DEBUG: anim_name = {name}, element_count = {layer_count}")

        for layer_num in range(layer_count):
            # Sprite frame list storage
            sprite_frame_list = []

            # Make a new 'root' at the frames directory and save the length; i.e. amount of frames for each element
            frames_root = layers_root[layer_num][0]

            # Save the sprite element reference
            # path : frames/DOMFrame/elements/DOMSymbolInstance; name
            # Logic in case the first element tag is empty; never 2 in a row
            if len(frames_root[0][0]) > 0:
                referenced_sprite = frames_root[0][0][0].attrib["libraryItemName"]
            else:
                referenced_sprite = frames_root[1][0][0].attrib["libraryItemName"]

            # Get animation data per layer
            for frame in frames_root:
                # Handle empty section
                if len(frame[0]) == 0:
                    sprite = 0
                    transform_values = None
                    color_transform_values = None
                else:
                    sprite = 1
                    # Path: DOMFrame/elements/DOMSymbolInstance/x/x
                    frame_matrix = frame[0][0][0][0]
                    frame_color = frame[0][0][1][0]

                    a, b, c, d, tx, ty = (frame_matrix.get("a"), frame_matrix.get("b"), frame_matrix.get("c"),
                                          frame_matrix.get("d"), frame_matrix.get("tx"), frame_matrix.get("ty"))
                    transform_values = [a, b, c, d, tx, ty]

                    r, g, b, a = (frame_color.get("redMultiplier"), frame_color.get("greenMultiplier"),
                                  frame_color.get("blueMultiplier"), frame_color.get("alphaMultiplier"))
                    color_transform_values = [r, g, b, a]

                    if color_transform_values == ["1.000000", "1.000000", "1.000000", "1.000000"]:
                        color_transform_values = "default"

                frame_index = frame.get("index")
                frame_duration = frame.get("duration")

                sprite_frame_list.append({
                    'sprite': sprite,
                    'frame_index': frame_index,
                    'frame_duration': frame_duration,
                    'transform_values': transform_values,
                    'color_values': color_transform_values
                })

            # Initialize the dictionary structure if it doesn't exist
            if name not in sprite_animation_data:
                sprite_animation_data[name] = {}

            if layer_num not in sprite_animation_data[name]:
                sprite_animation_data[name][layer_num] = {}

            if referenced_sprite not in sprite_animation_data[name][layer_num]:
                sprite_animation_data[name][layer_num][referenced_sprite] = []

            # Save all animation layer data
            sprite_animation_data[name][layer_num][referenced_sprite] = sprite_frame_list

    # Handles main_sprite.xml; only here in case I need it in the future
    elif href_name == "main_sprite.xml":
        pass

    # Handles any other case, considers it an error
    else:
        print(f"Invalid path: {href_name}")

    loaded_image_xml_files.append(xml_root)

# Modify data dicts, remove irrelevant information
parsed_starting_xml.pop("relevant_folders")
parsed_starting_xml.pop("media_items")
parsed_starting_xml.pop("symbol_items")
parsed_starting_xml.pop("timeline_items")

converted_json = {
    'header_data': parsed_starting_xml,
    'raw_images_data': raw_images_data,
    'sprite_textures_data': sprite_textures_data,
    'sprite_animation_data': sprite_animation_data
}

# Make sure output dirs exist, else create them
verify_dir_exists(OUTPUT_DIR)
verify_dir_exists(OUTPUT_MEDIA_DIR)

# Delete contents of the output directory
delete_dir_contents(OUTPUT_DIR)

# Open new json in output dir
with open(os.path.join(OUTPUT_DIR, file_name), "w+") as output:
    json.dump(converted_json, output, indent=4 if debug_mode and add_indent_to_output_json else None)

# Copy images from media to output/media
shutil_copytree(INPUT_MEDIA_DIR, OUTPUT_MEDIA_DIR, dirs_exist_ok=True)

sys.exit()
