import datetime
import os
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    GenerationConfig,
    # GenerationResponse,
    HarmCategory,
    HarmBlockThreshold,
)

# from google.generativeai.types import HarmCategory, HarmBlockThreshold
from loguru import logger
from utils.utils import (
    file_chunks,
    merge_json_files,
)  # , split_file_size   , read_log_file


# if using proxy, uncomment below lines and set proxy address
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
# os.environ['HTTPs_PROXY'] = 'http://127.0.0.1:10809'


def get_response(
    model,
    prompt,
    document,
    file_name,
    parameters,
    response_schema=None,
    safety_config=None,
):
    """get response from model
    model: GenerativeModel object
    prompt: str, prompt for model
    document: str, document to generate response for
    file_name: str, name of output file
    """
    response = model.generate_content(
        contents=f"{prompt}, {document}",
        generation_config=GenerationConfig(
            **parameters,
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
        safety_settings=safety_config,
    )
    write_response(response.text, file_name)


def write_response(response, filename):
    """write response to file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)
    logger.info(f"Generated response in {filename}")


def vertexai_init(PROJECT_ID, LOCATION, MODEL_NAME, system_instruction):
    """initialize vertex ai model
    PROJECT_ID:vertext ai module init
    LOCATION:vertext ai module init
    MODEL_NAME:generative model init
    system_instruction:generative model init
    """
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    logger.info("initial the model")
    logger.info(f"Project ID: {PROJECT_ID}")
    logger.info(f"Location: {LOCATION}")
    logger.info(f"Model Name: {MODEL_NAME}")
    # model initialization
    model = GenerativeModel(
        MODEL_NAME,
        system_instruction=system_instruction,
    )
    logger.info(f"Model system_instrcution {system_instruction}")
    return model
