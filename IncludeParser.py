import clang.cindex
import os
import sys
from subprocess import Popen, PIPE
import re

WIN_LIBCLANG_DLL_PATH = "D:/llvm/rel_32/bin/libclang.dll"
LINUX_LIBCLANG_DLL_PATH = "/usr/lib/llvm-3.8/lib/libclang-3.8.so.1"    

class IncludeParser:
    
    def __init__(self):
        if os.name == "posix":
            libclang_path = LINUX_LIBCLANG_DLL_PATH
        else:
            libclang_path = WIN_LIBCLANG_DLL_PATH
        clang.cindex.Config.set_library_file(libclang_path)
        self.__index = clang.cindex.Index.create()
        
    def get_includes(self, filename, include_dirs):
        
        filedir = os.path.dirname(os.path.abspath(filename))
        
        def list_includes(tu):
            cursor = tu.cursor
            standard = []
            user = []
            
            hfile = open(filename)
            lines = hfile.readlines()
            
            # The displayname of the top level cursor is the filename of the translation unit
            assert(filename == cursor.displayname)
            for child in cursor.get_children():
                if (child.kind == clang.cindex.CursorKind.INCLUSION_DIRECTIVE and
                    child.location.file.name == filename):
                    
                    include = str(child.displayname)
                    
                    linenum = child.location.line - 1
                    assert(len(lines) > linenum)
                    line = lines[linenum]
                    
                    # The libclang Python API is not sophisticated enough to only run the
                    # preprocessor. Original text information in lost
                    reg = re.match(r'#include\s+(<|")' + include, line)
                    assert(reg is not None)
                    
                    if reg.group(1) == "<" and os.path.basename(include) == include:
                        standard.append(include)
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
        
        flags = 0
        flags = flags | clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
        flags = flags | clang.cindex.TranslationUnit.PARSE_INCOMPLETE
        flags = flags | clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD
        
        tu = self.__index.parse(filename, None, None, flags)
        standard, user = list_includes(tu)
        
        return standard + [get_abs(include, include_dirs) for include in user]

if __name__ == "__main__":
    include_parser = IncludeParser()
    for inc in include_parser.get_includes("dummy.cpp", ["/mnt/c/Users/lenno/sandbox", "/usr/include"]):
        print(inc)