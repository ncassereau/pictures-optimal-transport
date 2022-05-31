import imageio
import os
import shutil
import glob
import conf


def make_gif(filename, fps):
    n_files = len(glob.glob(f"{conf.temporary_folder_name}/*.png"))
    assert n_files == (conf.n_frames * len(conf.picture_list))

    with imageio.get_writer(f"{filename}.gif", mode="I", fps=fps) as writer:
        for i in range(n_files):
            print(f"Frame {i + 1} / {n_files}")
            frame_filename = f"{conf.temporary_folder_name}/{i}.png"
            image = imageio.imread(frame_filename)
            repeat_image = int(conf.n_frames_pause) if i % conf.n_frames == 0 else 1
            for _ in range(repeat_image):
                writer.append_data(image)


def cleanup():
    try:
        os.remove("data")
    except FileNotFoundError:
        pass
    shutil.rmtree("pic")


def main():
    print("Merging frames into a gif")
    make_gif(conf.filename, conf.fps)
    print("The merger is complete")
    if conf.cleanup_after:
        cleanup()


if __name__ == "__main__":
    main()
