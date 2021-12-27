"""Pi-kalman"""

import numpy as np
from typing import Tuple


class LinearGaussianStateSpaceModel(object):
    """ Minimal implementation of a linear gaussian (LG) state space model (SSM)

    A (stationary) linear gaussian state space model is defined as:
    z' = A * z + B * U + 𝛆      (transition model)
    y' = C * z' + 𝛅             (observation model)
    𝛆 ~ 𝒩(0, Q)
    𝛅 ~ 𝒩(0, R)
    
    So that,
    ℙ(z'| z) ~ 𝒩(A * z + B * U, Q)
    ℙ(y' | z') ~ 𝒩(C * z', R)

    Where ℙ indicates the probability of an event, 𝒩 denotes the normal
    (gaussian) distribution, and the ' symbol indicates the next time step.
    i.e. z is at time t and z' is at time t + 1.

    The generative process for this model proceeds as follows; we start with a
    latent state z which describes the system at time t. From z, we can directly
    sample an observation y also at time t. To iterate the system, we transition
    from z to z' at time t + 1 allowing us to then sample y' at time t + 1.
    The equivalent probabilistic graphical model (PGM) is shown below:
    ```
    z_1     ->      z_2     ->      ...     ->      z_t        ->      z_T
    |               |               |               |                  |
    y_1             y_2             ...             y_t                y_T
    ```
    We can continue in this fashion to sample y_1, ..., y_T. Alternatively, if
    we observe y_1, ..., y_T as data, we can make inference about z_1, ..., z_T.

    References:
        https://arxiv.org/pdf/1204.0375.pdf
        https://probml.github.io/pml-book/

    Notes:
        ``Linear gaussian state space model`` is synonymous with a
        ``linear dynamical system``. An algorithm which performs estimation on
        an ``LG-SSM`` is known as the ``Kalman Filter Algorithm``.

    """

    def __init__(self,
                 A: np.ndarray,
                 B: np.ndarray,
                 C: np.ndarray,
                 U: np.ndarray,
                 Q: np.ndarray,
                 R: np.ndarray):
        """

        Args:
            A: nxn transition matrix
            B: input effect matrix
            C: observation matrix
            U: control input
            Q: transition noise covariance matrix
            R: observation noise covariance matrix
        """
        self.A = A
        self.C = C
        self.B = B
        self.U = U
        self.Q = Q
        self.R = R

    def prediction_step(self,
                        X: np.ndarray,
                        P: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """ Runs a prediction step in the kalman filter.

        To update the latent state z' and its mean X'|X and covariance P'|P from
        initial state z and a sequence of observations y_{1:t-1} we use the law
        of total probability and the definitions of the conditional
        distributions of z'| y_{1:t-1}, u, z and the prior distribution of
        z | X, P where X and P are the mean and covariance of z respectively.
        ```
        ℙ(z' | y_{1:t-1}, u) = ∫ ℙ(z' | y_{1:t-1}, u, z) * ℙ(z | X, P) * dz  (1)
        = ∫ ℙ(z' | u, z) * ℙ(z | X, P) dz                                    (2)
        = ∫ 𝒩(z'; A * z + B * U, Q) * 𝒩(z; X, P) dz                         (3)
        = 𝒩(z'; X'|X, P'|P)                                                 (4)
        X'|X = A * X + B * U
        P'|P = A * P * A^T + Q
        ```
        And we have used law of total probability in eqn (1), independence of z'
        y_{1:t-1} conditioned on z in eqn (2), conditional dist. assumptions in
        eqn (3) and the Normal-Normal conjugacy property in eqn (4).

        Args:
            X: mean state estimate of the previous step (t - 1).
            P: state covariance of previous step (t - 1).

        Returns:
            X'|X: predicted mean state estimate at time t without measurement
            P'|P: predicted state covariance at time t without measurement
        """
        X = np.dot(self.A, X) + np.dot(self.B, self.U)
        P = np.dot(self.A, np.dot(P, self.A.T)) + self.Q
        return X, P

    def measurement_step(self,
                         X: np.ndarray,
                         P: np.ndarray,
                         Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Tuple]:
        """ Runs a measurement update step in the kalman filter.

        Args:
            X'|X: predicted mean state estimate at time t without measurement
            P'|P: predicted state covariance at time t without measurement
            Y: observed value at time t

        Returns:
            X': predicted mean state estimate at time t with measurement
            P': predicted state covariance at time t with measurement
            Y_hat, S: params for posterior predictive distribution:
                ℙ(Y'| Y, U) ~ 𝒩(Y'; Y_hat, S)
                = 𝒩(C * X, C * P * C^T + R)
        """
        Y_hat = np.dot(self.C, X)
        S = np.dot(self.C, np.dot(P, self.C.T)) + self.R
        K = np.dot(P, np.dot(self.C.T, np.linalg.inv(S)))
        r = Y - Y_hat
        X = X + np.dot(K, r)
        P = P - np.dot(K, np.dot(self.C,  P))  # FIXME: References differ...
        # P = P - dot(K, dot(S, K.T))
        return X, P, (Y_hat, S)

    def posterior_predictive(self, Y_hat, S):
        # TODO: What will one step predictions show?
        return None

    def offline_update(
        self,
        X: np.ndarray,
        P: np.ndarray, 
        Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prediction and measurement steps for an offline Kalman filter.

        Notes: 
            Wraps the `online_update` function over the input `Y`.
        
        Args:
            X: mean state estimate of the previous step (t - 1).
            P: state covariance of previous step (t - 1).
            Y: observed value at time t
        
        Returns:
            X_sequence: predicted mean state estimate at times 1,...,T
        """
        n, _ = Y.shape
        X_list = []
        for i in range(n):
            Y_i = Y[i:i+1, :].T
            X, P, _ = self.online_update(X, P, Y_i)
            X_list.append(X)
        X_sequence = np.concatenate(X_list, axis=-1)
        return X_sequence
        

    def online_update(self, X: np.ndarray, P: np.ndarray, Y: np.ndarray):
        """Prediction and measurement step for an online Kalman filter step.
        
        Args:
            X: mean state estimate of the previous step (t - 1).
            P: state covariance of previous step (t - 1).
            Y: observed value at time t

        Returns:
            X': predicted mean state estimate at time t with measurement
            P': predicted state covariance at time t with measurement
            Y_hat, S: params for posterior predictive distribution
        """
        X, P = self.prediction_step(X, P)
        X, P, params = self.measurement_step(X, P, Y)
        Y_post = self.posterior_predictive(*params)
        return X, P, Y_post


class GPSTracker(LinearGaussianStateSpaceModel):
    """ GPS Tracker application as a Linear Gaussian State Space Model.

    Implements a Linear Gaussian State Space Model for n-dimensional tracking.
    Review on a LG-SSM is as follows:
    z' = A * z + B * U + 𝛆      (transition model)
    y' = C * z' + 𝛅             (observation model)
    𝛆 ~ 𝒩(0, Q)
    𝛅 ~ 𝒩(0, R)

    And,
    ℙ(z'| z) ~ 𝒩(A * z + B * U, Q)
    ℙ(y' | z') ~ 𝒩(C * z', R)

    Latent states (z) will represent both positions and velocities and
    the observations (y) only need positions. Specifically for 2-dimensions:
    ```
    z = [x_coord, y_coord, x_velocity, y_velocity]

    y = [x_coord, y_coord]

    A = [[1, 0, dt, 0],
         [0, 1, 0, dt],
         [0, 0, 1, 0],
         [0, 0, 0, 1]]

    C = [[1, 0, 0, 0],
         [0, 1, 0, 0]]

    Q = [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]]

    R = [[1, 0],
         [0, 1]]
    ```
    """

    def __init__(self,
                 obs_dim: int = 2,
                 dt: float = 0.1):

        # Double the latent dimension to include both speed and position
        latent_dim = 2 * obs_dim

        self.__observation_dimension = obs_dim
        self.__latent_dimension = latent_dim

        # last latent state plus a dead reckoning from the previous velocity
        A = np.eye(latent_dim) + np.diag([dt] * obs_dim, k=obs_dim)

        # no control inputs
        B = np.eye(latent_dim)
        U = np.zeros((latent_dim, 1))

        # Reduce the 2 * obs_dim, latent_dim to just obs_dim
        C = np.eye(latent_dim)[:obs_dim, :]

        # identity noise
        Q = np.eye(latent_dim)
        R = np.eye(obs_dim)
        super(GPSTracker, self).__init__(A=A, B=B, C=C, U=U, Q=Q, R=R)

    @property
    def latent_dimension(self):
        return self.__latent_dimension

    @property
    def observation_dimension(self):
        return self.__observation_dimension

    def print_latent_state(self, X: np.ndarray) -> None:
        print(f'coords: \n'
              f'{X[:self.observation_dimension]}')
        print(f'velocities: \n'
              f'{X[self.observation_dimension:]}')

    def __repr__(self):
        return """
        ---------------------
        State Equation:
        ---------------------
        z' = A * z + B * U + 𝒩(0, Q) \n
        A: \n {} \n
        B: \n {} \n
        U: \n {} \n
        Q: \n {} \n
        ---------------------
        Observation Equation:
        ---------------------
        y' = C * z' + 𝒩(0, R)
        C: \n {} \n
        R: \n {}
        """.format(self.A, self.B, self.U, self.Q, self.C, self.R).\
            replace(' ', '')
