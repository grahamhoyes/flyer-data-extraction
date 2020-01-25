import os

import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
from sklearn.metrics.pairwise import cosine_similarity

PRODUCTS_DATA_PATH = "files/emb_product_dictionary.pickle"


def embed(input_text):
    return model(input_text)


def compute_embedding(text):
    with tf.Session() as session:
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        message_embedding = session.run(embed([text]))
    return message_embedding


def find_closest_product(text):
    embedding = compute_embedding(text)
    df_products = pd.read_pickle(PRODUCTS_DATA_PATH)
    product_embeddings = np.stack(df_products['embedding'].values)

    similarity_matrix = cosine_similarity(embedding, product_embeddings)

    closest_product = df_products['product_name'].iloc[np.argmax(similarity_matrix)]

    return closest_product


if __name__ == '__main__':

    module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
    model = hub.load(module_url)
    print("module %s loaded" % module_url)

    product = find_closest_product("Organic Hummus Beans")

    print(product)