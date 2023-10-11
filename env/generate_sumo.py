import os
import random
from itertools import filterfalse
from typing import Dict
import pdb
from pathlib import Path


class GenSumo:

    def __init__(self, gen_path: Path,
                 network_settings: Dict,
                 simulation_settings: Dict):
        # network path
        self.gen_path = gen_path  # simulation data path
        # network settings
        self.num_intersection = network_settings['num_int']
        self.road_length = network_settings['length']
        self.num_lane = network_settings['num_lane']
        # simulation settings
        # self.sim_period = simulation_settings['period_sim']
        self.gen_period = simulation_settings['period_gen']
        self.peak_start = simulation_settings['peak_start']
        self.peak_end = simulation_settings['peak_start']
        self.flow_peak = simulation_settings['flow_peak']
        self.flow_op = simulation_settings['flow_off']
        self.mpr_peak = simulation_settings['mpr_peak']
        self.mpr_op = simulation_settings['mpr_op']

    # generate network (to be developed to support arbitrary network)
    def generate_network(self):
        net_path = self.gen_path / 'network.net.xml'
        # pdb.set_trace()
        os.popen('netgenerate -g '
                 '--grid.number "%d" '
                 '--grid.length "%d" '
                 '-o "%s" '
                 '-L "%d" '
                 '--no-internal-links '
                 '--grid.attach-length "%d" '
                 '--no-turnarounds '
                 '--tls.guess '
                 '--tls.layout incoming'
                 % (self.num_intersection,
                    self.road_length,
                    net_path,
                    self.num_lane,
                    self.road_length))

    # generate traffic flow
    def generate_flow(self):
        flow_path = self.gen_path / 'flow.rou.xml'
        # calculate depart times
        num_route = 6  # amount of traffic flows
        time_pool_peak = list(range(self.peak_start, self.peak_end))  # peak hour depart pool
        time_pool_off = list(filterfalse(time_pool_peak.__contains__, list(range(self.gen_period))))  # off-peak poll
        num_veh_off = int(len(time_pool_off) * self.flow_op / 3600) * num_route  # off-peak depart number
        num_veh_peak = int(len(time_pool_peak) * self.flow_peak / 3600) * num_route  # peak depart number
        time_off_hv = random.choices(time_pool_off, k=num_route * int(num_veh_off * (1 - self.mpr_op)))  # HV off-peak
        time_off_cav = random.choices(time_pool_off, k=num_route * int(num_veh_off * self.mpr_op))  # CAV off-peak
        time_peak_hv = random.choices(time_pool_peak, k=num_route * int(num_veh_peak * (1 - self.mpr_peak)))  # HV peak
        time_peak_cav = random.choices(time_pool_peak, k=num_route * int(num_veh_peak * self.mpr_peak))  # CAV peak
        time_hv = time_off_hv + time_peak_hv
        time_cav = time_off_cav + time_peak_cav
        # route id list
        route_id = ['r_1', 'r_2', 'r_3', 'r_4', 'r_5', 'r_6']  # route
        reroute_id = ['re_1', 're_2']  # reroute
        # write route file
        with open(flow_path, 'w+') as flow:
            print("""<routes>

             <vType id="data" color="0,1,0" accel="0.73" decel="1.67" length="5" minGap="2.0" maxSpeed="14" 
            carFollowModel="IDM" tau="1.0"/>

            <vType id="human" color="0.5,0,0" accel="0.73" decel="1.67" length="5" minGap="2.0" maxSpeed="14" 
            carFollowModel="IDM" tau="1.6"/>

            <vType id="accident" color="1,0,0" accel="0.73" decel="1400" length="5" minGap="2.0" maxSpeed="14" 
            carFollowModel="IDM" tau="1.6"/>

            <route id="r_1" edges="bottom0A0 A0A1 A1A2 A2top0" />

            <route id="r_2" edges="bottom1B0 B0B1 B1B2 B2top1" />

            <route id="r_3" edges="bottom2C0 C0C1 C1C2 C2top2" />

            <route id="r_4" edges="left2A2 A2B2 B2C2 C2right2" />

            <route id="r_5" edges="left1A1 A1B1 B1C1 C1right1" />

            <route id="r_6" edges="left0A0 A0B0 B0C0 C0right0" />

            <route id="re_1" edges="bottom1B0 B0B1 B0B1 B1C1 C1C2 C2B2 B2top1" />

            <route id="re_2" edges="bottom1B0 B0B1 B0B1 B1A1 A1A2 A2B2 B2top1" />
            """, file=flow)
            nr_veh = 0  # initialize vehicle count and id
            for v_time in range(self.gen_period):
                if v_time in time_hv:  # hv depart
                    depart_count = time_hv.count(v_time)  # count frequency of v_time
                    rand_route = random.choices(route_id, k=depart_count)
                    for count in range(depart_count):
                        print(
                            '<vehicle id="%i" type="human" route="%s" depart="%i" departSpeed="14"/>'
                            % (nr_veh, rand_route[count], v_time), file=flow)
                        nr_veh += 1
                if v_time in time_cav:  # cav depart
                    depart_count = time_hv.count(v_time)  # count frequency of v_time
                    rand_route = random.choices(route_id, k=depart_count)
                    for count in range(depart_count):
                        print(
                            '<vehicle id="%i" type="auto" route="%s" depart="%i" departSpeed="14"/>'
                            % (nr_veh, rand_route[count], v_time), file=flow)
                        nr_veh += 1
            print("</routes>", file=flow)

    def generate_sim(self):
        cfg_file = self.gen_path / 'example.sumocfg'
        # write configuration file
        with open(cfg_file, mode='w+') as cfg:
            print(
                """<configuration 
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">""",
                file=cfg)
            print("""
        <input>
            <net-file value="%s"/>
            <route-files value="%s"/>
        </input>""" % ('network.net.xml', 'flow.rou.xml'), file=cfg)

            print("""
        <time>
            <begin value="0"/>
        </time>
        <processing>
            <route-steps value="200" />
            <time-to-teleport value="1000.0" />
            <eager-insert value="true" />
        </processing>
        <gui_only>
            <gui-settings-file value="example.view.xml"/>
        </gui_only>
        <random_number>
            <seed value="12345"/>
        </random_number>""", file=cfg)

            print("""</configuration>""", file=cfg)
        # write gui file
        gui_file = self.gen_path / 'example.view.xml'
        with open(gui_file, mode='w+') as gui:
            print(
                """
                <viewsettings>
                    <scheme name="real world"/>
                    <delay value="20"/>
                </viewsettings>
                """, file=gui)

    def generate_sumo(self):
        self.generate_network()
        self.generate_flow()
        self.generate_sim()
