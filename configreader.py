#!/usr/bin/env python3
import yaml
import json
import os
import re
import stat

class ConfigReader:
    def __init__(self, config_file, file_type=None, create_config=False):
        self.yaml_exts = [ 'yaml', 'yml' ]
        self.json_exts = [ 'json' ]
        self.config_file = config_file
        self.config_file_type = self.__get_file_type()
        self.configs = {}
    
        if create_config:
            f = open(config_file, 'w')
            f.close()

        if os.path.isfile(self.config_file) or stat.S_ISFIFO(os.stat(self.config_file).st_mode):
            if self.config_file_type == "yaml" or file_type.lower() in self.yaml_exts:
                with open(self.config_file, 'r') as file:
                    self.configs = yaml.safe_load(file)
            elif self.config_file_type == "json" or file_type.lower() in self.json_exts:
                with open(self.config_file, 'r') as file:
                    self.configs = json.load(file)

            # if config is empty, set to empty dict
            if not self.configs: self.configs = {}
        else:
            raise FileNotFoundError ("Config file not found")

    def __get_file_type(self):
        basename = os.path.basename(self.config_file).lower()
        if re.search("\.({})$".format("|".join(self.yaml_exts)), basename):
            return "yaml"
        elif re.search("\.({})$".format("|".join(self.json_exts)), basename):
            return "json"
        else:
            return None

    def __mask_keywords(self, dictionary, mask_keywords=[], strict_match=False):
        if len(mask_keywords) == 0:
            mask_keywords += ['password', 'passwd', 'pass', 'pwd']

        masked_dict = {}
        for key, value in dictionary.items():
            if isinstance(value, dict):
                masked_dict[key] = self.__mask_keywords(value, mask_keywords, strict_match)
            else:
                is_sensitive = False
                for kw in mask_keywords:
                    if strict_match and kw.lower() == key.lower():
                        is_sensitive = True
                    elif not strict_match and kw.lower() in key.lower():
                        is_sensitive = True

                masked_dict[key] = "__SENSITIVE_DATA__" if is_sensitive else value
        return masked_dict

    def get(self, *keys):
        if len(keys) == 0:
            return self.configs
            
        current_dict = self.configs
        for key in keys[:-1]:
            current_dict = current_dict[key]
        return current_dict[keys[-1]]

    def set(self, *keys, value, override=True):
        current_dict = self.configs
        for key in keys[:-1]:
            try:
                current_dict = current_dict[key]
            except:
                current_dict = current_dict.setdefault(key, {})
        
        # set key if it does not exist
        try:
            current_dict[keys[-1]]
        except:
            current_dict[keys[-1]] = value

        # overwrite value if specified
        if override:
            current_dict[keys[-1]] = value
    
    def setdefault(self, *keys, value):
        self.set(*keys, value=value, override=False)

    def set_env_vars(self, prefix=None):
        def __map_booleans(str):
            true_list = ['on', 'true', 'enable']
            false_list = ['off', 'false', 'disable']
            if str.lower() in true_list:
                return True
            elif str.lower() in false_list:
                return False
            return str

        def __get_set_keys(parent_keys, current_dict):
            envkeys_defined = []
            for key in current_dict:
                if isinstance(current_dict[key], dict):
                    envkeys_defined += __get_set_keys(parent_keys + [key], current_dict[key])
                else:
                    env_keyname = key.upper() if len(parent_keys) == 0 else "__".join(parent_keys + [key]).upper()
                    # prepend with prefix if set
                    env_keyname = "{}_{}".format(prefix.upper(), env_keyname) if prefix else env_keyname
                    try:
                        current_dict[key] = __map_booleans(os.environ[env_keyname])
                        envkeys_defined.append(env_keyname)
                    except KeyError:
                        pass
            return envkeys_defined
        
        return __get_set_keys([], self.configs)

    def print_configs(self, banner_str="", mask_sensitive=True, mask_keywords=[], mask_strict_match=False):
        print_configs = self.configs
        if mask_sensitive:
            print_configs = self.__mask_keywords(self.configs, mask_keywords, strict_match=mask_strict_match)

        if banner_str:
            linelen = 50
            padding_len = int((linelen - len(banner_str)) / 2)
            padding = " " * padding_len
            print ("*" * linelen)
            print ("{}{}{}".format(padding, banner_str, padding))
            print ("*" * linelen)

        if self.config_file_type == "json":
            print (json.dumps(print_configs, indent=4))
        elif self.config_file_type == "yaml":
            print (yaml.dump(print_configs, indent=2))
        else:
            print (yaml.dump(self.configs, indent=2))            
