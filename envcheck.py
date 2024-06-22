import os
import readline
import sys
import maskpass

class EnvCheck:
    def __init__(self, required_env_vars=[], sensitive_env_vars=[]):
        self.required_env_vars = required_env_vars
        self.sensitive_env_vars = sensitive_env_vars

    def verify_required_env_vars(self, input_prompt=True):
        missing_vars = []
        for i in self.required_env_vars:
            try:
                os.environ[i]
            except KeyError:
                if input_prompt:
                    prompt = "{}: ".format(i)
                    os.environ[i] = maskpass.askpass(prompt=prompt) if i in self.sensitive_env_vars else input(prompt)
                missing_vars.append(i)

        has_missing = True if missing_vars else False
        return {
            "has_missing": has_missing,
            "missing_vars": missing_vars
        }

    def print_export_cmds(self, header_str="", header_banner_char="*", mask_sensitive=True):
        if header_str:
            padding = 5
            print (header_banner_char*(len(header_str)+padding))
            print (" "*int(padding/2) + header_str)
            print (header_banner_char*(len(header_str)+padding))

        print ("set +o history;\n")
        for i in self.required_env_vars:
            try:
                v = os.environ[i]
                if i in self.sensitive_env_vars and mask_sensitive:
                    v = "*"*8
            except KeyError:
                v = "<ENTER VALUE HERE>"
            print ("export {}='{}';".format(i, v))
        print ("set -o history;")