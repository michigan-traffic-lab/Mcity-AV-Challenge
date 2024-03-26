import json
import numpy as np
import time

from mrav.mcity_mr_av import MRAVTemplateMcity
from terasim_com.utils.convertion import utm_to_sumo_coordinate


class AVDecisionMakingModule(MRAVTemplateMcity):
    """This is an example AV decision making module that reads a logged trajectory from a file and follows it."""

    def initialize_av_algorithm(self):
        trajectory = []
        with open(
            "/app/av_decision_making_module/baseline_av_trajectory.json", "r"
        ) as f:
            for line in f:
                trajectory.append(json.loads(line)["CAV"])
        self.trajectory = {
            "x_vector": np.array(
                [
                    utm_to_sumo_coordinate([point["x"], point["y"]])[0]
                    for point in trajectory
                ]
            ),
            "y_vector": np.array(
                [
                    utm_to_sumo_coordinate([point["x"], point["y"]])[1]
                    for point in trajectory
                ]
            ),
            "orientation_vector": np.array(
                [point["orientation"] for point in trajectory]
            ),
            "velocity_vector": np.array([point["speed_long"] for point in trajectory]),
        }
        self.trajectory_index = 0

    def derive_planning_result(self, step_info):
        # parse the step_info
        av_state = step_info["av_info"]
        tls_info = step_info["tls_info"]
        av_context_info = step_info["av_context_info"]
        # find the closest point in the predefined trajectory
        current_x = av_state["x"]
        current_y = av_state["y"]
        x_vector = self.trajectory["x_vector"]
        y_vector = self.trajectory["y_vector"]
        distance = np.sqrt((x_vector - current_x) ** 2 + (y_vector - current_y) ** 2)
        closest_point_index = np.argmin(distance)
        self.trajectory_index = (
            closest_point_index
            if closest_point_index > self.trajectory_index
            else self.trajectory_index + 1
        )
        print("current AV position: ", current_x, current_y)
        print(
            "next AV position: ",
            x_vector[self.trajectory_index],
            y_vector[self.trajectory_index],
        )
        planning_result = {
            "timestamp": time.time(),
            "time_resolution": 0.1,
            "x_vector": self.trajectory["x_vector"][
                self.trajectory_index : self.trajectory_index + 20
            ].tolist(),
            "y_vector": self.trajectory["y_vector"][
                self.trajectory_index : self.trajectory_index + 20
            ].tolist(),
            "vd_vector": self.trajectory["velocity_vector"][
                self.trajectory_index : self.trajectory_index + 20
            ].tolist(),
            "ori_vector": self.trajectory["orientation_vector"][
                self.trajectory_index : self.trajectory_index + 20
            ].tolist(),
        }
        return planning_result


av_decision_making_module = AVDecisionMakingModule()
av_decision_making_module.run()
