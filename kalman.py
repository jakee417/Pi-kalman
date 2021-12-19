"""Pi-kalman"""

from numpy import dot, ndarray, sum, tile, linalg
from numpy.linalg import inv
from typing import Tuple


class KalmanFilter(object):
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
                 A: ndarray,
                 B: ndarray,
                 C: ndarray,
                 U: ndarray,
                 Q: ndarray,
                 R: ndarray):
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
                        X: ndarray,
                        P: ndarray) -> Tuple[ndarray, ndarray]:
        """ Runs a prediction step in the kalman filter.

        To update the latent state z' and its mean X'|X and covariance P'|P from
        initial state z and a sequence of observations y_{1:t-1} we use the law
        of total probability and the definitions of the conditional
        distributions of z'| y_{1:t-1}, u, z and the prior distribution of
        z | X, P where X and P are the mean and covariance of z respectively.
        ```
        ℙ(z' | y_{1:t-1}, u) = ∫ ℙ(z' | y_{1:t-1}, u, z) * ℙ(z | X, P) * dz  (1)
        = ∫ ℙ(z' | u, z) * ℙ(z | X, P) dz                                    (2)
        = ∫ 𝒩(z'; A * z + B * u, Q) * 𝒩(z; X, P) dz                         (3)
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
        X = dot(self.A, X) + dot(self.B, self.U)
        P = dot(self.A, dot(P, self.A.T)) + self.Q
        return X, P

    def measurement_step(self,
                         X: ndarray,
                         P: ndarray,
                         Y: ndarray) -> Tuple[ndarray, ndarray, Tuple]:
        """

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
        Y_hat = dot(self.C, X)
        S = dot(self.C, dot(P, self.C.T)) + self.R
        K = dot(P, dot(self.C.T, inv(S)))
        r = Y - Y_hat
        X = X + dot(K, r)
        P = P - dot(K, dot(self.C, P))  # FIXME: References differ...
        return X, P, (Y_hat, S)

    def posterior_predictive(self, Y_hat, S):
        # TODO: What will one step predictions show?
        return None

    def offline_update(self):
        pass

    def online_update(self, X, P, Y):
        """Prediction and measurement step for an online Kalman filter step."""
        X, P = self.prediction_step(X, P)
        X, P, params = self.measurement_step(X, P, Y)
        Y_post = self.posterior_predictive(*params)
        return X, P, Y_post
