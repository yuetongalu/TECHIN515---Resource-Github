import openai
import db
import os
from typing import Tuple, List
from dotenv import load_dotenv

# 设置OpenAI API键和自定义ChatGPT角色
load_dotenv()
openai.api_key = os.getenv('openai_key')

sentence_system_msg = {"role": "system",
                       "content": "我和朋友正在进行一场面试，之后会轮流输入说话的内容。每次我们一个人说完话之后，你需要做两件事：1.对我们说的内容产出一个20字以内的总结；2.从【自信、专业、傻瓜】这三个标签中选择一个最符合当前这段话的标签；3.你每次返回的格式必须符合模版并保持固定。样式为【总结：xxx，标签：xxx】",
                       }
interview_system_msg = {"role": "system",
                        "content": "我会传给你一段面试对话，你需要根据所有的对话内容给我返回一个100字数以内的总结"}

tag_system_msg = {"role": "system",
                  "content": "我会传给你一段面试对话，并且每句话已经被打了相同的标签。你需要根据所有的对话内容给我返回一个100字数以内的总结"}


def get_sentence_resp(origin_sentences: List[str]) -> Tuple[str, str]:
    try:
        sentence_msg = [sentence_system_msg]
        for origin_sentence in origin_sentences:
            sentence_msg.append({
                "role": "user",
                "content": origin_sentence
            })
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


def get_interview_resp(origin_sentences: List[str]) -> str:
    try:
        interview_msg = [interview_system_msg]
        for origin_sentence in origin_sentences:
            interview_msg.append({
                "role": "user",
                "content": origin_sentence
            })
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=interview_msg
        )
        interview_summary = resp["choices"][0]["message"]["content"]
        print(interview_summary)
        return interview_summary
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)


def get_tag_summary(sentences: List[db.SentenceData]) -> str:
    try:
        tag_msg = [tag_system_msg]
        for sentence in sentences:
            tag_msg.append({
                "role": "user",
                "content": sentence.origin_sentence
            })
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=tag_msg
        )
        tag_summary = resp["choices"][0]["message"]["content"]
        print(tag_summary)
        return tag_summary
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)
