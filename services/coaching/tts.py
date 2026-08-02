from io import BytesIO
from gtts import gTTS # google text to speech

class TextToSpeech:
    def speech(self, text, lang="en"):
        cleaned = (text or "").strip() # prevents if text is None

        if not cleaned:
            return 

        buffer = BytesIO() # Creates an empty temporary file in RAM.

        gTTS(text=cleaned,lang=lang).write_to_fp(buffer) # audio to buffer
        buffer.seek(0) # after wrting move pointer to start

        print("Generating speech:", text)

        audio = buffer.read()
        print("Audio bytes:", len(audio))

        return audio
