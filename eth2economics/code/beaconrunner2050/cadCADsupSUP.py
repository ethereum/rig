import time

def get_observed_initial_conditions(initial_conditions, observers):
    # Add initial observed values
    for k, f in observers.items():
        initial_conditions[k] = f(initial_conditions)
    return initial_conditions

def get_observed_psubs(psubs, observers):
    # Add observers to the variable updates in psubs
    for psub in psubs:
        for k, f in observers.items():
            psub["variables"][k] = lambda params, step, sL, s, _input, f=f, k=k: (k, f(s))
    return psubs

def loop_time(params, step, sL, s, _input):
    print(s["timestep"], ">> loop_time =", time.time() - s["loop_time"])
    return ("loop_time", time.time())

def loop_duration(params, step, sL, s, _input):
    return ("loop_duration", time.time() - s["loop_time"])
    
def add_loop_ic(initial_conditions):
    initial_conditions["loop_time"] = time.time()
    initial_conditions["loop_duration"] = 0
    return initial_conditions

def add_loop_psubs(psubs):
    psubs[-1]["variables"]["loop_time"] = loop_time
    psubs[-1]["variables"]["loop_duration"] = loop_duration
    return psubs