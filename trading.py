from .datatype import PersonalData, TradingData, Preference
import openai

class MetaActor:
    personal_data: PersonalData
    trading_data: TradingData
    preference: Preference
    pass

class Vehicle(MetaActor):
    pass

class Controller(MetaActor):
    pass



def handle_propose_offer(vehicle):
    # 整合输入数据
    input_data = {
        'personal_data': vehicle.personal_data,
        'trading_data': vehicle.trading_data,
        'preference': vehicle.preference
    }

    # 转换input_data为适合openai.ChatCompletion.create()的格式
    prompt = format_input_for_openai(input_data)

    # 调用openai.ChatCompletion.create()来生成提议
    response = openai.ChatCompletion.create(
        model="text-davinci-003",
        prompt=prompt,
        # 其他适当的参数
    )

    # 从response中提取message
    message = response.choices[0].message

    # 返回message给controller
    return message

def handle_decide_offer(controller, message):
    # 整合输入数据
    input_data = {
        'message': message,
        'personal_data': controller.personal_data,
        'trading_data': controller.trading_data,
        'preference': controller.preference
    }

    # 转换input_data为适合openai.ChatCompletion.create()的格式
    prompt = format_input_for_openai(input_data)

    # 调用openai.ChatCompletion.create()来生成决策
    response = openai.ChatCompletion.create(
        model="text-davinci-003",
        prompt=prompt,
        # 其他适当的参数
    )

    # 从response中提取新的message
    new_message = response.choices[0].message

    # 返回新的message给vehicle
    return new_message

def format_input_for_openai(input_data):
    # 格式化input_data为字符串，适用于openai.ChatCompletion.create()
    # 这里可以根据您的具体需求进行定制
    return str(input_data)





