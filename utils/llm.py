import config.config
import requests
import logging
import json

def invoke_llm(prompt: str) -> str:
    """
    Invoke the language model with the given prompt.
    This is the main entry point for using the LLM.
    """
    return invoke_ollama(prompt)


def _parse_streaming_response(response_text: str) -> str:
    """
    Parse OLLAMA streaming response format where each line is a separate JSON object.
    """
    full_response = []
    for line in response_text.strip().split("\n"):
        if not line.strip():
            continue
        try:
            json_obj = json.loads(line)
            response_part = json_obj.get("response", "")
            if response_part:
                full_response.append(response_part)
            if json_obj.get("done"):
                break
        except json.JSONDecodeError:
            logging.warning(f"Failed to parse JSON line: {line}")
    return "".join(full_response)




def invoke_ollama(prompt: str) -> str:
    """
    Invoke the OLLAMA model with the given prompt.
    """
    ollama_config = config.config.load_ollama_config()
    url = ollama_config["ollama_url"]
    model = ollama_config["ollama_model"]

    try:
        response = requests.post(
            f"{url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        try:
            return response.json().get("response", "")
        except json.JSONDecodeError:
            logging.warning(
                "JSON parsing failed. Attempting to parse as streaming response."
            )
            return _parse_streaming_response(response.text)

    except requests.exceptions.RequestException as e:
        error_msg = f"OLLAMA request failed: {e}"
        logging.error(error_msg)
        if isinstance(e, requests.exceptions.ConnectionError):
            return f"Sorry, I can't connect to the AI service at {url}. Please make sure OLLAMA is running."
        if isinstance(e, requests.exceptions.Timeout):
            return (
                "Sorry, the AI service is taking too long to respond. Please try again."
            )
        return "Sorry, there was an error communicating with the AI service. Please try again later."

    except Exception as e:
        logging.error(
            f"An unexpected error occurred in invoke_ollama: {e}", exc_info=True
        )
        return "Sorry, an unexpected error occurred. Please try again later."
