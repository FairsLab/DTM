from __future__ import absolute_import
from __future__ import print_function

import pdb
from typing import Dict
import os
# import pdb
import sys

try:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    import sumolib
except ImportError:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
import traci
from env.generate_sumo import GenSumo
from env.gen_event import Event
from control.signal_control import SignalControl
from data_trade.data_trade import DataTrade


class SimTraci:
    # class CAV:
    #     def __init__(self, id, token, credit):
    #         self.id = id
    #         self.token = token
    #         self.credit = credit

    def __init__(self, **kwargs):
        # simulation option
        self.anime_variable = kwargs['option']['gui']
        self.generate_net = kwargs['option']['generate_net']
        self.control_option = kwargs['option']['control_option']
        self.data_trade = kwargs['option']['trading']
        self.graph_plot = kwargs['option']['graph']
        # network data path
        self.gen_path = kwargs['network']
        # event data
        self.event = kwargs['event']
        # network settings for a random network
        self.network_setting = kwargs['network_setting']
        # simulation settings
        self.simulation_setting = kwargs['simulation_setting']
        # sim step initial
        self.sim_step = 0

    def __sumo_run(self, **kwargs):
        event = kwargs.get('event', None)
        trade_register = kwargs.get('trade', None)
        controlled_signal = kwargs.get('control', None)
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            # pdb.set_trace()
            if event:
                event.event_loger(self.sim_step)
            if trade_register:
                pass
            # if self.graph_plot:
            #     if self.simstep % 200 == 0:
            #         GraphPresent.draw_physic()
            #         self.draw_control()
            self.sim_step += 1
        traci.close()
        sys.stdout.flush()

    # start sumo simulation
    def __sumo_start(self):
        if self.anime_variable:
            sumo_binary = sumolib.checkBinary('sumo-gui')  # animation
        else:
            sumo_binary = sumolib.checkBinary('sumo')  # no animation
        sim_path = (self.gen_path / 'example.sumocfg').absolute()
        try:
            traci.start([sumo_binary, "-c", sim_path, "--step-length", '0.1'])
        except UserWarning:
            sys.exit("No simulation data")

    def __sumo_initialize(self) -> Dict:
        obj_dict = dict()
        # pdb.set_trace()
        if self.event:
            event = Event(self.event)
            obj_dict['event'] = event
        if self.data_trade:
            trade = DataTrade()
            signal = SignalControl()
            obj_dict['trade'] = trade
            obj_dict['control'] = signal
        return obj_dict

    # generate sumo configuration files
    def __sumo_generate(self):
        # generate net or not
        if self.generate_net:
            gen_data = GenSumo(self.gen_path, self.network_setting, self.simulation_setting)
            gen_data.generate_sumo()
        else:
            pass
        # actuated traffic signal on or off
        net_dir = self.gen_path / 'network.net.xml'
        if self.control_option:
            os.popen('netconvert '
                     '-s "%s" '
                     '--o "%s" '
                     '--tls.rebuild '
                     '--tls.default-type actuated'
                     % (net_dir,
                        net_dir))
        else:
            os.popen('netconvert '
                     '-s "%s" '
                     '--o "%s" '
                     '--tls.rebuild '
                     '--tls.default-type static'
                     % (net_dir,
                        net_dir))

    def sim_run(self):
        self.__sumo_generate()
        obj_dict = self.__sumo_initialize()
        # pdb.set_trace()
        self.__sumo_start()
        self.__sumo_run(**obj_dict)