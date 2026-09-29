"""
Base class for all network disturbances.

Disturbances modify the state of the electrical network during
a simulation but do not themselves contain differential equations.

Examples
--------
    - Line trip
    - Bus fault
    - Line fault
    - Generator trip
    - Inverter trip
    - Load step
    - Mechanical power step
    - Voltage reference step

Each disturbance is responsible for deciding when it becomes
active and ensuring it is only applied once (unless explicitly
designed otherwise).
"""


class Disturbance:
    """
    Base disturbance class.

    Every disturbance has:

        start_time
            Time at which the disturbance begins.

        end_time
            Optional clearing time.

        applied
            Prevents repeated application.

        cleared
            Indicates whether the disturbance has been removed.
    """

    def __init__(
            self,
            start_time,
            end_time=None,
            name=None):
        """
        Parameters
        ----------
        start_time : float
            Time at which the disturbance starts.

        end_time : float or None
            Time at which the disturbance clears.
            If None, the disturbance is permanent.

        name : str or None
            Optional descriptive name.
        """

        self.start_time = float(start_time)

        self.end_time = (
            None if end_time is None
            else float(end_time)
        )

        self.name = (
            name
            if name is not None
            else self.__class__.__name__
        )

        self.applied = False
        self.cleared = False

    # -------------------------------------------------
    # Status
    # -------------------------------------------------

    def is_active(self, t):
        """
        Returns True if the disturbance should currently
        be active.
        """

        if t < self.start_time:
            return False

        if self.end_time is None:
            return True

        return self.start_time <= t < self.end_time

    # -------------------------------------------------
    # Simulation interface
    # -------------------------------------------------

    def apply(self, t, grid):
        """
        Apply the disturbance.

        Must be implemented by subclasses.

        Parameters
        ----------
        t : float
            Current simulation time.

        grid : Grid
            Grid object being simulated.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__} must implement apply()."
        )

    def clear(self, t, grid):
        """
        Clear (remove) the disturbance.

        Permanent disturbances do not need to override this.

        Parameters
        ----------
        t : float
            Current simulation time.

        grid : Grid
            Grid object.
        """

        self.cleared = True

    # -------------------------------------------------
    # Reset
    # -------------------------------------------------

    def reset(self):
        """
        Reset disturbance so that it can be reused in
        another simulation.
        """

        self.applied = False
        self.cleared = False

    # -------------------------------------------------
    # Display
    # -------------------------------------------------

    def __repr__(self):

        if self.end_time is None:

            return (
                f"{self.name}"
                f"(start={self.start_time})"
            )

        return (
            f"{self.name}"
            f"(start={self.start_time}, "
            f"end={self.end_time})"
        )