import ps.basic.Config
from ps.basic import __version__ as version
from ps.basic import get_html_string
from ps.basic.State import State


class TransitionError(Exception):
    """State Exception."""

    def __init__(self, message):
        """State Exception."""
        self.message = message


class FiniteStateMachine(object):
    """Generic Finite State Machine."""

    def __init__(self, name: str):
        """Construct a FSM."""
        self.name = name
        self.current_state, self.init_state = None, None
        self.inputs, self.states, = (
            [],
            [],
        )
        self.final_states, self.error_states = [], []

    def add_state(self, states: [State]) -> None:
        """Add State."""
        for state in states:
            if state.error:
                self.error_states.append(state)
            if state.final:
                self.final_states.append(state)
            if state.initial:
                if self.init_state is None:
                    self.init_state = state
                else:
                    raise TransitionError("Only One initial State allowed.")
            self.states.append(state)

    @property
    def all_transitions(self):
        """Get transitions from states.

        Returns:
            List of three element tuples each consisting of
            (source state, input, destination state)
        """
        transitions = list()
        for src_state in self.states:
            for input_value, dst_state in src_state.items():
                transitions.append((src_state, input_value, dst_state))
        return transitions

    def transition(self, input_value: str):
        """Transition to the next state."""
        current = self.current_state
        destination_state = current[input_value]
        self.current_state = destination_state

    def reset(self):
        """Enter the Finite State Machine."""
        self.current_state = self.init_state
        del self.inputs
        self.inputs = list()

    def process(self, input_data: str):
        """Process input data."""
        self.reset()
        for item in input_data:
            self.transition(item)

    def run(self, context: dict):
        """Process input data."""
        self.reset()
        current_state = self.init_state
        ps.basic.Config.logger.debug(
            "FSM: " + self.name + " started in State " + str(current_state),
            extra={"package_version": version},
        )
        while True:
            my_current_state = self.current_state
            rval = my_current_state.compute_function(my_current_state, context)
            s = f"{my_current_state.name}-compute_function ret {str(rval)}"
            ps.basic.Config.logger.debug(
                s, extra={"package_version": version},
            )
            s = f"{self.name}.run new step: {my_current_state.name} compute"
            s += f" function left context as {get_html_string(context)}"
            ps.basic.Config.logger.debug(
                s, extra={"package_version": version},
            )
            self.inputs.append(rval)
            if my_current_state.final is True:
                ps.basic.Config.logger.debug(
                    f"""Leave run, as
                     {self.current_state.name}
                      is a final state """,
                    extra={"package_version": version},
                )
                break
            else:
                self.transition(rval)
                ps.basic.Config.logger.debug(
                    f"""TRANSITION: from State
                    {my_current_state.name}
                    <br> ONInput:
                    {str(rval)}
                    <br>To State:
                    {self.current_state.name}""",
                    extra={"package_version": version},
                )
