# global variables

"""road network settings"""
num_intersection = 2  # NxN block network
length = 500  # length of each stretch
num_lane = 3  # number of lanes
network_settings = {"num_int": num_intersection, "length": length, "num_lane": num_lane}

"""simulation settings"""
period_gen = 300  # generate time
peak_start = 100  # peak hour start
peak_end = 200  # peak hour end
flow_off = 300  # off-peak hour flow N/hour
flow_peak = 1800  # peak hour flow N/hour
pm_off = 0.6  # off-peak  data car MPR
pm_peak = 0.3  # peak hour data car MPR
simulation_settings = {
    "period_gen": period_gen,
    "peak_start": peak_start,
    "peak_end": peak_end,
    "gen_sim": period_gen,
    "flow_off": flow_off,
    "flow_peak": flow_peak,
    "mpr_off": pm_off,
    "mpr_peak": pm_peak,
}

"""controller entity and measures"""

"""irregular event"""
# irregular event attribute
v_accident = {
    "start_time": [1000, 1700],
    "end_time": [2100, 2000],
    "lane": ["A0A1_0", "A0A1_1"],
    "pos": [430, 200],
}

"""simulation option"""
generate_net = True
control_option = True
trading_option = False
gui = False
graph_plot = True
simulation_option = {
    "generate_net": generate_net,
    "control_option": control_option,
    "trading": trading_option,
    "gui": gui,
    "graph": graph_plot,
}
vehicle_visibility = 30
