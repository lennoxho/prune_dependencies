import os
import re

class IncludeParser:
    
    def __init__(self, strict=True):
        self.__strict = strict
        
    def get_includes(self, filename, include_dirs, args):
        
        filedir = os.path.dirname(os.path.abspath(filename))
        
        def list_includes(filename):            
            standard = []
            user = []
            hfile = open(filename)

            reg_comp = re.compile(r'^#include\s+(<|")(\S+)(>|")')
            for line in hfile:
                reg = re.match(reg_comp, line)
                if reg is not None:
                    include = reg.group(2).strip()
                    if not self.__strict or reg.group(1) == '<':
                        standard.append(os.path.basename(include))
                    else:
                        user.append(include)

            return standard, user

        def get_abs(include, include_dirs):
            resolved_path = os.path.realpath(include)
            
            if not os.path.isabs(include):            
                for dir in [filedir] + include_dirs:
                    resolved_path = os.path.realpath(os.path.join(dir, include))
                    if os.path.isfile(resolved_path):
                        break

            if not os.path.isfile(resolved_path):
                raise IOError(include + " not found")

            return resolved_path
        
        standard, user = list_includes(filename)
        
        return standard + [get_abs(include, include_dirs) for include in user]

if __name__ == "__main__":
    include_parser = IncludeParser(strict=False)
    for inc in include_parser.get_includes("dummy.cpp", ["/mnt/c/Users/lenno/sandbox", "/usr/include"], []):
        print(inc)