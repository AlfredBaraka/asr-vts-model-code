from transformers import VitsModel, AutoTokenizer
import torch
import numpy as np
import scipy.io.wavfile
import os

model_path = "/home/egovridc//Desktop/learn/asr-vts-model-code/vits"
model = VitsModel.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

def generate_speech_from_text(text, output_file="static/audio/output.wav"):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    output_np = output.squeeze().cpu().numpy()
    if output_np.dtype == 'float32':
        output_np = (output_np * 32767).astype('int16')
    scipy.io.wavfile.write(output_file, rate=model.config.sampling_rate, data=output_np)
