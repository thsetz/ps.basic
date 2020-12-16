from ps.basic.State import StateError

def get_graph(fsm, title=None):
    """Generate a DOT graph with pygraphviz."""
    import pygraphviz as pgv 
        
    FSM_DOT_ATTRS = {
        'directed': True,
        'strict': False,
        'rankdir': 'LR',
        'ratio': '0.3'
    }

    STATE_DOT_ATTRS = { 
        'shape': 'circle',
        'height': '1.2',
    }   
    
    DOT_FINAL= 'doublecircle'

    title = fsm.name


    fsm_graph = pgv.AGraph(title=title, size="10.3, 5.3", **FSM_DOT_ATTRS)
    fsm_graph.node_attr.update(STATE_DOT_ATTRS)

    if fsm.init_state == None:
            raise StateError('A FSM must have a defined init_state')

    for state in [fsm.init_state] + fsm.states:
        print("STATE GENERATOR " + state.name)
        color="black"
        shape = STATE_DOT_ATTRS['shape']
        if hasattr(fsm, 'final_states'):
            if id(state) in [id(s) for s in fsm.final_states]:
                shape = DOT_FINAL
        if hasattr(fsm, 'error_states'):
            if id(state) in [id(s) for s in fsm.error_states]:
                color = 'red' 

        try:
            tooltip_str=pprint.pformat(inspect.getdoc(state.compute_function))
        except:
            tooltip_str=None
        if tooltip_str: tooltip = tooltip_str.replace("\\n","&#013;")
        else:           tooltip = "no tooltip"
        fsm_graph.add_node(n=state.name, shape=shape, color=color, tooltip=tooltip)
        if state.mail_addr: 
            print(state.mail_addr) 
            print(type(state.mail_addr))
            l=eval(state.mail_addr)
            for d in l:
                l2= d.keys()
                name = list(l2)[0]
                value= d[name]
                fsm_graph.add_node(n="EMAIL_DST"+name+value, label="%s:%s"%(name,value), 
                                   shape="rpromoter", style="filled", 
                                   fillcolor="lightseagreen:orangered",
                                   color = color, tooltip=tooltip)
                fsm_graph.add_edge(state.name, "EMAIL_DST"+ name+value, penwidth=2,
                                   label='send email ', style="dashed", color=color, 
                                    tooltip=tooltip)

    fsm_graph.add_node('null', shape='plaintext', label=' ')
    fsm_graph.add_edge('null', fsm.init_state.name)

    for src, input_value, dst in fsm.all_transitions:
        label = str(input_value)
        fsm_graph.add_edge(src.name, dst.name, label=label)
    for state in fsm.states:
        if state.default_transition is not None:
             if id(state.default_transition) in [id(s) for s in fsm.error_states]:
               fsm_graph.add_edge(state.name, state.default_transition.name, 
                               label='error',color='red',tooltip="werner")
             else:
               fsm_graph.add_edge(state.name, state.default_transition.name, label='else',tooltip="werner")

    return fsm_graph
