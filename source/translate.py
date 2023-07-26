from enum import Enum
from abc import ABC, abstractmethod

from utilities.llm_utils import openai_query
from config.valid_languages import ValidLanguages, get_full_lang_name

class TranslationModels(Enum):
    OPENAI = 0

class Translate(ABC):
    @abstractmethod
    def translate_string(self, str, input_lang, output_lang):
        """Translate the input string from the input language to the output language

        :param str: string to be translated
        :param input_lang: input language
        :param output_lang: output language
        :return: translated string
        """
        pass

class TranslateOpenAI(Translate):
    MODEL = 'gpt-4'
    def translate_string(self, str, input_lang, output_lang):
        # system_role = f'Translate the following Hindi text to English:'
        input_lang_full = get_full_lang_name(input_lang)
        output_lang_full = get_full_lang_name(output_lang)
        query = f"Translate the following string from {input_lang_full} to {output_lang_full}:\n{str}"
        return openai_query(query, TranslateOpenAI.MODEL)

# print(TranslateOpenAI().translate_string('चीनी प्लम बहुत स्वादिष्ट होते हैं', ValidLanguages.HI, ValidLanguages.EN))
