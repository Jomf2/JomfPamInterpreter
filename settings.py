import os

# - Dev Settings -
debug_mode = 1
all_debug_settings_enabled = 0

# These settings require developer mode
print_element_retrieval_success = 1 if all_debug_settings_enabled else 0
print_starting_parse_success = 1 if all_debug_settings_enabled else 0
print_parsed_starting_xml = 1 if all_debug_settings_enabled else 0
add_indent_to_output_json = 1 if all_debug_settings_enabled else 0
should_print_label_data = 1 if all_debug_settings_enabled else 0
show_file_handling_output = 1 if all_debug_settings_enabled else 0

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

INPUT_DIR = "input"
OUTPUT_DIR = "output"

INPUT_MEDIA_DIR = os.path.join(INPUT_DIR, "library", "media")
OUTPUT_MEDIA_DIR = os.path.join(OUTPUT_DIR, "media")

XML_PATH = "DOMDocument.xml"
LIB_PATH = "library"

XML_PREFIX = "{http://ns.adobe.com/xfl/2008/}"

FOLDER_ITEM_ID = "DOMFolderItem"
MEDIA_ITEM_ID = "DOMBitmapItem"
SYMBOL_ITEM_ID = "Include"
TIMELINE_ITEM_ID = "DOMFrame"
LAYER_ITEM_ID = "DOMLayer"

FOLDER_RELEVANT_ATTRIBUTES = [
    {'name': "name"}]
MEDIA_RELEVANT_ATTRIBUTES = [{'name': "name"},
                             {'item_id': "itemID"},
                             {'href': "href"},
                             {'frame_right': "frameRight"},
                             {'frame_bottom': "frameBottom"}]
SYMBOL_RELEVANT_ATTRIBUTES = [{'href': "href"},
                              {'item_id': "itemID"}]
TIMELINE_RELEVANT_ATTRIBUTES = [{'animation_name': "name"},
                                {'animation_index': "index"},
                                {'animation_duration': "duration"}]


# -- Data Structure --
# header_data
# - anim_dimensions: the size of the animation frame to be scaled, zombies especially are usually bigger
# - anim_frame_rate: the speed of the animation - almost always 30fps
#
# raw_images_data
# - image name: the name of the image under images/x after transformation
# -- image_path: the path to the raw media image, should be a media/image
# -- transform_values: the transformation matrix to apply to the media image
#
# sprite_textures_data
# - sprite name: the name of the sprite under sprites/x after compiling
# -- texture_name: the name used to find the texture, should be an image/image
# -- transform_values: the transformation matrix to modify the texture by
# -- color_values: the values to multiply each color in the texture by; default means [1, 1, 1, 1]
#
# sprite_animation_data
# - anim name: the name of the specific animation for the entity, to be used as identifier
# -- layer num: the layer num in the animation, used for one sprite at a time
# --- sprite name: the name of the sprite referenced, should be sprite/image
# ---- sprite: bool, whether this index should draw the texture
# ---- frame_index: the placement in the timeline where the frame starts
# ---- frame_duration: the placement of the end of the frame in the timeline; end can be found with index+duration
# ---- transform_values: the transformation matrix to modify the image with; length of 6
# ---- color_values: the rgba color values to multiply the texture by; default means [1, 1, 1, 1]
#

