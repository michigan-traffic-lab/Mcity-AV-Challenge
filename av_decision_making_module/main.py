import csv
import math
import numpy as np
import time

from mrav.mcity_mr_av import (
    MRAVTemplateMcity,
)  # This Python class is a basic component for any developed AV decision-making module and the user should inherit from it.


class AVDecisionMakingModule(MRAVTemplateMcity):
    """This is an example AV decision making module that reads a logged trajectory from a file and follows it."""

    def initialize_av_algorithm(self):
        """This function will be used to initialize the developed AV ddecision-making module. In this example, we read the predefined trajectory from a file."""
        trajectory = []
        with open("/baseline_av_data/baseline_av_trajectory.csv", "r") as f:
            reader = csv.reader(f)
            trajectory = []
            for row in reader:
                orientation = float(row[3])
                if orientation > math.pi:
                    orientation -= 2 * math.pi
                trajectory.append(
                    {
                        "x": float(row[1]),
                        "y": float(row[2]),
                        "orientation": orientation,
                        "velocity": float(row[4]),
                    }
                )
        self.trajectory = {
            "x_vector": np.array([point["x"] for point in trajectory]),
            "y_vector": np.array([point["y"] for point in trajectory]),
            "orientation_vector": np.array(
                [point["orientation"] for point in trajectory]
            ),
            "velocity_vector": np.array([point["velocity"] for point in trajectory]),
        }
        self.trajectory_index = 0

    def derive_planning_result(self, step_info):
        """This function will be used to compute the planning results based on the observation from "step_info". In this example, we find the closest point in the predefined trajectory and return the next waypoint as the planning results."""
        # parse the step_info
        av_state = step_info["av_info"]
        tls_info = step_info["tls_info"]
        av_context_info = step_info["av_context_info"]
        # find the closest point in the predefined trajectory
        current_x = av_state["x"]
        current_y = av_state["y"]
        if self.trajectory_index > len(self.trajectory["x_vector"]) - 1:
            next_x = self.trajectory["x_vector"][-1]
            next_y = self.trajectory["y_vector"][-1]
        else:
            next_x = self.trajectory["x_vector"][self.trajectory_index]
            next_y = self.trajectory["y_vector"][self.trajectory_index]

        print("current AV position:", current_x, current_y)
        print("next AV position:", next_x, next_y)
        planning_result = {
            "timestamp": time.time(),
            "time_resolution": 0.1,
            "next_x": self.trajectory["x_vector"][self.trajectory_index],
            "next_y": self.trajectory["y_vector"][self.trajectory_index],
            "next_speed": self.trajectory["velocity_vector"][self.trajectory_index],
            "next_orientation": self.trajectory["orientation_vector"][
                self.trajectory_index
            ],
        }
        self.trajectory_index += 1
        return planning_result


# Create an instance of the AV decision-making module and run it
av_decision_making_module = AVDecisionMakingModule()
av_decision_making_module.run()
