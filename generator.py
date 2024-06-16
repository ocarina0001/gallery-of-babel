import numpy as np
from PIL import Image
import os
import sys
import random
import brotli
import lzma
import gzip
import base64

sys.set_int_max_str_digits(0)

WIDTH = 128
HEIGHT = 128

def id_to_pixels(image_id, width, height):
    print("Converting id to pixels...")
    num_pixels = width * height
    max_value = 256
    pixels = []

    for _ in range(num_pixels):
        b = image_id % max_value
        image_id //= max_value
        g = image_id % max_value
        image_id //= max_value
        r = image_id % max_value
        image_id //= max_value
        pixels.append((r, g, b))
    
    return pixels

def create_image_from_id(image_id):
    print("Creating image from id...")
    pixels = id_to_pixels(image_id, WIDTH, HEIGHT)
    image_data = np.array(pixels, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
    image = Image.fromarray(image_data)
    os.makedirs('images', exist_ok=True)
    image.save(f'images/image.png')

def create_random_image():
    print("Creating random image...")
    pixels = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(WIDTH * HEIGHT)]
    pixels = id_to_pixels(pixels_to_id(pixels), WIDTH, HEIGHT)
    image_data = np.array(pixels, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
    image = Image.fromarray(image_data)
    os.makedirs('images', exist_ok=True)
    image.save(f'images/image.png')

def pixels_to_id(pixels):
    print("Converting pixels to id...")
    max_value = 256
    image_id = 0
    multiplier = 1
    for r, g, b in pixels:
        image_id += b * multiplier
        multiplier *= max_value
        image_id += g * multiplier
        multiplier *= max_value
        image_id += r * multiplier
        multiplier *= max_value
    with open("raw.txt", "w") as file:
        file.write(str(image_id))
    with open("id.txt", "w") as file:
        file.write(compress_text(str(image_id)))
    return image_id

def image_to_id(image_path):
    print("Converting image to id...")
    image = Image.open(image_path)
    image = image.resize((WIDTH, HEIGHT))
    image = image.convert("RGB")
    image_data = np.array(image)
    pixels = [tuple(pixel) for row in image_data for pixel in row]
    return pixels_to_id(pixels)

def compress_text(text):
    print("Compressing text...")
    brotli_compressed = brotli.compress(text.encode('utf-8'))
    gzip_compressed = gzip.compress(brotli_compressed)
    lzma_compressed = lzma.compress(gzip_compressed)
    encoded = base64.b64encode(lzma_compressed)
    return encoded.decode('utf-8')

def decompress_text(encoded_text):
    print("Decompressing text...")
    lzma_compressed = base64.b64decode(encoded_text.encode('utf-8'))
    gzip_compressed = lzma.decompress(lzma_compressed)
    brotli_compressed = gzip.decompress(gzip_compressed)
    text = brotli.decompress(brotli_compressed).decode('utf-8')
    return text

while True:
    choice = input("Type 'GEN' to generate an image, or 'FIND' to find the ID of an image: ")
    if choice.upper() == 'GEN':
        image_id = input("Type 'ID' to read from id.txt, type 'RAW' to read from raw.txt, or 'RAND' to get a random image: ")
        if image_id.upper() == "ID":
            with open("id.txt", 'r') as file:
                content = file.read()
                image_data = decompress_text(content)
            create_image_from_id(int(image_data))
        elif image_id.upper() == "RAW":
            with open("raw.txt", 'r') as file:
                content = file.read()
                create_image_from_id(int(content))
        elif image_id.upper() == "RAND":
            create_random_image()
        else:
            continue
        print("The image has been saved to images/image.png")
    elif choice.upper() == 'FIND':
        image_path = input("Please provide the path to the image: ")
        image_id = image_to_id(image_path)
        print(f"The ID of the image has been saved to 'id.txt' and 'raw.txt'")
