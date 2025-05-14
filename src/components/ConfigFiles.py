# ConfigFiles.py
import os
import glob
import yaml

import streamlit as st

ASSETS_DIR = "assets"
APPEND_DIR = "privates"


class ConfigFiles:
    def __init__(self) -> None:
        self.config_file = []
        # assetsフォルダからyamlファイルを選択
        self.config_files = glob.glob(os.path.join(ASSETS_DIR, "*.yaml"))
        for private_config in glob.glob(os.path.join(APPEND_DIR, "*.yaml")):
            self.config_files.append(private_config)

    def get_config_files_list(self):
        return self.config_files

    def load_config_from_yaml(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def render_config_selector(self):
        return st.selectbox("Select a config file", self.config_files)

    def render_config_viewer(self, config_path, config):
        if "title" in config:
            st.info(f"{config.get('title')}")
        if "note" in config:
            st.warning(f"{config.get('note')}")
        # st.write("##### Config states")
        with st.expander(
            label="##### Config states",
            expanded=False,
            icon="📝",
        ):
            st.code(config_path)
            st.write(config)
