import time

class PidController:
    #
    # Constructor
    #
    def __init__(self, kp, ki, kd, output_min, output_max, set_point):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.set_point = set_point
        self._integral = 0.0
        self._prev_value = 0.0
        self._prev_error = 0.0
        self._previous_time = time.time()

    #
    # Public Methods
    #
    def update(self, current_value) -> float:
        current_time = time.time()
        delta_t = current_time - self._previous_time

        # calculate error
        error = self.set_point - current_value

        # proportional term
        p_value = self.kp * error

        # integral term
        i_value = self._integral

        # derivative term
        # d_value = self.kd * (error - self._prev_error) / delta_t
        d_value = -self.kd * (current_value - self._prev_value) / delta_t # slightly better transient response

        # output signal
        v = p_value + i_value + d_value
        u = max(self.output_min, min(self.output_max, v))

        # self._integral += self.ki * (error + u - v) * delta_t
        self._integral += self.ki * error * delta_t
        self._integral = max(self.output_min, min(self.output_max, self._integral)) # might make it slower to converge

        self._prev_value = current_value
        self._prev_error = error
        self._previous_time = current_time

        return u
