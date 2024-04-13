import json
import numpy as np
import time
import scipy.integrate as spi
from mrav.mcity_mr_av import (
    MRAVTemplateMcity,
)  # This Python class is a basic component for any developed AV decision-making module and the user should inherit from it.
from terasim_com.utils.convertion import utm_to_sumo_coordinate


class AVDecisionMakingModule(MRAVTemplateMcity):
    """This is an example AV decision making module that reads a logged trajectory from a file and follows it."""

    def initialize_av_algorithm(self):
        """This function will be used to initialize the developed AV ddecision-making module. In this example, we read the predefined trajectory from a file."""
        trajectory = []
        with open("/baseline_av_data/baseline_av_trajectory.json", "r") as f:
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
        # IDM model parameters
        self.s0 = 2  # minimum distance between vehicles
        self.v0 = 50  # speed of vehicle in free traffic
        self.a = 0.73  # maximum acceleration
        self.b = 1.67  # comfortable deceleration
        self.T = 1.5  # safe time headway
        self.delta = 4  # acceleration exponent
        self.carlen = 4  # length of the vehicles
        self.a_max = 2  # maximum acceleration of AV
        self.d_max = 1  # maximum deceleration of AV
        self.conf_dist = 5  # conflict distance

    def derive_planning_result(self, step_info):
        t = np.linspace(0, 0.2, 2)
        next_state = self.fsys(step_info, t)

        # Increment the trajectory index sequentially
        self.trajectory_index += 1

        # Check for end of trajectory and handle accordingly
        if self.trajectory_index >= len(self.trajectory["x_vector"]):
            self.trajectory_index = 0  # Reset to start or handle as needed
            # Implement any necessary actions when trajectory ends, e.g., slowing down
            print("End of trajectory reached. Taking necessary actions.")

        # Extract the next state values from the trajectory
        next_x = self.trajectory["x_vector"][self.trajectory_index]
        next_y = self.trajectory["y_vector"][self.trajectory_index]
        next_velocity = self.trajectory["velocity_vector"][self.trajectory_index]
        next_orientation = self.trajectory["orientation_vector"][self.trajectory_index]

        print("next AV position: ", next_x, next_y, next_velocity)

        planning_result = {
            "timestamp": time.time(),
            "time_resolution": 0.1,
            "next_x": next_x,
            "next_y": next_y,
            "next_speed": next_velocity,
            "next_orientation": next_orientation,
        }

        return planning_result



    def fsys(self, step_info, t):
        # Extract AV information
        av_info = step_info['av_info']
        tls_info = step_info['tls_info']
        av_context_info = step_info['av_context_info']

        # Initialize simulation runs based on AV info
        x_follow = av_info['x']
        v_follow = av_info['speed_long']
        v_init = np.array([x_follow, x_follow + 100, v_follow])  # Assume no leading vehicle initially

        # Check if there is a leading vehicle
        for vehicle_id, info in av_context_info.items():
            if info['leading_info']['is_leading_cav']:
                x_lead = info['x']
                v_lead_init = info['speed_long']
                v_init = np.array([x_follow, x_lead, v_follow])  # Update with leading vehicle info
                break

        # Check traffic light status and adjust acceleration accordingly
        next_tls_state = tls_info['next_tls_state']
        distance_to_next_tls = tls_info['distance_to_next_tls']
        if next_tls_state in ['R', 'r', 'Y', 'y'] and distance_to_next_tls < self.conf_dist:
            acc_profile = np.full(t.shape, -self.d_max)  # Decelerate if traffic light is red or yellow and close
        else:
            acc_profile = np.full(t.shape, self.a)  # Accelerate otherwise

        # Simulate the ODE describing the IDM model for a very short time interval
        v = spi.odeint(self.f, v_init, t, args=(acc_profile,))

        return v[-1]  # Return only the last state (next immediate state)


    def f(self, v, t0, v_l_traj):
        # Differential equations for the IDM model
        idx = np.round(t0).astype('int')
        T = len(v_l_traj) - 1
        if idx > T:
            idx = T

        v_l = v_l_traj[idx]
        x_f_dot = v[2]
        x_l_dot = v_l
        v_f_dot = self.a * (1 - (v[2] / self.v0) ** self.delta - (self.s_star(v[2], (v[2] - v_l)) / (v[1] - v[0] - self.carlen)) ** 2)

        if v_f_dot > self.a_max:
            v_f_dot = self.a_max
        elif v_f_dot < -self.d_max:
            v_f_dot = -self.d_max

        return np.r_[x_f_dot, x_l_dot, v_f_dot]

    def s_star(self, v_f, v_f_del):
        return self.s0 + v_f * self.T + v_f * v_f_del / (2 * np.sqrt(self.a * self.b))



# Create an instance of the AV decision-making module and run it
av_decision_making_module = AVDecisionMakingModule()
av_decision_making_module.run()