# import speech_recognition as sr
# import pyttsx3
import time

import openai
import db
import os
from typing import Tuple

# 初始化 pyttsx3
# engine = pyttsx3.init()

# 设置声音属性
# engine.setProperty('rate', 125)  # 调整为中等语速
# engine.setProperty('volume', 1.0)  # 最大音量

# 选择发声的声音（根据系统和语音库）
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id)  # 可以更换索引以选择不同的声音

# 设置OpenAI API键和自定义ChatGPT角色
openai.api_key = "sk-proj-el6izMseehUEpqT39m3jT3BlbkFJyWjYzo5USrwjRK007fu6"
sentence_msg = [
    {"role": "system",
     "content": "我和朋友正在进行一场面试，之后会轮流输入说话的内容。每次我们一个人说完话之后，你需要做两件事：1.对我们说的内容产出一个20字以内的总结；2.从【自信、专业、傻瓜】这三个标签中选择一个最符合当前这段话的标签；3.你每次返回的格式必须符合模版并保持固定。样式为【总结：xxx，标签：xxx】",
     }
]
interview_msg = [
    {"role": "system", "content": "我会传给你一段面试对话，你需要根据所有的对话内容给我返回一个100字数以内的总结"}
]

# 全局参数
manager = 'manager'
candidate = 'candidate'
total_duration = 0
cur_role = manager
listening = True


def change_role():
    global cur_role
    if cur_role == manager:
        cur_role = candidate
    else:
        cur_role = manager


def get_sentence_resp(origin_sentence: str) -> Tuple[str, str]:
    sentence_msg.append({
        "role": 'user',
        "content": origin_sentence,
    })
    interview_msg.append({
        "role": 'user',
        "content": origin_sentence,
    })
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=sentence_msg
        )
        chatgpt_reply = resp["choices"][0]["message"]["content"]
        print(chatgpt_reply)
        tag_index = chatgpt_reply.find("标签:")
        # 提取总结内容，假设总结部分总是从开始到“标签:”关键字前
        ai_sentence = chatgpt_reply[3:tag_index].strip() if tag_index != -1 else chatgpt_reply[3:].strip()
        # 提取标签内容，从“标签:”开始到字符串末尾
        tag = chatgpt_reply[tag_index + 3:].strip() if tag_index != -1 else ""
        return ai_sentence, tag
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
        interview_summary = resp["choices"][0]["message"]["content"]
        print(interview_summary)
        return interview_summary
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)


def listen_and_respond(origin_sentence: str):
    global listening
    global total_duration
    # with sr.Microphone() as source:
    #     recognizer = sr.Recognizer()
    #     recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Please [%s] speak now..." % cur_role)
    # try:
    # 监听音频
    # audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
    # 生成原文
    # origin_sentence = recognizer.recognize_google(audio)
    print("[%s] said: %s" % (cur_role, origin_sentence))
    # 判断终止
    if "stop listening" in origin_sentence.lower():
        print("Stopping listening.")
        listening = False
        return
    # 生成：音频时长，译文，标签
    # sentence_duration = int(len(audio.frame_data) / (audio.sample_rate * audio.sample_width))
    sentence_duration = 5
    ai_sentence, label = get_sentence_resp(origin_sentence)
    # 插入sentence
    sentence = db.SentenceData(
        interview_id=interview_id,
        role=cur_role,
        origin_sentence=origin_sentence,
        ai_sentence=ai_sentence,
        label=label,
        duration=sentence_duration,
    )
    # 插入sentence表
    db.insert_sentence(sentence)
    total_duration = total_duration + sentence_duration
    # 说话
    # engine.say(ai_sentence)
    # engine.runAndWait()
    return


if __name__ == "__main__":
    # 插入interview表
    interview_id = db.insert_interview('', 0)
    s = ["你好，请先做个自我介绍", "我叫apple，我在找sde工作", "你会java吗", "不会", "那你会什么", "我擅长写ppt，曾经获得比赛第一名", "很好，你符合我们的要求，你被录用了", "谢谢", "stop listening"]
    i = 0
    # 循环处理音频
    while listening:
        listen_and_respond(s[i])
        change_role()
        i += 1
        time.sleep(5)

    # 生成总结
    summary = get_interview_resp()
    # 更新interview表
    db.update_interview(interview_id, summary, total_duration)
    # engine.stop()
