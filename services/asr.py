import torch
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torchaudio

model = Wav2Vec2ForCTC.from_pretrained("/home/egovridc/Desktop//learn/asr-vts-model-code/wav2vec_swahili/")
processor = Wav2Vec2Processor.from_pretrained("/home/egovridc/Desktop/learn/asr-vts-model-code/wav2vec_swahili/")

def transcribe_audio(audio_path: str):
    # Load audio file (must be 16kHz, mono-channel)
    speech, sample_rate = sf.read(audio_path)

    # Ensure the audio file is resampled to 16kHz if needed
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        speech = resampler(torch.tensor(speech).unsqueeze(0)).squeeze(0).numpy()

    # Tokenize and perform inference
    input_values = processor(speech, sampling_rate=16000, return_tensors="pt", padding=True).input_values

    # Get logits from the model
    with torch.no_grad():
        logits = model(input_values).logits

    # Decode predicted tokens to text
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]

    return transcription