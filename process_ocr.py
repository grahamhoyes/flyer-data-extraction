from enum import Enum
from PIL import Image, ImageDraw
import io
import json

from google.cloud import storage, vision
from google.protobuf.json_format import MessageToDict


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARAGRAPH = 3
    WORD = 4
    SYMBOL = 5


COLORS = {
    FeatureType.PAGE: "yellow",
    FeatureType.BLOCK: "blue",
    FeatureType.PARAGRAPH: "red",
    FeatureType.WORD: "green",
    FeatureType.SYMBOL: "purple",
}


EPS = 20

COLORS_OF_WORDS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
}


def draw_boxes(image, bounds, color):
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon(
            [
                bound.vertices[0].x,
                bound.vertices[0].y,
                bound.vertices[1].x,
                bound.vertices[1].y,
                bound.vertices[2].x,
                bound.vertices[2].y,
                bound.vertices[3].x,
                bound.vertices[3].y,
            ],
            None,
            color,
        )
    return image


def get_document_text(uri):
    vision_client = vision.ImageAnnotatorClient()

    image = vision.types.Image()
    image.source.image_uri = uri

    response = vision_client.document_text_detection(image=image)
    document = response.full_text_annotation

    message = MessageToDict(response)

    bounds = {i: [] for i in FeatureType}

    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        bounds[FeatureType.SYMBOL].append(symbol.bounding_box)

                    bounds[FeatureType.WORD].append(word.bounding_box)

                bounds[FeatureType.PARAGRAPH].append(paragraph.bounding_box)

            bounds[FeatureType.BLOCK].append(block.bounding_box)

    return bounds, message


def _is_color_similar(a, b, eps=EPS):
    return all(abs(a[i] - b[i]) < eps for i in range(len(a)))


def get_main_color(image, box):
    """
    :param image: An image
    :param box: Bounding box vertices, not necessarily axis aligned
        [{'x': 1608, 'y': 243},
         {'x': 2853, 'y': 243},
         {'x': 2853, 'y': 356},
         {'x': 1608, 'y': 356}]
    :return: main color
    """

    left = min(v["x"] for v in box)
    top = min(v["y"] for v in box)
    right = max(v["x"] for v in box)
    bottom = max(v["y"] for v in box)

    cropped = image.copy().crop((left, top, right, bottom))

    colors = cropped.getcolors(cropped.size[0] * cropped.size[1])
    ordered = sorted(colors, key=lambda x: x[0], reverse=True)

    EPS = 16

    for _, col in ordered:
        if _is_color_similar(col, COLORS_OF_WORDS["white"], EPS):
            continue

        return col


def render_doc_text(uri, *levels):
    split_uri = uri[5:].split("/")
    bucket = split_uri[0]
    path = "/".join(split_uri[1:])

    filename = path.split("/")[-1].split(".")[0]
    filename = f"{filename}_{'_'.join(levels)}"

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.get_blob(path)

    buffer = io.BytesIO()
    blob.download_to_file(buffer)
    buffer.seek(0)

    image = Image.open(buffer)

    bounds, message = get_document_text(uri)

    for level in levels:
        if hasattr(FeatureType, level):
            param = getattr(FeatureType, level)
            draw_boxes(image, bounds[param], COLORS[param])

    for page in message["fullTextAnnotation"]["pages"]:
        for block in page["blocks"]:
            for paragraphs in block["paragraphs"]:
                for i in range(len(paragraphs["words"])):
                    main_color = get_main_color(
                        image, paragraphs["words"][i]["boundingBox"]["vertices"]
                    )
                    paragraphs["words"][i]["color"] = main_color

    image.save(f"files/annotated/{filename}.jpg")

    with open(f"files/ocr/{filename}.json", "w+") as fd:
        json.dump(message, fd)

    return image
