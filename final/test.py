import openai

# 设置OpenAI API键和自定义ChatGPT角色
openai.api_key = "sk-proj-TQUS6WVF82otvC5jn3xHT3BlbkFJ6eIvYJWqFlvUsCXCJcar"
messages = [{"role": "system", "content": "Your name is Tom and give answers in 2 lines, "}]


def get_sentence_resp(origin_sentence: str):
    messages.append({
        "role": "user",
        "content": origin_sentence,
    })
    try:
        print('message---', messages)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        print(response)
        ai_sentence = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": ai_sentence})
        print(ai_sentence)
        return ai_sentence
    except Exception as e:
        return "Failed to get response from OpenAI: " + str(e)


get_sentence_resp("my name is apple")
get_sentence_resp("how are you")
