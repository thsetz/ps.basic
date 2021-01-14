from typing import Any, Callable


class StateError(Exception):
    """Error in fsm."""

    def __init__(self, message):
        """Error in fsm."""
        self.message = message


class State(dict):
    """State class.

    >>> def f(state: State, context: dict) -> str:
    ...     return "FIN"
    >>> final = State("FINAL", f, final=True)
    """

    def __init__(
        self,
        name: str,
        compute_function: Callable[[Any, dict], str],
        initial: bool = False,
        final: bool = False,
        error: bool = False,
        mail_addr: str = "",
        default: Any = None,
    ):
        """Construct a state."""
        self.name = name
        self.compute_function = compute_function
        self.final = final
        self.error = error
        self.initial = initial
        self.mail_addr = mail_addr
        self.default_transition = default
        self.tooltip = "None"

    def __getitem__(self, input_value):
        """Make a transition to the next state."""
        return dict.__getitem__(self, input_value)

    def __setitem__(self, input_value, next_state):
        """Set a transition to a new state."""
        if not isinstance(next_state, State):
            raise StateError(
                "A state must transition to another state,"
                " got %r instead." % next_state
            )
        dict.__setitem__(self, input_value, next_state)

    def __repr__(self):
        """Represent the object in a string."""
        return "<%r %s @ 0x%x>" % (
            self.name,
            self.__class__.__name__,
            id(self),
        )
