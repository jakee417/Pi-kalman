from gps_tracker import GPSTracker
import numpy as np
import os
import argparse

KALMAN_PATH = '/home/pi/Documents/Pi-kalman/'
ROUTE_PATH = os.path.join(KALMAN_PATH, 'tracker', 'route.csv')

if __name__ == "__main__":
    # Take inputs from users to instantiate the kalman filter
    parser = argparse.ArgumentParser(description='Run GPS Tracking.')
    parser.add_argument(
        '--dimension', type=int, default=2,
        help='Dimensionality of dataset'
        )
    parser.add_argument(
        '--dt', type=float, default=1,
        help='Time difference between datapoints'
        )

    args = parser.parse_args()
    
    # Init the GPS tracker object based upon args
    tracker = GPSTracker(obs_dim=args.dimension, dt=args.dt)

    # Init state vector and covariance
    X = np.array(
        [[0.],   # x_coord
         [0.],   # y_coord
         [0.1],  # x_velocity
         [0.1]]  # y_velocity
    )
    P = np.diag([0.01] * tracker.latent_dimension)

    route = np.genfromtxt(ROUTE_PATH, delimiter=',')
    Y = route[:, 1:3]  # lat, lon hard coded to 2nd and 3rd columns
    X_seq = tracker.offline_update(X, P, Y)
    print(X_seq)