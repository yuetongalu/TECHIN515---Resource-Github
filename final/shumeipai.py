import speech_recognition as sr
import pyttsx3
import db
import my_openai
from typing import List

# 初始化 pyttsx3
engine = pyttsx3.init()

# 设置声音属性
engine.setProperty('rate', 125)  # 调整为中等语速
engine.setProperty('volume', 1.0)  # 最大音量

# 选择发声的声音（根据系统和语音库）
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 可以更换索引以选择不同的声音

# 全局参数
origin_sentences: List[str] = []
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


def listen_and_respond():
    global listening
    global total_duration
    global origin_sentences
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Please [%s] speak now..." % cur_role)
        try:
            # 监听音频
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            # 生成原文
            origin_sentence = recognizer.recognize_google(audio)
            print("[%s] said: %s" % (cur_role, origin_sentence))
            # 判断终止
            if "stop listening" in origin_sentence.lower():
                print("Stopping listening.")
                listening = False
                return
            # 生成：音频时长，译文，标签
            sentence_duration = int(len(audio.frame_data) / (audio.sample_rate * audio.sample_width))
            total_duration = total_duration + sentence_duration
            origin_sentences.append(origin_sentence)
            ai_sentence, label = my_openai.get_sentence_resp(origin_sentences)
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
            # 说话
            engine.say(ai_sentence)
            engine.runAndWait()
            return

        except sr.UnknownValueError:
            engine.say("I didn't understand what was said.")
            engine.runAndWait()
        except sr.RequestError as e:
            engine.say("Failed to request results from the speech recognition service.")
            engine.runAndWait()


if __name__ == "__main__":
    # 插入interview表
    interview_id = db.insert_interview(0, '', 0)
    # 循环处理音频
    while listening:
        listen_and_respond()
        change_role()

    # 生成总结
    summary = my_openai.get_interview_resp(origin_sentences)
    # 更新interview表
    db.update_interview(interview_id, summary, total_duration)
    engine.stop()
