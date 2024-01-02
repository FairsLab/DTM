from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AccidentData:
    accident_id: str
    accident_location: str
    time_to_trading_point: str
    distance_to_traing_point: str
    accident_severity: str
    traffic_flow: Dict[str, List[int]]





@dataclass
class PersonalData:
    location: List[int] = field(default_factory=list)  # 位置，主要用于 Vehicle
    current_traffic_state: str = None  # 当前交通状态，主要用于 Controller
    predicted_income: float = None  # 预测收入，主要用于 Controller


@dataclass
class TradingData:
    current_token: float
    history_average_price: float
    trading_history: List[Dict[str, any]] = field(default_factory=list)  # 交易历史
    accident_info: Dict[str, any] = None  # 事故信息，主要用于 Vehicle


@dataclass
class Preference:
    trading_purpose: str
    expected_price: float
    cost: float
    skepticism: bool = None  # 对数据保留怀疑态度，主要用于 Controller


Offer = [
    {
        "name": "propose_offers",
        "description": "propose data trading offer based on the information provided",
        "parameters": {
            "type": "object",
            "properties": {
                "data_description": {
                    "type": "string",
                    "description": "The description of data which would be traded",
                },
                "price": {
                    "type": "number",
                    "description": "the proposed price of the data",  # "12 dollars"
                },
                "amount": {
                    "type": "number",
                    "description": "the amount of traded data",
                },
                "reason": {
                    "type": "string",
                    "description": "the reason to convince controller to buy the data",
                },
            },
        },
        "required": ["content"],
    }
]

# "可以为你带来更高的交通效率和安全，提高交通流畅度，从而减少事故发生的可能性，并且对城市的交通管理有积极的影响。"


Decision = [
    {
        "decision": "y",
        "reason": "我决定接受这笔交易，因为交通事故信息对于改善交通效率非常重要。根据我的personal data，我预测通过更好的交通状态可以获得50美元的收益。虽然价格略高于我的历史平均价格（10美元），但考虑到数据的重要性和潜在的效益，我认为这是一笔有利可图的交易。同时，我会在交叉验证过程中谨慎使用这些数据，以最大化我的token数量。",
    }
]
#     vehicle_id: str
#     description: str
#     price: float
#     amount: int
#     reason: str

# @dataclass
# class Decision:
#     controller_id: str
#     decision: str  # 例如 'accept' 或 'reject'
#     reason: str
