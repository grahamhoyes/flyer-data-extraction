import json
import numpy as np
import pandas as pd
from PIL import Image
from fuzzywuzzy import fuzz
import os
from multiprocessing.pool import Pool
import time

from ad_block import AdBlock
from price_string_matching import match_price_in_block


df_products = pd.read_csv("files/product_dictionary.csv")
images_path = "files/cleaned_images"
ocrs_path = "files/ocr"
save_path = "files/products"
images = os.listdir(images_path)


red = np.array([228, 23, 43])
black = np.array([37, 35, 36])
grey = np.array([79, 77, 78])

colors = {"red": red, "black": black, "grey": grey}

epsilons = {"red": 45, "black": 30, "grey": 18}

min_height = 38
max_height = 66


def color_percentage(word, color):
    return (np.abs(word - colors[color]) <= epsilons[color]).all(
        axis=2
    ).sum() / word.size


def get_main_color(image, box):
    """
    :param image: An image
    :param box: Bounding box vertices, not necessarily axis aligned
        [{'x': 1608, 'y': 243},
         {'x': 2853, 'y': 243},
         {'x': 2853, 'y': 356},
         {'x': 1608, 'y': 356}]
    :return: main color, percentage of color in word box
    """

    left = min(v["x"] for v in box)
    top = min(v["y"] for v in box)
    right = max(v["x"] for v in box)
    bottom = max(v["y"] for v in box)

    cropped = image.copy().crop((left, top, right, bottom))

    im = np.array(cropped)

    max_percent = 0
    word_color = ""
    for color in colors.keys():
        percent = color_percentage(im, color)
        if percent > max_percent:
            word_color = color
            max_percent = percent

    return word_color, max_percent


def check_color(image, word, color):
    word_color, percent = get_main_color(image, word["boundingBox"]["vertices"])
    return percent > 0.02 and word_color == color


def check_fontsize(box):
    min_y = np.inf
    max_y = 0

    for vertex in box["vertices"]:
        min_y = min(min_y, vertex["y"])
        max_y = max(max_y, vertex["y"])

    return max_y - min_y >= min_height and max_y - min_y <= max_height


def extract_products(ocr_path, image_path):
    """
    :param ocr_path: Path to an OCR JSON output file
    :param image_path: path to flyer image
    :return: product names
    """
    products = []
    paragraphs = []
    blocks = []
    with open(ocr_path, "r") as fd:
        data = json.load(fd)

    image = Image.open(image_path)

    for page in data["fullTextAnnotation"]["pages"]:
        for block in page["blocks"]:
            if block["confidence"] < 0.9:
                continue

            text = ""
            for paragraph in block["paragraphs"]:
                add_to_prod = False
                for word in paragraph["words"]:
                    word_text = "".join([symbol["text"] for symbol in word["symbols"]])

                    if check_fontsize(word["boundingBox"]):
                        if check_color(image, word, "black"):
                            text += word_text + " "
                            add_to_prod = True

                if add_to_prod:
                    products.append(text.strip())
                    paragraphs.append(paragraph)
                    blocks.append(block)

    return products, paragraphs, blocks


def remove_duplicates(products):
    matches = {}

    for product in products:
        category = product[1]
        if category not in matches.keys():
            matches[category] = [product]
        else:
            matches[category].append(product)

    final_products = []
    for category in matches.keys():
        largest_block_area = 0

        for product in matches[category]:
            block = product[-1]
            box = block["boundingBox"]["vertices"]

            left = min(v["x"] for v in box)
            top = min(v["y"] for v in box)
            right = max(v["x"] for v in box)
            bottom = max(v["y"] for v in box)

            area = np.abs(left - right) * np.abs(top - bottom)

            if area > largest_block_area:
                largest_block_area = area
                final_products.append(product)

    return final_products


def match_products(products, paragraphs, blocks):
    matched_products = []
    for i, product in enumerate(products):
        best_match = ""
        max_score = 0
        for _, row in df_products.iterrows():
            score = fuzz.token_set_ratio(product, row["product_name"])
            if score > max_score:
                max_score = score
                best_match = row["product_name"]

        if max_score > 90:
            matched_products.append([product, best_match, paragraphs[i], blocks[i]])

    return matched_products


def identify_products(images):
    labels = []
    start_time = time.time()

    data = []
    columns = [
        "flyer_name",
        "product_name",
        "unit_promo_price",
        "uom",
        "least_unit_for_promo",
        "save_per_unit",
        "discount",
        "organic",
    ]

    for count, flyer in enumerate(images):
        title = flyer[:-4]
        ocr_path = os.path.join(ocrs_path, title + "_WORD_BLOCK.json")
        image_path = os.path.join(images_path, flyer)

        products, paragraphs, blocks = extract_products(ocr_path, image_path)

        matched_products = match_products(products, paragraphs, blocks)

        final_products = remove_duplicates(matched_products)
        labels.append([[title, product[1]] for product in final_products])

        blocks = []
        for product in final_products:
            block = product[-1]
            block["product"] = product[1]
            block["productText"] = product[0]
            blocks.append(block)

        for i in range(len(blocks)):
            block_text = ""
            for paragraph in blocks[i]["paragraphs"]:
                for word in paragraph["words"]:
                    word_text = ""
                    for symbol in word["symbols"]:
                        word_text += symbol["text"]
                        if (
                            "property" in symbol
                            and "detectedBreak" in symbol["property"]
                        ):
                            word_text += " "

                    block_text += word_text

            blocks[i]["text"] = block_text

        for block in blocks:
            ad = AdBlock(title, block["product"])
            found_some_price_thing = match_price_in_block(block["text"], ad)
            ad.combine_information()
            data.append(ad.get_row())

        flyer_json = {}
        flyer_json["blocks"] = blocks

        with open(os.path.join(save_path, title + ".json"), "w") as f:
            json.dump(flyer_json, f)

    df = pd.DataFrame(data, columns=columns)
    df.to_csv("output.csv", index=False)


if __name__ == "__main__":
    # pool_images = [images[: min(i * 16, len(images))] for i in range(14)]
    # pool = Pool(processes=8, maxtasksperchild=1000)
    # i = 0
    # for _ in pool.imap_unordered(identify_products, pool_images, chunksize=16):
    #     i += 1
    #
    #     if i % 10 == 0:
    #         print(f"{i}/{len(images)}")
    #
    # pool.close()
    # pool.join()

    identify_products(["week_10_page_1.jpg"])
