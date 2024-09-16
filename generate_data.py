import os
import json
import re
from loguru import logger


def split_file_size(file_path, size_per_file, save_path):
    """split big file into small files with specified size，
    and save into specified folder
    file_path: file to split
    size_per_file: size of each small file in bytes,e.g. 512*1024 for 512KB
    save_path: dir path to save small files
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_count = 0
    current_file_size = 0
    output_file = None
    basename = os.path.basename(file_path)
    file_name = os.path.splitext(basename)[0]

    with open(file_path, "r", encoding="utf-8") as large_file:
        for line in large_file:
            line_size = len(line.encode("utf-8"))

            if current_file_size + line_size > size_per_file:
                if output_file:
                    output_file.close()
                file_count += 1
                current_file_size = 0
                output_file = open(
                    os.path.join(save_path, f"{file_name}_{file_count}.txt"),
                    "w",
                    encoding="utf-8",
                )
            elif output_file is None:
                # 初始化 output_file
                output_file = open(
                    os.path.join(save_path, f"{file_name}_{file_count}.txt"),
                    "w",
                    encoding="utf-8",
                )

            output_file.write(line)
            current_file_size += line_size

        if output_file:
            output_file.close()

    logger.info(f"Split into {file_count} files, split size {size_per_file} bytes.")


def count_occurrences(list_data, text):
    """count occurrences of items in text with Regular Expression
    items: json data of IP and URL list(without counts)
    text: text to search
    """
    result = {
        "IP": [],
        "URL": [],
    }
    for item in list_data["IP"]:
        count = len(re.findall(item, text))
        result["IP"].append({"IP": item, "count": count})
    for item in list_data["URL"]:
        count = len(re.findall(item, text))
        result["URL"].append({"URL": item, "count": count})
    return result


def get_count_data(list_data_path, text_path, save_dir):
    """
    add counts to extracted data list:
    human_data_path: path of human data list
    text_path: path of text to search
    save_path: path to save new human data list
    """
    with open(list_data_path, "r") as f:
        data = json.load(f)

    with open(text_path, "r", errors="ignore") as f:
        text = f.read()

    new_data = {
        "IP": count_occurrences(data, text)["IP"],
        "URL": count_occurrences(data, text)["URL"],
        "Memory": [],
    }

    file_name = os.path.splitext(os.path.basename(list_data_path))[0]
    save_name = os.path.join(save_dir, f"count_{file_name}.json")

    with open(save_name, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    logger.info("New human data saved to", save_name)


def remove_repeat(data):
    """remove repeat items in data"""
    data["IP"] = list(set(data["IP"]))
    data["URL"] = list(set(data["URL"]))
    return data


def get_human_json(refer_path, text_path, save_dir):
    """get human data from text with refer big human data(used to generate small file standard result)
    refer_path: path of big human data
    text_path: path of text to search
    save_dir: dir path to save result
    """
    # open file
    with open(refer_path, "r") as f:
        data = json.load(f)
    with open(text_path, "r", errors="ignore") as f:
        text = f.read()
    # find data
    found_ips = []
    found_urls = []

    for ip in data["IP"]:
        if ip in text:
            found_ips.append(ip)

    for url in data["URL"]:
        if url in text:
            found_urls.append(url)

    human_data = remove_repeat({"IP": found_ips, "URL": found_urls})

    # save
    file_name = os.path.splitext(os.path.basename(text_path))[0]
    save_name = os.path.join(save_dir, f"result_huaman_{file_name}.json")

    with open(save_name, "w") as f:
        json.dump(human_data, f, indent=4)
    logger.info("Human data saved to", save_name)


def get_extract_re(text_path, save_name):
    """extract IPs and URL from log file using regular expression
    text_path: path of text to search
    save_dir: dir path to save result
    """
    with open(text_path, "r", errors="ignore") as f:
        text_re = f.read()
    # IP pattern
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    IP = re.findall(ip_pattern, text_re)
    IP = list(set(IP))
    logger.info(f"Total IPs found:{len(IP)}")
    # URL pattern
    url_pattern = r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9-]+(?:\.[0-9]+){3})"
    URL = re.findall(url_pattern, text_re)
    URL = list(set(URL) - set(IP))  # remove IP in URL
    logger.info(f"Total URL found:{len(URL)}")

    Result = remove_repeat({"IP": IP, "URL": URL})
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)
    #     logger.info(f"Create dir {save_dir} to save result")
    with open(save_name, "w") as f:
        json.dump(Result, f, indent=4)
    logger.info(f"RE_list result saved to {save_name}")


if __name__ == "__main__":
    # file defination
    orginal_file = "data/Linux.txt"
    save_dir = "test"
    refer_file = "result/human_evaluation.json"
    chunk_size = 256 * 1024  #

    # split file and save
    split_file_size(orginal_file, chunk_size, save_dir)

    # generate count human data
    for root, dirs, files in os.walk(save_dir):
        for file in files:
            file_path = os.path.join(root, file)
            human_json_path = os.path.join(root, f"count_{file}")
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            save_name = os.path.join(save_dir, f"result_huaman_{file_name}.json")
            save_name_re = os.path.join(save_dir, f"result-re_{file_name}.json")
            get_human_json(refer_file, file_path, save_dir)
            get_count_data(save_name, file_path, save_dir)
            get_extract_re(file_path, save_name_re)
            get_count_data(save_name_re, file_path, save_dir)

    # get_extract_re("data/Linux.txt", "data/result-re_Linux.json")
    # get_count_data("data/human_evaluation.json", "data/Linux.txt", "data")
