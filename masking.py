from PIL import Image
import numpy as np
import os
import time


images_path = "files/flyer_images"
image_path = "files/flyer_images/week_1_page_1.jpg"
save_path = "test_images"

images = os.listdir(images_path)

image = Image.open(image_path)

im_array = np.array(image)

red_price = np.array([228, 23, 43])
black_desc = np.array([37, 35, 36])
grey_disc = np.array([79, 77, 78])

colours = [red_price, black_desc, grey_disc]


epsilons = [45, 30, 18]


def get_mask(image, colour, epsilon=10):
    return (np.abs(image - colour) >= epsilon).any(axis=2)


def get_global_mask(image):
    masks = []

    for colour, epsilon in zip(colours, epsilons):
        mask = get_mask(image, colour, epsilon)
        masks.append(mask)

    global_mask = masks[0]
    for mask in masks[1:]:
        global_mask = global_mask ^ mask

    return global_mask


def test_red(image, epsilon):
    red_mask = get_mask(image, red_price, epsilon=epsilon)
    image[red_mask] = np.array([255, 255, 255])

    Image.fromarray(image).save("test_red.jpg")


def test_black(image, epsilon):
    black_mask = get_mask(image, black_desc, epsilon=epsilon)
    image[black_mask] = np.array([255, 255, 255])

    Image.fromarray(image).save("test_black1.jpg")


def test_grey(image, epsilon):
    grey_mask = get_mask(image, grey_disc, epsilon=epsilon)
    image[grey_mask] = np.array([255, 255, 255])

    Image.fromarray(image).save("test_grey1.jpg")


def test_global(image):
    global_mask = get_global_mask(image)
    image[global_mask] = np.array([255, 255, 255])
    Image.fromarray(image).save("test.jpg")


def mask_image(image):
    global_mask = get_global_mask(image)
    image[global_mask] = np.array([255, 255, 255])
    return image


def main():
    # indices = np.random.choice(len(images), size=num_images, replace=False)

    start_time = time.time()
    for i in range(len(images)):
        image = Image.open(os.path.join(images_path, images[i]))
        im_array = np.array(image)
        im_array = mask_image(im_array)
        Image.fromarray(im_array).save(os.path.join(save_path, images[i]))

        if (i % 10) == 0:
            elapsed = time.time() - start_time
            print(
                "{} out of {} images completed, in {:.2f}s".format(
                    i + 1, len(images), elapsed
                )
            )
