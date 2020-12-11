from ps.basic.State import State

import logging

logger = logging.getLogger(__name__)
version = "xxxx"
def get_html_string(s):
    return s

class TransitionError: pass



class FiniteStateMachine(object):
    """Generic Finite State Machine."""

    def __init__(self, name ):
        """Construct a FSM."""
        self.name = name
        self.current_state, self.init_state  = None,None
        self.inputs , self.states , self.final_states,  self.error_states = [] , [], [], []
        #MACHINES[name] = self
        #MACHINES['default'] = MACHINES[name]

    def add_state(self, states: [State]) -> None:
        for state in states:
            if state.error: self.error_states.append(state)
            if state.final: self.final_states.append(state)
            if state.initial:
                if self.init_state == None:
                    self.init_state = state
                else:
                    raise TransitionError('Only One initial State allowed.')
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
    
    def transition(self, input_value):
        """Transition to the next state."""
        current = self.current_state
        if current is None:
            raise TransitionError('Current state not set.')

        #destination_state = current.get(input_value, current.default_transition)
        print(input_value)
        destination_state = current[input_value]
        if destination_state is None: 
            raise TransitionError('Cannot transition from state %r'
                                  ' on input %r.' % (current.name, input_value))
        else:
            self.current_state = destination_state

    def reset(self):
        """Enter the Finite State Machine."""
        self.current_state = self.init_state
        del(self.inputs)
        self.inputs = list() 

    def process(self, input_data):
        """Process input data."""
        self.reset()
        for item in input_data:
            self.transition(item)

    def run(self,context ):
        """Process input data."""
        self.reset()
        current_state = self.init_state
        logger.debug("FSM: " + self.name + " started in State " + str(current_state), extra={"package_version":version})
        while True:
            my_current_state = self.current_state
            return_value_of_compute_function = my_current_state.compute_function(my_current_state,context)
            logger.debug(my_current_state.name + "-compute_function returned  " + str(return_value_of_compute_function), extra={"package_version":version}) 
            if isinstance(return_value_of_compute_function,State):
                logger.debug("%s.run new step: %s's default_handler left context as %s"\
                                  %( self.name, my_current_state.name, get_html_string(context)), extra={"package_version":version})
            else:
                logger.debug("%s.run new step: %s's compute function left context as %s"\
                                  %( self.name, my_current_state.name, get_html_string(context)), extra={"package_version":version})
            self.inputs.append(return_value_of_compute_function)
            if my_current_state.final == True:
               logger.debug("Leave run, as " + self.current_state.name + " is a final state ", extra={"package_version":version})
               break
            else:
                self.transition(return_value_of_compute_function)
                logger.debug("TRANSITION: from State " + my_current_state.name + "<br> ONInput:   '" \
                                   + str(return_value_of_compute_function) + "'<br>To State: " + self.current_state.name \
                                         , extra={"package_version":version})

