from utils.arg_helper import parse_arguments, get_config
from utils.utils import (
    import_prompt,
    file_chunks,
    merge_new_json_files,
    merge_json_files,
    read_log_file,
)
from utils.vertex_ai_model import vertexai_init, get_response

# from utils.re_extract import evaluate_result
from utils.eval_util_test import evaluate_result
from loguru import logger
import os


def main():

    # if using proxy, uncomment below lines and set proxy address
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
    os.environ["HTTPs_PROXY"] = "http://127.0.0.1:10809"

    args = parse_arguments()
    config = get_config(args.config_file)
    prompt_template = config.inference.prompt
    prompt = f"prompt.{prompt_template}"
    system_instruction, parameters, response_schema, context, safety_config = (
        import_prompt(prompt)
    )

    logger.info("Starting the application")
    log_file = os.path.join(
        config.save_dir, f"log_{config.exp_time}_{config.run_id}.txt"
    )
    logger.add(log_file)
    logger.info(f"Log file created at: {log_file}")
    logger.info(f"experiment comment:{args.comment}")
    # logger.info("Config =")
    # print(">" * 80)
    # pprint(config)
    # print("<" * 80)
    RUN_ID = config.run_id
    logger.info(f"RUN_ID: {RUN_ID}")
    if not args.test:
        # todo
        logger.info("Running in inference mode")
        logger.info("-" * 80)
        PROJECT_ID = config.model.PROJECT_ID
        LOCATION = config.model.LOCATION
        MODEL_NAME = config.model.MODEL_NAME
        logger.info(f"PROJECT_ID: {PROJECT_ID}")
        logger.info(f"LOCATION: {LOCATION}")
        logger.info(f"MODEL_NAME: {MODEL_NAME}")
        logger.info(f"system_instruction: {system_instruction}")
        logger.info(f"prompt: {context}")
        if config.inference.chunk_size:
            # chunks file into a list
            document = file_chunks(
                config.dataset.log_file, eval(config.inference.chunk_size)
            )  # 728 * 728
        else:
            document = [read_log_file(config.dataset.log_file)]
        inference_dir = os.path.join(config.save_dir, "inference_output")
        os.makedirs(inference_dir, exist_ok=True)
        # init model
        model = vertexai_init(PROJECT_ID, LOCATION, MODEL_NAME, system_instruction)
        # INFERENCE
        for i, j in enumerate(document):
            save_path = os.path.join(inference_dir, f"output{i}.json")
            logger.info(f"process the {i}th chunk, save to {save_path}")
            get_response(
                model,
                context,
                j,
                save_path,
                parameters,
                response_schema,
                safety_config,
            )
        if config.inference.chunk_size:
            if config.inference.count:
                merge_new_json_files(
                    inference_dir, f"{inference_dir}/merged_output.json"
                )
            else:
                merge_json_files(inference_dir, f"{inference_dir}/merged_output.json")
            config.test.llm_result_file = f"{inference_dir}/merged_output.json"
        else:
            config.test.llm_result_file = f"{inference_dir}/output0.json"
        evaluate_result(config)
    else:
        evaluate_result(config)


if __name__ == "__main__":
    main()
