
import json
import numpy as np
# from process_ocr import get_main_color
from PIL import Image

# df_products = pd.read_csv("files/product_dictionary.csv")

red = np.array([228, 23, 43])
black = np.array([37, 35, 36])
grey = np.array([79, 77, 78])

colors = {'red': red, 
            'black': black,
            'grey': grey}

epsilons = {'red': 45,
            'black': 30,
            'grey': 18}

min_height = 38
max_height = 66


def color_percentage(word, color):
    return (np.abs(word - colors[color]) <= epsilons[color]).all(axis=2).sum()/word.size
    
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
    word_color = ''
    for color in colors.keys():
        percent = color_percentage(im, color)
        if percent > max_percent:
            word_color = color
            max_percent = percent


    return word_color, max_percent


def check_color(image, word, color):
    word_color, percent = get_main_color(image, word['boundingBox']['vertices'])
    return percent > 0.02 and word_color == color


def check_fontsize(box):
    min_y = np.inf
    max_y = 0

    for vertex in box['vertices']:
        min_y = min(min_y, vertex['y'])
        max_y = max(max_y, vertex['y'])
    
    return max_y - min_y >= min_height and max_y - min_y <= max_height


def identify_products(ocr_path, image_path):
    """
    :param ocr_path: Path to an OCR JSON output file
    :param image_path: path to flyer image
    :return: product names
    """
    products = []

    with open(ocr_path, "r") as fd:
        data = json.load(fd)

    image = Image.open(image_path)


    for page in data["fullTextAnnotation"]["pages"]:
        for block in page["blocks"]:
            if block["confidence"] < 0.9:
                continue

            text = ""
            best_match = ""
            max_score = 0
            for paragraph in block["paragraphs"]:
                add_to_prod = False
                for word in paragraph["words"]:
                    word_text = "".join([symbol["text"] for symbol in word["symbols"]])

                    if check_fontsize(word['boundingBox']):
                        if check_color(image, word, 'black'):
                            text += "".join(word_text) + " "
                            add_to_prod = True
                
                if add_to_prod:
                    products.append(text)

    return products


if __name__ == "__main__":
    products = identify_products("files/ocr/week_10_page_1_BLOCK_WORD.json", 'test_images/week_10_page_1.jpg')
    [print(product) for product in products]