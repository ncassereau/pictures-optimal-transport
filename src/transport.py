import numpy as np
from PIL import Image
import ot
import pickle
from scipy import sparse
import conf


def convert_to_black_probabilities(im):
    # Convert a grey array picture to a probability distribution to choose a pixel
    # A black pixel is more likely to be picked than a while pixel

    # Flatten it, a 1-D distribution is needed
    flattened_array = im.reshape(-1)

    # 0 is black, 255 is white ---> 0 is white, 255 is black
    blackness = 255 - flattened_array

    # Further increase contrast and improve points cloud image quality
    # by changing the probability distribution
    blackness = blackness ** 3.25

    # Normalization
    blackness = blackness / blackness.sum()

    return blackness


def convert_pic_to_scatter_plot(black_probabilities, initial_shape, n_points=10000):
    # Draw a given number of points from the provided probability distribution
    # in order to create a picture from dots.

    # Random draw of many pixels (by their respective index)
    points = np.random.choice(
        black_probabilities.shape[0],
        replace=True,
        size=(n_points, ),
        p=black_probabilities
    )

    # Fold in order to convert the pixels' index to ij-coordinates
    p1, p2 = np.unravel_index(points, initial_shape)

    # Fill the void between pixels by randomly moving them in their respective 1x1 square
    rand = np.random.random((2, n_points))
    p1 = p1.astype(np.float64) + rand[0]
    p2 = p2.astype(np.float64) + rand[1]

    return p1, p2


def change_contrast(img, level):
    # Change the contrast of a greyscale PIL image
    # Level 0 does not change anything.
    # Recommended to try between 50 and 150

    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


def picture_treatment(filename):
    # Treats a PIL picture so that it is usable for our little project

    # Open picture
    original_img = Image.open(filename).convert("RGBA")

    # Convert transparent background to white
    pil_image = Image.new("RGBA", original_img.size, "WHITE")
    pil_image.paste(original_img, (0, 0), original_img)

    # Convert to greyscale
    pil_image = pil_image.convert(mode="L")

    # Resize the picture
    if conf.size is not None:
        pil_image = pil_image.resize(conf.size)

    # Change contrast
    pil_image = change_contrast(pil_image, conf.contrast_level)

    return np.array(pil_image)


def im2dots(filename, n_points):
    # Make a points cloud from an image's filename

    # Load the picture and make it a greyscale array
    im = picture_treatment(filename)

    # Convert to a dotted picture
    probabilities = convert_to_black_probabilities(im)
    x, y = convert_pic_to_scatter_plot(probabilities, im.shape, n_points)

    return np.stack([x, y], axis=-1) # Link x and y coordinates in the same variable


def compute_plan(xs, xt, n):
    # Compute the plan between the source and the target
    a = np.ones((n,)) / n
    b = np.ones((n,)) / n
    M = ot.dist(xs, xt) # Cost to turn any source pixel into any target pixel
    print("Max number of iterations: ", conf.numItermax)

    G = ot.emd(a, b, M, numThreads=conf.numThreads, numItermax=conf.numItermax)

    # The plan is, in this case, a permutation so it is a very sparse matrix.
    # A lot of memory can be saved by actually making it sparse.
    G = sparse.csr_matrix(G) * n

    print("Plan computed!")
    print(G.__repr__())
    return G


def save_input_data(dotted_pictures, plans):
    with open(conf.transport_file, "wb") as file:
        print("Saving data...")
        pickle.dump({
            "images": dotted_pictures,
            "plans": [(g.data, g.indices, g.indptr) for g in plans]
        }, file)
    print("Data saved!")


def main():
    if len(conf.picture_list) < 2:
        raise ValueError("Multiple pictures must be provided")
    else:
        print(f"{len(conf.picture_list)} pictures were found")

    dotted_pictures = [] # Will store scatter plots in the order of the cycle
    plans = [] # Will store any transport plan between a picture and the next one in the cycle

    # First picture
    xs = im2dots(conf.picture_list[0], conf.n_points)
    dotted_pictures.append(xs)

    for i in range(1, len(conf.picture_list)):
        xt = im2dots(conf.picture_list[i], conf.n_points)
        dotted_pictures.append(xt)

        print(f"Computing plan {i}")
        G = compute_plan(xs, xt, conf.n_points)
        plans.append(G)
        xs = xt

    # If the cycle only has two pictures then the cycle can be completed by using the
    # already computed transport plan and transposing it.
    # Otherwise compute the plan between last picture and first picture
    # to complete the cycle.
    if len(conf.picture_list) != 2:
        print(f"Computing plan {len(conf.picture_list)}")
        G = compute_plan(xs, dotted_pictures[0], conf.n_points)
        plans.append(G)

    save_input_data(dotted_pictures, plans)


if __name__ == "__main__":
    main()
