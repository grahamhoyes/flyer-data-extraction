import os

import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub

DATA_PATH = "files/"
FILES_TO_ENCODE = ['product_dictionary.csv', 'units_dictionary.csv']


def compute_embeddings_for_the_dictionary(data_path, files_to_encode):

    module_url = "https://tfhub.dev/google/universal-sentence-encoder-large/5"
    model = hub.load(module_url)
    print("module %s loaded" % module_url)

    def embed(input_text):
        return model(input_text)

    for file_to_encode in files_to_encode:
        df = pd.read_csv(os.path.join(data_path, file_to_encode), header=0)

        with tf.Session() as session:
            session.run([tf.global_variables_initializer(), tf.tables_initializer()])

            message_embedding = session.run(embed(df[df.columns[0]].values))

            df['embedding'] = list(message_embedding)

        df.to_pickle(os.path.join(os.path.join(data_path, f'emb_{file_to_encode.split(".")[0]}.pickle')))


if __name__ == '__main__':
    compute_embeddings_for_the_dictionary(DATA_PATH, FILES_TO_ENCODE)
