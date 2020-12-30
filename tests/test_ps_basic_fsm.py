import pytest
import os
import pprint
from ps.basic import Config
from t_utils import TEST_SERVICE_NAME

os.environ["IS_TESTING"] = "YES"
Config.Basic(TEST_SERVICE_NAME)
from ps.basic.State import State, StateError
from ps.basic.fsm import FiniteStateMachine, TransitionError
from ps.basic.get_graph import get_graph


def f(state: State, context: dict) -> str:
    context[state.name] = "visited"
    print(state.name)
    context[state.name] = state.name
    print(pprint.pformat(context))
    if state.name == "START":
        return "input"
    if state.name == "STAGE1":
        return "input2"
    if state.name == "FIN":
        return "ii"


def test_no_initial_stage_raise_Attribute_error():
    stage1 = State("STAGE1", f)
    fsm = FiniteStateMachine("TheMachine")
    fsm.add_state([stage1])
    with pytest.raises(AttributeError):
        fsm.run({})


def test_input_not_in_alphabet_raises_Transition_error():
    stage1 = State("STAGE1", f)
    fsm = FiniteStateMachine("TheMachine")
    fsm.add_state([stage1])
    with pytest.raises(TypeError):
        fsm.process(["a"])


def test_multiple_initial_stages_raise_Transition_error():
    start = State(
        "START",
        f,
        initial=True,
    )
    stage1 = State(
        "STAGE1",
        f,
        initial=True,
    )
    fsm = FiniteStateMachine("TheMachine")
    with pytest.raises(TransitionError):
        fsm.add_state([start, stage1])


def test_attributes_are_set():
    final = State("FINAL", f, final=True)
    error = State(
        "ERROR",
        f,
        error=True,
        mail_addr='[{"A":"error_handler@mail.company"}]',
        default=final,
    )
    start = State("START", f, initial=True, default=error)
    stage1 = State("STAGE1", f, default=error)

    start["input"] = stage1
    stage1["input2"] = final
    error["go_back_to_start"] = start
    error["go_back_to_stage1"] = stage1
    kk = start["input"]
    print(kk)

    print(start)
    # start.compute_function(start,d)
    # stage1.compute_function(stage1,d)
    # error.compute_function(error,d)
    # final.compute_function(final,d)
    #

    fsm = FiniteStateMachine("TheMachine")
    fsm.add_state([start, stage1, error, final])
    fsm.run({})
    # assert False

    graph = get_graph(fsm)
    graph.draw("x.png", prog="dot")
    graph.draw("x.svg", prog="dot")


#
# Graph Printing
#
def test_get_graph_without_initi_state_raises_StateError():
    final = State("FINAL", f, final=True)
    fsm = FiniteStateMachine("TheMachine")
    fsm.add_state([final])
    with pytest.raises(StateError):
        graph = get_graph(fsm)
