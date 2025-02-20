A simple program to convert from PAM to json.

Data Structure:

header_data
- anim_dimensions: the size of the animation frame to be scaled, zombies especially are usually bigger
- anim_frame_rate: the speed of the animation - almost always 30fps

raw_images_data
- image name: the name of the image under images/x after transformation
- image_path: the path to the raw media image, should be a media/image
- transform_values: the transformation matrix to apply to the media image
  
sprite_textures_data
- sprite name: the name of the sprite under sprites/x after compiling
- texture_name: the name used to find the texture, should be an image/image
- transform_values: the transformation matrix to modify the texture by
- color_values: the values to multiply each color in the texture by; default means [1, 1, 1, 1]
  
sprite_animation_data
- anim name: the name of the specific animation for the entity, to be used as identifier
- layer num: the layer num in the animation, used for one sprite at a time
- sprite name: the name of the sprite referenced, should be sprite/image
- sprite: bool, whether this index should draw the texture
- frame_index: the placement in the timeline where the frame starts
- frame_duration: the placement of the end of the frame in the timeline; end can be found with index+duration
- transform_values: the transformation matrix to modify the image with; length of 6
- color_values: the rgba color values to multiply the texture by; default means [1, 1, 1, 1]
