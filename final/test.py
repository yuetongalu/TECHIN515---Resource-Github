import openai
from typing import Tuple

# 设置OpenAI API键和自定义ChatGPT角色
openai.api_key = "sk-proj-TQUS6WVF82otvC5jn3xHT3BlbkFJ6eIvYJWqFlvUsCXCJcar"
sentence_msg = [
    {"role": "system",
     "content": "我和朋友正在进行一场面试，之后会轮流输入说话的内容。每次我们一个人说完话之后，你需要做两件事：1.对我们说的内容产出一个50字以内的总结；2.从【自信、专业、傻瓜】这三个标签中选择一个最符合当前这段话的标签；3.你每次返回的格式必须符合模版并保持固定。样式为【总结：xxx，标签：xxx】",
     }
]
interview_msg = [
    {"role": "system", "content": "我会传给你一段面试对话，你需要根据所有的对话内容给我返回一个100字数以内的总结"}
]

def get_sentence_resp(origin_sentence: str) -> Tuple[str, str]:
    sentence_msg.append({
        "role": 'user',
        "content": origin_sentence,
    })
    interview_msg.append({
        "role": 'user',
        "content": interview_msg,
    })
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=sentence_msg
        )
        print(resp)
        chatgpt_reply = resp["choices"][0]["message"]["content"]
        print(chatgpt_reply)
        return chatgpt_reply
    except Exception as e:
        print("Failed to get response from OpenAI: " + str(e))
        return "Failed to get response from OpenAI: " + str(e), ''


def get_interview_resp() -> str:
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=interview_msg
        )
        print(resp)
        summary = resp["choices"][0]["message"]["content"]
        print(summary)
        return summary
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)



get_sentence_resp("你好，现在面试开始，你会用python吗")
print('----------------------------------------------------------')
get_sentence_resp("我不会")
print('----------------------------------------------------------')
# get_sentence_resp("那你会用java吗")
# print('----------------------------------------------------------')
# get_sentence_resp("我听说但是也不太会")
# print('----------------------------------------------------------')
# get_sentence_resp("那你会什么")
# print('----------------------------------------------------------')
# get_sentence_resp("我精通写ppt汇报工作。曾获得全国ppt比赛一等奖")
# print('----------------------------------------------------------')
# get_sentence_resp("那你很符合我们的要求，你被录用了")
# print('**********************************************************')
get_interview_resp()