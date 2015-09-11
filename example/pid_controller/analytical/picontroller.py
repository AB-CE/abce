class PiController:
    """ The PiController, learns from an error to set a certain control.
        It only produces positive signals.

        Args:
            error_parameter:
                weight for error
            cumulative_error_parameter:
                weight for cumulative error
            positive:
                if true it truncates negative control signals to 0
    """
    def __init__(self, error_parameter, cumulative_error_parameter, positive=False):
        self.a = error_parameter
        self.b = cumulative_error_parameter
        self.error_cum = 0


    def _update(self, error):
        """ Add a new error to the learning and return the updated control
            variable
        """
        self.error_cum += error
        control = self.a * error + self.b * self.error_cum
        return control

    def update(self, error):
        return max(0, self._update(error))




