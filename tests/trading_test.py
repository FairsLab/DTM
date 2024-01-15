# 用于测试函数
import openai
from DTM.trading import *
from typings.datatype import *


# 智能车的个人数据
vehicle_id = "vehicle_001"
vehicle_personal_data = PersonalData(road_id="A0A1", position=[10, 20])

controller_id = "controller_1"
controller_personal_data = ControllerPersonalData()


# 智能车的交易数据
vehicle_trading_data = TradingData(
    current_token=50.0,
    history_average_price=10.0,
    accident_info={
        "Accident_Location": "road A",
        "Distance_To_Trading_Point": "50m",
        "Time_To_Trading_Point": "20s",
        "Accident_Severity": "high",
        "Traffic_Flow": "500 veh/h",
    },
)

# controller的交易数据
controller_trading_data = TradingData(
    current_token=100, history_average_price=10, accident_info=None
)

# 智能车的偏好设置
vehicle_preference = Preference(
    trading_purpose="获得最大化收益", expected_price=12.0, cost=1.0
)

# controller的偏好设置
controller_preference = Preference(
    trading_purpose="获得最大化收益", expected_price=10.0, cost=1.0
)

vehicle_1 = Vehicle(
    vehicle_id, vehicle_personal_data, vehicle_trading_data, vehicle_preference
)

controller_1 = Controller(
    controller_id,
    controller_personal_data,
    controller_trading_data,
    controller_preference,
)

if __name__ == "__main__":
    openai_login(azure=True)
    offer_context = vehicle_1.propose_offer()
    print(offer_context)

    decision_context = controller_1.decide_offer(offer_context)
    print(decision_context)

    # 测试提取函数
    extracted_offer = extract_offer(offer_context)
    print("Extracted Offer: ", extracted_offer)

    extracted_decision = extract_decision(decision_context)
    print("Extracted Decision: ", extracted_decision)
