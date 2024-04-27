import speech_recognition as sr
import pyttsx3
import openai
import db
import os

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
messages = [{"role": "system", "content": "Your name is Tom and give answers in 2 lines"}]


def get_sentence_resp(origin_sentence: str):
    messages.append({
        "role": "user",
        "content": origin_sentence,
    })
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        print(response)
        chatgpt_reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": chatgpt_reply})
        return chatgpt_reply
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)


def get_interview_resp(user_input):
    messages.append({"role": "user", "content": user_input})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        chatgpt_reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": chatgpt_reply})
        return chatgpt_reply
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)


def listen_and_respond(duration: int):
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Please speak now...")

        try:
            # 生成原文
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=5)
            origin_sentence = recognizer.recognize_google(audio)
            print("You said:", origin_sentence)
            # 判断终止
            if "stop listening" in origin_sentence.lower():
                print("Stopping listening.")
                return False
            # 生成
            all_sentence.append(origin_sentence)
            ai_sentence = get_sentence_resp(origin_sentence)
            # 插入sentence
            sentence = db.SentenceData
            db.insert_sentence(sentence)

            # 说话
            engine.say(ai_sentence)
            engine.runAndWait()
            return True

        except sr.UnknownValueError:
            engine.say("I didn't understand what was said.")
            engine.runAndWait()
        except sr.RequestError as e:
            engine.say("Failed to request results from the speech recognition service.")
            engine.runAndWait()

    return True


if __name__ == "__main__":
    listening = True
    all_sentence = []
    total_duration = 0
    interview_id = db.insert_interview('', 0)
    while listening:
        duration = 10
        total_duration += duration
        listening = listen_and_respond(duration)

    # todo 调用openai，更新interview
    db.update_interview(interview_id, '', total_duration)
    engine.stop()
