import os
import time
from enum import Enum
from joblib import Memory
from datetime import datetime

memory = Memory('./cachedir', verbose=0)

from elevenlabs import set_api_key, voices, generate, save
set_api_key(os.getenv("ELEVEN_LABS_KEY"))

class ElevenModelEnum(Enum):
    ENGLISH = 'eleven_monolingual_v1'
    NONENGLISH = 'eleven_multilingual_v1'

def save_voice_generation(voice_name, text, model):
    voice_list = voices()
    voice_index = [v.name for v in voice_list].index(voice_name)
    voice_id = voice_list[voice_index].voice_id

    audio = generate(
    text=text,
    voice=voice_id,
    model=model.value
    )

    outpath = './output/' + f'{voice_name}_' + str(datetime.now()).replace(' ', '_') + '.wav'

    directory = os.path.dirname(outpath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    save(
        audio,
        outpath
    )

save_voice_generation("Ajay Solanky", "Welcome back to the aboveground, Yamini!", ElevenModelEnum.ENGLISH)
