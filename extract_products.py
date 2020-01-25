from fuzzywuzzy import fuzz
import pandas as pd
import json

df_products = pd.read_csv("files/product_dictionary.csv")


def extract_products(ocr_path):
    """
    :param ocr_path: Path to an OCR JSON output file
    :return:
    """
    products = []

    with open(ocr_path, "r") as fd:
        data = json.load(fd)

    for page in data["fullTextAnnotation"]["pages"]:
        for block in page["blocks"]:
            if block["confidence"] < 0.9:
                continue

            text = ""
            best_match = ""
            max_score = 0
            for paragraph in block["paragraphs"]:
                for word in paragraph["words"]:
                    text += "".join(symbol["text"] for symbol in word["symbols"]) + " "

            for _, row in df_products.iterrows():
                score = fuzz.token_set_ratio(text, row["product_name"])
                if score > max_score:
                    max_score = score
                    best_match = row["product_name"]

            products.append(best_match)

    return products


if __name__ == "__main__":
    products = extract_products("files/ocr/week_10_page_1_BLOCK_WORD.json")