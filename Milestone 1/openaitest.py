import lgpio
import speech_recognition as sr
import pyttsx3
import openai
import wave

# Initializing pyttsx3
listening = True
engine = pyttsx3.init()

# Set your openai api key and customize the chatgpt role
openai.api_key = "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"
messages = [{"role": "system", "content": "Your name is Tom and give answers in 2 lines"}]

# Customizing the output voice
voices = engine.getProperty('voices')
rate = engine.getProperty('rate')
volume = engine.getProperty('volume')

# Initialize the GPIO
h = lgpio.gpiochip_open(4)

#To do make sure the file is not closed and that I can givefurther commands withoout stopping recording unless I say "stop recording". Thus the command should not stop the main thread.

def get_response(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply

def start_recording(recognizer, source):
    print("Recording started...")
    audio = recognizer.listen(source)  # Record until the source stops
    with open("recording.wav", "wb") as f:
        f.write(audio.get_wav_data())
    print("Recording stopped and saved as 'recording.wav'")
    return audio

def stop_recording_and_save(audio):
    try:
        text = recognizer.recognize_google(audio)
        with open("transcription.txt", "w") as f:
            f.write(text)
        print("Transcription saved as 'transcription.txt'")
    except sr.UnknownValueError:
        print("Could not understand audio")

recording = False
audio_data = None

while listening:
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        recognizer.dynamic_energy_threshold = 3000

        try:
            if not recording:
                print("Listening...")
                audio = recognizer.listen(source, timeout=5.0)
                response = recognizer.recognize_google(audio)
                print(response)

                if "start recording" in response.lower():
                    recording = True
                    audio_data = start_recording(recognizer, source)
                if "tom" in response.lower():
                    response_from_openai = get_response(response)
                    engine.setProperty('rate', 120)
                    engine.setProperty('volume', volume)
                    engine.setProperty('voice', 'greek')
                    engine.say(response_from_openai)
                    engine.runAndWait()
                else:
                    print("No special command detected.")

            elif "end recording" in response.lower():
                recording = False
                stop_recording_and_save(audio_data)

        except sr.UnknownValueError:
            print("Didn't recognize anything.")

# Clean up GPIO on exit
lgpio.gpiochip_close(h)
print("GPIO cleanup completed")


