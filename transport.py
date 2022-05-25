import numpy as np
from PIL import Image
#import sys
#sys.path.append("../../pnria/pot/POT")
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

    return blackness / blackness.sum()


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


def im2dots(pil_image, n_points, size):
    # Convert a PIL image to a dotted picture

    # Resize, make the picture grey and make it an array
    if size is not None:
        pil_image = pil_image.resize(size)
    pil_image = pil_image.convert(mode="L")
    im = np.array(pil_image)

    # Transparent background is black after previous conversion
    # So make it white so that it has a zero probability to be selected
    im[im == 0.] = 255

    # Convert to a dotted picture
    probabilities = convert_to_black_probabilities(im)
    x, y = convert_pic_to_scatter_plot(probabilities, im.shape, n_points)

    return np.stack([x, y], axis=-1) # Link x and y coordinates in the same variable


def compute_plan(xs, xt, n):
    # Compute the plan between the source and the target
    a = np.ones((n,))
    b = np.ones((n,))
    M = ot.dist(xs, xt) # Cost to turn any source pixel into any target pixel
    print("Number of iterations: ", conf.numItermax)
    G = ot.emd(a, b, M, numThreads=conf.numThreads, numItermax=conf.numItermax)

    # The plan is, in this case, a permutation so it is a very sparse matrix.
    # A lot of memory can be saved by actually making it sparse.
    G = sparse.csr_matrix(G, dtype=np.uint8)

    print("Plan computed!")
    return G


def save_input_data(dotted_pictures, plans):
    with open("data", "wb") as file:
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
    image = Image.open(conf.picture_list[0])
    xs = im2dots(image, conf.n_points, conf.size)
    dotted_pictures.append(xs)

    for i in range(1, len(conf.picture_list)):
        image = Image.open(conf.picture_list[i])
        xt = im2dots(image, conf.n_points, conf.size)
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
