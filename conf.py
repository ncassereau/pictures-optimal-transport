use_slurm = True # whether or not slurm is used for the computation
cleanup_after = False # whether or not to delete plans and scatter plots after the gif is formed

slurm_kwargs = dict(
    job_name="pictures-transportation",
    output="slurm.out",
    error="slurm.err",
    account="xyz@cpu",
    time="02:00:00",
    qos="qos_cpu-dev",
)
module_to_load = "pytorch-gpu/py3/1.10.0"
ntasks = 40
scatter_nodes = 1
scatter_cpus_per_task = 1

picture_list = [
    "picture1.png",
    "picture2.png",
]

n_points = 40000 # Number of points drawn randomly on each picture
size = (295, 470) # Resizing the image before using it. Set None to ignore
display_size = (3.2, 4.8) # Size of the matplotlib figure for scatter plot
points_size = 2000. / n_points # size of points on the scatter plot
numItermax = 1_000_000_000 # Max iteration for plan computation
numThreads = 24 # EMD distribution

# In seconds, duration is the time to go from one picture to the next one.
# The total duration of the GIF is the (number of images + 1) * duration.
duration = 2
fps = 60
n_frames = duration * fps # number of frames for one transformation

# Easing functions allow to modulate the speed of the transition from one
# state to another. No easing functions (None value) means a linear translation.
# Examples of easing functions:
# https://github.com/semitable/easing-functions
# https://easings.net
# easing_function should either be a callable or None
def easeInOutCubic(x):
    import numpy as np
    return np.where(
        x < 0.5,
        4 * (x ** 3),
        1 - pow(-2 * x + 2, 3) / 2
    )

easing_function = easeInOutCubic # None

# A pause between two transitions to admire the picture before moving on
# to the next transformation.
duration_pause = 0.5 # in seconds
n_frames_pause = duration_pause * fps # number of frames to pause between two transports

filename = "mygif" # name of the file where the final gif will be stored. Do not include the extension
temporary_folder_name = "pic" # name of the folder where scatter plots will be saved
