import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import speech_recognition as sr
import io
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor

CHANNEL = 'from-server'

def run_wav2vec_model(audio, emit):
    wav_data = audio.get_wav_data()
    data = io.BytesIO(wav_data)
    clip = AudioSegment.from_file(data)
    x = torch.FloatTensor(clip.get_array_of_samples())
    # print('wav_data', x)

    input = processor(x, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True)
    logits = model(input.input_values).logits
    tokens = torch.argmax(logits, axis=-1)
    results = processor.batch_decode(tokens)
    # return
    print('wav2vic', results)
    emit(CHANNEL, {"result": results[0], "method": "wav2vic"})
    return results

SAMPLE_RATE = 16_000
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-arabic"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

r = sr.Recognizer()

def run_recognizer(type, recognizer, audio, language, emit):
    result = recognizer(audio, language=language)
    # return
    print(type, result)
    emit(CHANNEL, {"result": result, "method": type})
    return result

# 
def recognize(emit):
    with sr.Microphone(sample_rate=SAMPLE_RATE) as source:
        r.adjust_for_ambient_noise(source) # This filters noise
        r.pause_threshold = 1
        print('you can speak now')
        try:
            audio = r.listen(source)
            with ThreadPoolExecutor() as executor:
                executor.submit(run_wav2vec_model, audio, emit)
                executor.submit(run_recognizer, 'google', r.recognize_google, audio, 'ar-AR', emit)
                executor.submit(run_recognizer, 'whisper', r.recognize_whisper, audio, 'ar', emit)
        except:
            print("Could not understand audio")