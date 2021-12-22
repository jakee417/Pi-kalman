from gps_tracker import GPSTracker
import pytest
import numpy as np

N = 50
DIM = 2

@pytest.mark.parametrize('dim', [2])
def test_example_from_paper(dim):
    from matplotlib import pyplot as plt
    tracker = GPSTracker(obs_dim=dim, dt=0.1)

    X = np.array(
        [[0.],   # x_coord
         [0.],   # y_coord
         [0.1],  # x_velocity
         [0.1]]  # y_velocity
    )
    P = np.diag([0.01] * tracker.latent_dimension)
    Y = X[:dim, :] + abs(np.random.rand(dim, 1))
    for i in range(0, N):
        X, P = tracker.prediction_step(X, P)
        X, P, _ = tracker.measurement_step(X, P, Y)
        Y = X[:dim, :] + 5. * abs(np.random.rand(dim, 1))
        plt.scatter(*X[:dim], c='b')
        plt.scatter(*Y, c='r')
    plt.show()
    