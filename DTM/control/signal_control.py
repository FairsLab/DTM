
import traci

class SignalControl:
    def __init__(self):
        pass
    
    
    def data_driven_control(controller_id = 'A1'):
        #     a=random.rand(1)
#     if change_rate < a:
#         traci.trafficlight.setPhaseId(id, p1)
        controller_id = controller_id
        
        # Define the custom program
        # Create a Logic instance
        program_id = "data_driven_control"
        phases = [
            traci.trafficlight.Phase(80, "GGGGgrrrrrGGGGgrrrrr", 5, 80),
            traci.trafficlight.Phase(3, "yyyyyrrrrryyyyyrrrrr"),
            traci.trafficlight.Phase(50, "rrrrrGGGGgrrrrrGGGGg", 5, 50),
            traci.trafficlight.Phase(3, "rrrrryyyyyrrrrryyyyy")
        ]
        logic = traci.trafficlight.Logic(programID=program_id, type=0, currentPhaseIndex=0, phases=phases)
        
        print('*'*20,program_id)
        # Apply the custom program to the traffic light
        traci.trafficlight.setProgramLogic(controller_id, logic)


            
    


# phase('rrrgggrrrr')ss
# road_id
# if current_phase == r:
    
#     another_pahse_plan={'rrr
#                         ggg
#                         ggg
#                         rrr
#                         ',id = p2}
#     traci.trafficlight.setPhaseId = p2
#     s




# Ensure this function is called within the context of a running SUMO simulation.

