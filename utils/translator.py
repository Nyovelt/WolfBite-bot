import json
import os
from utils.llm import invoke_llm


def load_translations(language):
    """
    Load translation dictionary for a given language.
    """
    path = f"translations/{language}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def log_untranslated(text, language):
    path = "translations/untranslated.json"
    try:
        with open(path, "r+", encoding="utf-8") as file:
            data = json.load(file)
            if language not in data:
                data[language] = []
            if text not in data[language]:  # Check if the text is already logged
                data[language].append(text)
                file.seek(0)
                json.dump(data, file, indent=4)
    except FileNotFoundError:
        with open(path, "w", encoding="utf-8") as file:
            json.dump({language: [text]}, file, indent=4)



def translate_text(text, language):
    """
    Translate text using the loaded translations for the specified language.
    """
    if language == "English":
        return text  # Skip translation if the language is English
    translations = load_translations(language)
    if text not in translations:
        # use llm to translate the text
        translated_text = translate_text_use_llm(text, language)
        log_untranslated(text, language)  # Log untranslated text
        return translated_text  # Use the original text if no translation is found
    return translations.get(text, text)


def translate_text_use_llm(text, language):
    """
    Translate text using a language model for the specified language.
    """
    if language == "English":
        return text  # Skip translation if the language is English
    # Call the language model API here
    prompt = (
        f"Translate the following text to {language}.\n"
        "Only answer with the translated text.\n"
        "Add an emoji for the food before the text only if the text is a dish.\n"
        f"{text}."
    )
    response = invoke_llm(prompt)
    return response
