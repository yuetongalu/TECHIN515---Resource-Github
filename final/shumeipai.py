import speech_recognition as sr
import pyttsx3
import openai
import db
import os
from typing import Tuple

# 初始化 pyttsx3
engine = pyttsx3.init()

# 设置声音属性
engine.setProperty('rate', 125)  # 调整为中等语速
engine.setProperty('volume', 1.0)  # 最大音量

# 选择发声的声音（根据系统和语音库）
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 可以更换索引以选择不同的声音

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
all_sentence = []
manager = 'manager'
candidate = 'candidate'


def change_role(role: str) -> str:
    if role == manager:
        return candidate
    return manager


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


def listen_and_respond(role: str) -> Tuple[bool, int]:
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Please [%s] speak now..." % (role))
        try:
            # 监听音频
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            # 生成原文
            origin_sentence = recognizer.recognize_google(audio)
            print("[%s] said: %s" % (role, origin_sentence))
            # 判断终止
            if "stop listening" in origin_sentence.lower():
                print("Stopping listening.")
                return False, 0
            # 生成：音频时长，译文，标签
            duration = len(audio.frame_data) / (audio.sample_rate * audio.sample_width)
            ai_sentence, label = get_sentence_resp(origin_sentence)
            # 插入sentence
            sentence = db.SentenceData(
                interview_id=interview_id,
                origin_sentence=origin_sentence,
                ai_sentence=ai_sentence,
                label=label,
                duration=int(duration),
            )
            db.insert_sentence(sentence)
            all_sentence.append(origin_sentence)
            # 说话
            engine.say(ai_sentence)
            engine.runAndWait()
            return True, int(duration)

        except sr.UnknownValueError:
            engine.say("I didn't understand what was said.")
            engine.runAndWait()
        except sr.RequestError as e:
            engine.say("Failed to request results from the speech recognition service.")
            engine.runAndWait()


if __name__ == "__main__":
    interview_id = db.insert_interview('', 0)
    total_duration = 0
    role = manager
    listening = True
    while listening:
        listening, duration = listen_and_respond(role)
        role = change_role(role)
        total_duration = 0

    # todo 调用openai，更新interview
    db.update_interview(interview_id, '', total_duration)
    engine.stop()
