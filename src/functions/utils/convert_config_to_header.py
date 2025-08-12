# convert_config_to_header.py
import os


def convert_config_to_header(config):
    header_dict = {}
    api_key = os.getenv("API_KEY")
    config_headers = config.get("header_df")
    for header_item in config_headers:
        auth_value = header_item["Value"].replace("＜API_KEY＞", api_key)
        header_dict[header_item["Property"]] = auth_value
    return header_dict
