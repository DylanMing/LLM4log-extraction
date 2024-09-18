import re
import os
import json
from loguru import logger


def save_json_file(data, file_path):
    """save dict data to json file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def mkdir(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)


def load_json(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def get_data_dict(data):
    """get data dict with keys: IP(list), URL(list), value is count
    data: data with counts
    e.g. data: {"IP": [{"IP": ip, "count": count},...], "URL": [{"URL": url, "count": count},...]}
    return dict data with keys: IP(dict), URL(dict)
    each dict: key is IP/URL, value is count
    {"IP": {"192.168.1.1": 10, "192.168.1.2": 20}, "URL": {"http://www.baidu.com": 100, "http://www.google.com": 200}}
    """
    ip_dict = {}
    url_dict = {}
    # ip_list = []
    # url_list = []
    # ip_count = []
    # url_count = []

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
    return {"IP": ip_dict, "URL": url_dict}


def get_ipurl_list(result):
    """get ip and url list from count result
    result: data with counts
    e.g. result: {"IP": [{"IP": ip, "count": count},...], "URL": [{"URL": url, "count": count},...]}
    return ip_list, url_list
    """
    ip_list = []
    url_list = []
    for item in result["IP"]:
        ip_list.append(item["IP"])
    for item in result["URL"]:
        url_list.append(item["URL"])
    return ip_list, url_list


def get_bad_case(result_predict, result_standard, count):
    """get miss extracted IPs and URL for predict result from standard result
    
    """
    if count:
        predict_ip_list, predict_url_list = get_ipurl_list(result_predict)
        standard_ip_list, standard_url_list = get_ipurl_list(result_standard)
    else:
        predict_ip_list, predict_url_list = result_predict["IP"], result_predict["URL"]
        standard_ip_list, standard_url_list = result_standard["IP"], result_standard["URL"]
    bad_url = set(predict_url_list) - set(standard_url_list)
    bad_ip = set(predict_ip_list) - set(standard_ip_list)
    return {"IP": list(bad_ip), "URL": list(bad_url)}


def get_miss_case(result_predict, result_standard, count):
    """get bad cased extracted from IPs and URLs for predict result from standard result"""
    
    if count:
        predict_ip_list, predict_url_list = get_ipurl_list(result_predict)
        standard_ip_list, standard_url_list = get_ipurl_list(result_standard)
    else:
        predict_ip_list, predict_url_list = result_predict["IP"], result_predict["URL"]
        standard_ip_list, standard_url_list = result_standard["IP"], result_standard["URL"]
    miss_url = set(standard_url_list) - set(predict_url_list)
    miss_ip = set(standard_ip_list) - set(predict_ip_list)
    return {"IP": list(miss_ip), "URL": list(miss_url)}


def pure_llm(llm_result, count):
    """RE to correct the misclassified IPs and URLs for LLM"""
    if count:
        llm_ip_list, llm_url_list = get_ipurl_list(llm_result)
    else:
        llm_ip_list, llm_url_list = llm_result["IP"], llm_result["URL"]

    pure_llm_result = {"IP": [], "URL": []}
    
    # find url in ip and ip in url
    ip_in_url = []
    url_in_ip = []
    # re for ip in url
    ip_pattern = r'^\b(?:\d{1,3}\.){3}\d{1,3}\b$'
    for i in llm_url_list:
        if re.match(ip_pattern, i):
            ip_in_url.append(i)
    # @todo 62.99.164.82.sh.interxion.inode.at will also be matched as ip

    logger.info(f"nums of IP in URL:{len(ip_in_url)}")
    logger.info(f"IP in url{ip_in_url}")
    # re for url in ip
    url_pattern = r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    # url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    for i in llm_ip_list:
        if re.match(url_pattern, i):
            url_in_ip.append(i)
    logger.info(f"nums of URL in IP:{len(url_in_ip)}")
    logger.info(f"URL in ip{url_in_ip}")
  
    # pure ip and url
    ip_pure = list(set(llm_ip_list) - set(url_in_ip))
    url_pure = list(set(llm_url_list) - set(ip_in_url))
    logger.info(f"nums of pure IP:{len(ip_pure)}")
    logger.info(f"nums of pure URL:{len(url_pure)}")
    # add pure ip and url to pure_llm_result
    new_llm_ip_list = list(set(ip_pure + ip_in_url))
    new_llm_url_list = list(set(url_pure + url_in_ip))
    logger.info(f"new add llm IP{list(set(new_llm_ip_list)-set(llm_ip_list))}")
    logger.info(f"new add llm url{list(set(new_llm_url_list)-set(llm_url_list))}")

    # make new llm_result dict
    if count:
        llm_data_dict = get_data_dict(llm_result)
        for ip in new_llm_ip_list:
            if ip in llm_data_dict["IP"]:
                pure_llm_result["IP"].append({"IP": ip, "count": llm_data_dict["IP"][ip]})
        for url in new_llm_url_list:
            if url in llm_data_dict["URL"]:
                pure_llm_result["URL"].append(
                    {"URL": url, "count": llm_data_dict["URL"][url]}
                )
    else:
        pure_llm_result["IP"] = new_llm_ip_list
        pure_llm_result["URL"] = new_llm_url_list
    return pure_llm_result


def recall_llm(predict_result, standard_result, count):
    """calculate the recall of LLM"""
    if count:
        predict_ip_list, predict_url_list = get_ipurl_list(predict_result)
        standard_ip_list, standard_url_list = get_ipurl_list(standard_result)
    else:
        predict_ip_list, predict_url_list = predict_result["IP"], predict_result["URL"]
        standard_ip_list, standard_url_list = standard_result["IP"], standard_result["URL"]

    recall_ip = len(set(predict_ip_list) & set(standard_ip_list)) / len(
        set(standard_ip_list)
    )

    recall_url = len(set(predict_url_list) & set(standard_url_list)) / len(
        set(standard_url_list)
    )

    return recall_ip, recall_url


def precision_llm(predict_result, standard_result, count):
    """calculate the precision of LLM"""
    if count:
        predict_ip_list, predict_url_list = get_ipurl_list(predict_result)
        standard_ip_list, standard_url_list = get_ipurl_list(standard_result)
    else:
        predict_ip_list, predict_url_list = predict_result["IP"], predict_result["URL"]
        standard_ip_list, standard_url_list = standard_result["IP"], standard_result["URL"]

    precision_ip = len(set(predict_ip_list) & set(standard_ip_list)) / len(
        set(predict_ip_list)
    )
    precision_url = len(set(predict_url_list) & set(standard_url_list)) / len(
        set(predict_url_list)
    )
    return precision_ip, precision_url


def get_wrong_count_case(predict_result, standard_result):
    """get the count of wrong IPs and URL for predict result from standard result"""
    standard_data_dict = get_data_dict(standard_result)
    predict_data_dict = get_data_dict(predict_result)
    wrong_count_case = {"IP": [], "URL": []}
    for ip, count in predict_data_dict["IP"].items():
        if ip in standard_data_dict["IP"]:
            if count != standard_data_dict["IP"][ip]:
                wrong_count_case["IP"].append(
                    {
                        "IP": ip,
                        "wrong_count": count,
                        "standard_count": standard_data_dict["IP"][ip],
                    }
                )

    for url, count in predict_data_dict["URL"].items():
        if url in standard_data_dict["URL"]:
            if count != standard_data_dict["URL"][url]:
                wrong_count_case["URL"].append(
                    {
                        "URL": url,
                        "wrong_count": count,
                        "standard_count": standard_data_dict["URL"][url],
                    }
                )
    return wrong_count_case



def evaluate_result(config):
    """evaluate the result of RE and LLM
    config: edict object
    """
    logger.info("Running in test mode")
    logger.info("loading results")
    llm_result_file = config.test.llm_result_file
    re_result_file = config.test.re_result_file
    human_result_file = config.test.human_result_file
    logger.info(f"llm_result_file: {llm_result_file}")
    logger.info(f"re_result_file: {re_result_file}")
    logger.info(f"human_result_file: {human_result_file}")
    # load json file
    llm_result = load_json(llm_result_file)
    re_result = load_json(re_result_file)
    human_result = load_json(human_result_file)
    logger.info("human resut as standard")

    logger.info("num of ip in human result:{}".format(len(human_result["IP"])))
    logger.info("num of url in human result:{}".format(len(human_result["URL"])))
    logger.info("num of ip in llm result:{}".format(len(llm_result["IP"])))
    logger.info("num of url in llm result:{}".format(len(llm_result["URL"])))

    # miss case
    logger.info("-" * 80)
    # miss case for llm
    miss_case_llm_human = get_miss_case(llm_result, human_result, config.inference.count)
    save_json_file(
        miss_case_llm_human,
        os.path.join(config.save_dir, "miss_case_llm_human.json"),
    )
    logger.info(
        "miss case between llm and human:{},{}".format(
            len(miss_case_llm_human["IP"]), len(miss_case_llm_human["URL"])
        )
    )
    # miss case for re
    miss_case_llm_re = get_miss_case(llm_result, re_result, config.inference.count)
    save_json_file(
        miss_case_llm_re, os.path.join(config.save_dir, "miss_case_llm_re.json")
    )
    logger.info(
        "miss case between llm and re:{},{}".format(
            len(miss_case_llm_re["IP"]), len(miss_case_llm_re["URL"])
        )
    )
    # miss case for re human
    miss_case_re_human = get_miss_case(re_result, human_result, config.inference.count)
    save_json_file(
        miss_case_re_human, os.path.join(config.save_dir, "miss_case_re_human.json")
    )
    logger.info(
        "miss case between re and human:{},{}".format(
            len(miss_case_re_human["IP"]), len(miss_case_re_human["URL"])
        )
    )
    logger.info("-" * 80)

    # pure llm result
    logger.info(
        "exchange missed classify url and ip for result of llm to get pure llm result"
    )
    pure_llm_result = pure_llm(llm_result, config.inference.count)
    save_json_file(
        pure_llm_result, os.path.join(config.save_dir, "pure_llm_result.json")
    )

    logger.info("num of ip in pure_llm_result:{}".format(len(pure_llm_result["IP"])))
    logger.info("num of url in pure_llm_result:{}".format(len(pure_llm_result["URL"])))
    logger.info("-" * 80)
    
    # miss case for pure llm
    miss_case_pure_llm_human = get_miss_case(pure_llm_result, human_result, config.inference.count)
    save_json_file(
        miss_case_pure_llm_human,
        os.path.join(config.save_dir, "miss_case_pure_llm_human.json"),
    )
    logger.info(
        "miss case between pure_llm and human:{},{}".format(
            len(miss_case_pure_llm_human["IP"]),
            len(miss_case_pure_llm_human["URL"]),
        )
    )
    miss_case_pure_llm_re = get_miss_case(pure_llm_result, re_result, config.inference.count)
    save_json_file(
        miss_case_pure_llm_re,
        os.path.join(config.save_dir, "miss_case_pure_llm_re.json"),
    )
    logger.info(
        "miss case between pure_llm and re:{},{}".format(
            len(miss_case_pure_llm_re["IP"]), len(miss_case_pure_llm_re["URL"])
        )
    )

    miss_case_re_human = get_miss_case(re_result, human_result, config.inference.count)
    save_json_file(
        miss_case_re_human, os.path.join(config.save_dir, "miss_case_re_human.json")
    )
    logger.info(
        "miss case between re and human: {},{}".format(
            len(miss_case_re_human["IP"]), len(miss_case_re_human["URL"])
        )
    )

    logger.info("-" * 80)
    
    # bad case
    bad_case_llm_human = get_bad_case(llm_result, human_result, config.inference.count)
    save_json_file(
        bad_case_llm_human, os.path.join(config.save_dir, "bad_case_llm_human.json")
    )
    logger.info(
        "bad case between llm and human:{},{}".format(
            len(bad_case_llm_human["IP"]), len(bad_case_llm_human["URL"])
        )
    )

    bad_case_pure_llm_human = get_bad_case(pure_llm_result, human_result, config.inference.count)
    save_json_file(
        bad_case_pure_llm_human,
        os.path.join(config.save_dir, "bad_case_pure_llm_human.json"),
    )

    logger.info(
        "bad case between pure_llm and human:{},{}".format(
            len(bad_case_pure_llm_human["IP"]), len(bad_case_pure_llm_human["URL"])
        )
    )
    
    bad_case_re_human = get_bad_case(re_result, human_result, config.inference.count)
    save_json_file(
        bad_case_re_human, os.path.join(config.save_dir, "bad_case_re_human.json")
    )
    logger.info(
        "bad case between re and human:{},{}".format(
            len(bad_case_re_human["IP"]), len(bad_case_re_human["URL"])
        )
    )
    
    logger.info("-" * 80)
    # recall and precision of llm and pure_llm

    logger.info("recall of llm{}".format(recall_llm(llm_result, human_result, config.inference.count)))
    logger.info(
        "recall of pure_llm{}".format(recall_llm(pure_llm_result, human_result, config.inference.count))
    )
    logger.info("recall of re{}".format(recall_llm(re_result, human_result, config.inference.count)))

    logger.info("precision of llm{}".format(precision_llm(llm_result, human_result, config.inference.count)))
    logger.info(
        "precision of pure_llm{}".format(precision_llm(pure_llm_result, human_result, config.inference.count))
    )
    logger.info("precision of re{}".format(precision_llm(re_result, human_result, config.inference.count)))

    # get wrong count cases
    if config.inference.count:
        logger.info("-" * 80)
        wrong_count_case = get_wrong_count_case(llm_result, human_result)
        logger.info(
            "num of wrong count IP and url of llm: {},{}".format(
                len(wrong_count_case["IP"]), len(wrong_count_case["URL"])
            )
        )
        save_json_file(
            wrong_count_case,
            os.path.join(config.save_dir, "wrong_count_case.json"),
        )
        wrong_count_ip_rate = len(wrong_count_case["IP"])/len(pure_llm_result["IP"])
        wrong_ip_rate = (len(wrong_count_case["IP"])+len(bad_case_llm_human["IP"]))/len(llm_result["IP"])
        logger.info(f"wrong_count_ip_rate:{wrong_count_ip_rate}")
        logger.info(f"whole wrong_ip_rate:{wrong_ip_rate}")
        
        wrong_count_url_rate = len(wrong_count_case["URL"])/len(pure_llm_result["URL"])
        wrong_url_rate = (len(wrong_count_case["URL"])+len(bad_case_llm_human["URL"]))/len(llm_result["URL"])
        logger.info(f"wrong_count_url_rate:{wrong_count_url_rate}")
        logger.info(f"whole wrong_url_rate:{wrong_url_rate}")
    





def evaluate_result_test(llm_result_file, re_result_file, human_result_file, save_dir):
    """evaluate the result of RE and LLM
    config: edict object
    """
    logger.info("Running in test mode")
    logger.info("loading results")
    logger.info(f"llm_result_file: {llm_result_file}")
    logger.info(f"re_result_file: {re_result_file}")
    logger.info(f"human_result_file: {human_result_file}")
    # load json file
    llm_result = load_json(llm_result_file)
    re_result = load_json(re_result_file)
    human_result = load_json(human_result_file)
    logger.info("human resut as standard")
    logger.info("num of ip in human result:{}".format(len(human_result["IP"])))
    logger.info("num of url in human result:{}".format(len(human_result["URL"])))
    logger.info("num of ip in llm result:{}".format(len(llm_result["IP"])))
    logger.info("num of url in llm result:{}".format(len(llm_result["URL"])))

    # miss case
    logger.info("-" * 80)
    miss_case_llm_human = get_miss_case(llm_result, human_result)
    save_json_file(
        miss_case_llm_human,
        os.path.join(save_dir, "miss_case_llm_human.json"),
    )
    logger.info(
        "miss case between llm and human:{},{}".format(
            len(miss_case_llm_human["IP"]), len(miss_case_llm_human["URL"])
        )
    )
    miss_case_llm_re = get_miss_case(llm_result, re_result)
    save_json_file(miss_case_llm_re, os.path.join(save_dir, "miss_case_llm_re.json"))
    logger.info(
        "miss case between llm and re:{},{}".format(
            len(miss_case_llm_re["IP"]), len(miss_case_llm_re["URL"])
        )
    )

    miss_case_re_human = get_miss_case(re_result, human_result)
    save_json_file(
        miss_case_re_human, os.path.join(save_dir, "miss_case_re_human.json")
    )
    logger.info(
        "miss case between re and human:{},{}".format(
            len(miss_case_re_human["IP"]), len(miss_case_re_human["URL"])
        )
    )
    logger.info("-" * 80)
    # pure llm result

    logger.info(
        "exchange missed classify url and ip for result of llm to get pure llm result"
    )
    pure_llm_result = pure_llm(llm_result)
    save_json_file(pure_llm_result, os.path.join(save_dir, "pure_llm_result.json"))

    logger.info("num of ip in pure_llm_result:{}".format(len(pure_llm_result["IP"])))
    logger.info("num of url in pure_llm_result:{}".format(len(pure_llm_result["URL"])))
    logger.info("-" * 80)
    # miss case for pure llm
    miss_case_pure_llm_human = get_miss_case(pure_llm_result, human_result)
    save_json_file(
        miss_case_pure_llm_human,
        os.path.join(save_dir, "miss_case_pure_llm_human.json"),
    )
    logger.info(
        "miss case between pure_llm and human:{},{}".format(
            len(miss_case_pure_llm_human["IP"]),
            len(miss_case_pure_llm_human["URL"]),
        )
    )
    miss_case_pure_llm_re = get_miss_case(pure_llm_result, re_result)
    save_json_file(
        miss_case_pure_llm_re,
        os.path.join(save_dir, "miss_case_pure_llm_re.json"),
    )
    logger.info(
        "miss case between pure_llm and re:{},{}".format(
            len(miss_case_pure_llm_re["IP"]), len(miss_case_pure_llm_re["URL"])
        )
    )

    miss_case_re_human = get_miss_case(re_result, human_result)
    save_json_file(
        miss_case_re_human, os.path.join(save_dir, "miss_case_re_human.json")
    )
    logger.info(
        "miss case between re and human: {},{}".format(
            len(miss_case_re_human["IP"]), len(miss_case_re_human["URL"])
        )
    )

    logger.info("-" * 80)
    # bad case
    bad_case_llm_human = get_bad_case(llm_result, human_result)
    save_json_file(
        bad_case_llm_human, os.path.join(save_dir, "bad_case_llm_human.json")
    )
    logger.info(
        "bad case between llm and human:{},{}".format(
            len(bad_case_llm_human["IP"]), len(bad_case_llm_human["URL"])
        )
    )

    bad_case_pure_llm_human = get_bad_case(pure_llm_result, human_result)
    save_json_file(
        bad_case_pure_llm_human,
        os.path.join(save_dir, "bad_case_pure_llm_human.json"),
    )
    logger.info(
        "bad case between pure_llm and human:{},{}".format(
            len(bad_case_pure_llm_human["IP"]), len(bad_case_pure_llm_human["URL"])
        )
    )
    logger.info("-" * 80)
    # recall and precision of llm and pure_llm

    logger.info("recall of llm{}".format(recall_llm(llm_result, human_result)))
    logger.info(
        "recall of pure_llm{}".format(recall_llm(pure_llm_result, human_result))
    )
    logger.info("recall of re{}".format(recall_llm(re_result, human_result)))

    logger.info("precision of llm{}".format(precision_llm(llm_result, human_result)))
    logger.info(
        "precision of pure_llm{}".format(precision_llm(pure_llm_result, human_result))
    )
    logger.info("precision of re{}".format(precision_llm(re_result, human_result)))


if __name__ == "__main__":
    save_dir = "test"
    # text_re = read_log_file("data\Linux.txt")
    # re_result = extract_re(text_re, save_dir)
    re_result = "data/result-re_Linux.json"
    predict_result = "result/result_2024-09-10_17-13-04_all file 192k-12 only extraction/inference_output/merged.json"
    human_result = "result/human_evaluation.json"

    evaluate_result_test(predict_result, re_result, human_result, save_dir)
