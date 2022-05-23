import numpy as np
import os
import time
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle
import conf
import scipy.sparse as sparse


def load_data():
    with open("data", "rb") as file:
        D = pickle.load(file)
    pictures = D["images"]
    plans = [sparse.csr_matrix(d) for d in D["plans"]]

    assert (
        len(plans) == len(pictures) or
        (len(plans) == 1 and len(pictures) == 2)
    ), f"Found {len(plans)} plans and {len(pictures)} pictures"

    pictures.append(pictures[0]) # allows to complete the cycle

    # If only two pictures, then a single plan can do both trip by transposing it
    if len(plans) == 1:
        plans.append(plans[0].T)

    return pictures, plans


def mkdir(*args):
    path = os.path.join(*args)
    try:
        os.makedirs(path)
    except FileExistsError:
        # Delete any remaining picture in the folder
        search = os.path.join(path, "*.png")
        for filename in glob.glob(search):
            os.remove(filename)


def get_points_at_t(xs, xt, G, t):
    # Barycenter between xs and its corresponding xt
    # Linear translation: at xs for t=0 and at xt for t=1
    return (1 - t) * xs + t * G @ xt


def make_time_dimension(n_frames):
    t = np.linspace(0, 1, n_frames)
    return t


def display_scatter(source, show=True):
    x, y = source[..., 0], source[..., 1]
    plt.scatter(y, -x, s=conf.points_size, c='k', marker=".")
    size = conf.size or (y.max() - y.min(), x.max() - x.min())
    plt.xlim(0, size[0] + 1)
    plt.ylim(-size[1], 0)
    plt.axis('off')
    if show:
        plt.show()    


def make_pics(pictures, plans, n_frames, rank, ntasks):

    time_dim = make_time_dimension(n_frames)
    plt.figure(figsize=conf.display_size)

    def make_frame(image_index, time_index):
        t = time_dim[time_index]
        xs = pictures[image_index]
        xt = pictures[image_index + 1]
        G = plans[image_index]
        points = get_points_at_t(xs, xt, G, t)
        display_scatter(points, show=False)
        filename = f"pic/{image_index * n_frames + time_index}.png"
        plt.savefig(filename, transparent=False, bbox_inches='tight')
        plt.clf()

    for image_index in range(len(pictures) - 1):
        if rank == 0:
            i1 = image_index + 1
            i2 = image_index + 2
            if i2 > len(conf.picture_list): # because we're doing a cycle
                i2 -= len(conf.picture_list)
            print(f"Applying transport plan between images {i1} and {i2}")
        for time_index in range(n_frames):
            # Distribution on ntasks
            if (image_index * n_frames + time_index - rank) % ntasks == 0:
                make_frame(image_index, time_index)

    plt.close()
    plt.cla()
    plt.clf()

    
def main():
    pictures, plans = load_data()

    if conf.use_slurm:
        ntasks = int(os.environ["SLURM_NTASKS"])
        rank = int(os.environ['SLURM_PROCID'])
    else:
        ntasks = 1
        rank = 0

    if rank == 0:
        mkdir(conf.temporary_folder_name)
    else: 
        # Dirty but functional way to wait for the pic folder to be created / emptied
        # before we start making scatter plots.
        # A cleaner way would be to use MPI and synchronize them at this point but
        # that import seem unnecessary for just this small use-case.
        time.sleep(10)

    make_pics(pictures, plans, conf.n_frames, rank, ntasks)
    if rank == 0:
        print("Scatter plotted!")


if __name__ == "__main__":
    main()
