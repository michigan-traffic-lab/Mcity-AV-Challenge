import glob
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

import SumoTrajVis


def check_broken_fcd_xml(traj_file_path):
    broken_flag = False
    with open(traj_file_path, "r") as fcd_file:
        new = []
        for line in fcd_file:
            new.append(line)
        if "</fcd-export>" not in new[-1]:
            broken_flag = True
    return broken_flag


def make_video(net_file_path, traj_file_path, output_folder):
    # Load net file and trajectory file
    net = SumoTrajVis.Net(net_file_path)
    trajectories = SumoTrajVis.Trajectories(traj_file_path)

    cav_exist_flag = False
    cav_start_time_index = 0

    # Set trajectory color for different vehicles
    for trajectory in trajectories:
        if trajectory.id == "CAV":
            trajectory.assign_colors_constant("#ff0000")
            cav_exist_flag = True
            cav_start_time_index = int(trajectory.time[0] * 10)
        else:
            trajectory.assign_colors_constant("#00FF00")
    if cav_exist_flag == False:
        print(f"No CAV trajectory in {traj_file_path}")
        return
    # Show the generated trajectory video
    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="box")  # same scale
    artist_collection = net.plot(ax=ax)
    plot_time_interaval = trajectories.timestep_range()[
        cav_start_time_index:
    ]  # only plot the last minute before the end of the trajectories, can be modified later
    a = animation.FuncAnimation(
        fig,
        trajectories.plot_points,
        frames=plot_time_interaval,
        interval=1,
        fargs=(ax, True, artist_collection.lanes),
        blit=False,
    )
    test_index = traj_file_path.split("/")[-2]
    output_path = os.path.join(output_folder, f"{test_index}.mp4")
    a.save(output_path, writer=animation.FFMpegWriter(fps=10), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    net_file = "/app/av_decision_making_module/initial_information/mcity.net.xml"
    output_folder = "/app/output/trajectory_videos"
    data_folder = "/app/output/trajectory_data"

    traj_files = sorted(
        glob.glob(
            os.path.join(data_folder, "mcity_av_challenge_results/raw_data/**/fcd.xml")
        )
    )
    if traj_files == []:
        print("No trajectory files found")
        exit()
    os.makedirs(output_folder, exist_ok=True)
    for f in tqdm(traj_files):
        if check_broken_fcd_xml(f):
            print(f"Trajectory file {f} is broken")
            continue
        make_video(net_file, f, output_folder)
    print("Done")
