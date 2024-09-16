import os
from loguru import logger
import json
import importlib


def import_prompt(prompt_file):
    '''import prompt from prompt file'''
    module_name = prompt_file
    module = importlib.import_module(module_name)

    return (
        module.system_instruction,
        module.parameters,
        module.response_schema,
        module.context,
        module.safety_config,
    )

def read_log_file(file_path):
    """read log file(txt) and return its content"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        log_content = f.read()
    return log_content


def split_file_num(file="Linux.txt", split_num=3):
    """split log file(txt) into specified number of parts
    default split into 3 parts"""
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        log_content = f.read()
    log_list = log_content.split("\n")
    split_list = [log_list[i::split_num] for i in range(split_num)]
    return split_list


# def split_file_size(file_path, size_per_file, save_path):
#     """split big file into small files with specified size，and save into specified folder
#     file_path: file to split
#     size_per_file: size of each small file in bytes,e.g. 512*1024 for 512KB
#     save_path: path to save small files
#     """
#     if not os.path.exists(save_path):
#         os.makedirs(save_path)
#     # Open the large file
#     with open(file_path, "rb") as large_file:
#         file_count = 0
#         small_file = None
#         basename = os.path.basename(file_path)
#         file_name = os.path.splitext(basename)[0]

#         while True:
#             # Read a chunk of the specified size
#             chunk = large_file.read(size_per_file)
#             if not chunk:
#                 break  # End of file

#             # Open a new small file
#             output_file = os.path.join(save_path, f"{file_name}_{file_count}.txt")
#             with open(output_file, "wb") as small_file:
#                 small_file.write(chunk)

#             file_count += 1

#         print(
#             f"Split into {file_count} files,splite szie {convert_bytes(size_per_file)}."
#         )

def split_file_size(file_path, size_per_file, save_path):
    """split big file into small files with specified size，and save into specified folder
    file_path: file to split
    size_per_file: size of each small file in bytes,e.g. 512*1024 for 512KB
    save_path: path to save small files
    the saved file are named as "file_name_file_count.txt"
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_count = 0
    current_file_size = 0
    output_file = None
    basename = os.path.basename(file_path)
    file_name = os.path.splitext(basename)[0]

    with open(file_path, "r", encoding='utf-8') as large_file:
        for line in large_file:
            line_size = len(line.encode('utf-8'))

            if current_file_size + line_size > size_per_file:
                if output_file:
                    output_file.close()
                file_count += 1
                current_file_size = 0
                output_file = open(os.path.join(save_path, f"{file_name}_{file_count}.txt"), "w", encoding='utf-8')

            output_file.write(line)
            current_file_size += line_size

        if output_file:
            output_file.close()

    print(f"Split into {file_count} files, split size {size_per_file} bytes.")

def file_chunks(file_path, chunk_size=1024 * 1024):
    """read big file,save chunked text into a list
    file_path: file to chunks
    chunk_size: size of each chunk in bytes,e.g. 1024*1024 for 1MB
    """
    # Open the large file
    with open(file_path, "rb") as large_file:
        chunk_list = []
        while True:
            chunk = large_file.read(chunk_size)
            if not chunk:
                break
            # save the chunk to a list
            chunk_list.append(chunk)
        logger.info(
            f"with chunk size {convert_bytes(chunk_size)}, split file into {len(chunk_list)} chunks."
        )
        return chunk_list


def convert_bytes(num_bytes):
    """Convert bytes to a human-readable format."""
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0


def merge_json_files(folder_path, output_file):
    """merge multiple json files into one
    folder_path: path of folder contains multiple json files
    output_file: path of output merged json file
    """
    merged_dict = {"IP": [], "URL": [], "memory": {}}

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                merged_dict["IP"] = list(set(merged_dict["IP"]) | set(data["IP"]))
                merged_dict["URL"] = list(set(merged_dict["URL"]) | set(data["URL"]))
                # todo merge memory dict
                # merged_dict = data.get("memory", {})
                
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_dict, f, ensure_ascii=False)

def merge_new_json_files(folder_path, output_file):
    '''new json file schema:IP and URL are arrays, items are dicts, each item has key "IP"/"URL" and "count"
    for memory, we add the counts and compare the other keys in the dcits
    folder_path: path of folder contains multiple json files
    output_file: path of output merged json file
    '''
    merged_dict = {"IP": [], "URL": [], "memory": []}
    ip_dict = {}
    url_dict = {}
    memory_dict = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                # merge IP and URL
                for ip_entry in data.get("IP", []):
                    if ip_entry["IP"] in ip_dict:                       
                        ip_dict[ip_entry["IP"]] += ip_entry["count"]
                    else:
                        ip_dict[ip_entry["IP"]] = ip_entry["count"]
                for url_entry in data.get("URL", []):
                    if url_entry["URL"] in url_dict:
                        url_dict[url_entry["URL"]] += url_entry["count"]
                    else:
                        url_dict[url_entry["URL"]] = url_entry["count"]
                # @todo merge memory
                
    merged_dict["IP"] = [{"IP": ip, "count": count} for ip, count in ip_dict.items()]
    merged_dict["URL"] = [{"URL": url, "count": count} for url, count in url_dict.items()]
                          
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_dict, f, ensure_ascii=False)


def save_json_file(data, file_path):
    """save data to json file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


if __name__ == "__main__":
    # merge_json_files("result/result_2024-08-13_15-27-27","result/result_2024-08-13_15-27-27/merged_output.json")
    # logger.add("log_file.log")
    # split_file_size("D:\Desktop\Orange stage MFE\orange stage\ServerLog\log-ex\data\Linux.txt", 640*640)

    # chunks = file_chunks("Linux.txt", 512 * 512)
    # logger.info(f"Number of chunks: {len(chunks)}")
    # if chunks:
    #     logger.info(f"Size of the first chunk: {len(chunks[0])} bytes")

    print(convert_bytes(128 * 1024))
    # with open("result/result_2024-08-13_15-27-27/merged.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)
    #     print("number of IPs:", len(data["IP"]))
    #     print("number of urls:", len(data["URL"]))
    #     print("number of memory:",len(data["memory"]))
