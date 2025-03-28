#!/usr/bin/env python3
# -*- python -*-
#BEGIN_LEGAL
#
#Copyright (c) 2024 Intel Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#END_LEGAL


import sys
import os
from pysrc import genutil

from platform import system
from setuptools import setup, Extension

# Assume mbuild is next to the current source directory
# put mbuild on the import path
# from "path-to-xed/xed2/mfile.py" obtain: "path-to-xed/xed2".

def fatal(m):
    sys.stderr.write("\n\nXED build error: %s\n\n" % (m) )
    sys.exit(1)

def try_mbuild_import():
    try:
        import mbuild
        return True
    except:
        return False

def find_mbuild_import():
    if try_mbuild_import():
        # mbuild is already findable by PYTHONPATH. Nothing required from
        # this function.
        return

    script_name = sys.argv[0]
    mbuild_install_path_derived = \
                   os.path.join(os.path.dirname(script_name), '..', 'mbuild')

    mbuild_install_path_relative = genutil.find_dir('mbuild')
    mbuild_install_path = mbuild_install_path_derived
    if not os.path.exists(mbuild_install_path):
        if not mbuild_install_path_relative:
            # If find_dir() fails, it returns None. That messes
            # up os.path.exists() so we fix it with ''
            mbuild_install_path_relative=''
        mbuild_install_path = mbuild_install_path_relative
        if not os.path.exists(mbuild_install_path):
            s = "mfile.py cannot find the mbuild directory: [%s] or [%s]"
            fatal(s % (mbuild_install_path_derived,
                       mbuild_install_path_relative))

    # modify the environment python path so that the imported modules
    # (enumer,codegen) can find mbuild.

    if 'PYTHONPATH' in os.environ:
        sep = os.pathsep
        os.environ['PYTHONPATH'] =  mbuild_install_path + sep +  \
                                    os.environ['PYTHONPATH']
    else:
        os.environ['PYTHONPATH'] =  mbuild_install_path

    sys.path.insert(0,mbuild_install_path)

def work():
    genutil.check_python_version(3,9)
    try:
        find_mbuild_import()
    except:
        fatal("mbuild import failed")
    import xed_mbuild
    import xed_build_common
    try:
        retval = xed_mbuild.execute()
    except Exception as e:
        xed_build_common.handle_exception_and_die(e)
    return retval

def buildPyModule():
    setup(name='xed',
        version='1.0',
        options={'build':{'build_lib':'.'}},
        script_args=['build'],
        ext_modules=[
            Extension('xed',
                include_dirs = ['obj/wkit/include'],
                library_dirs = ['obj/wkit/lib'],
                libraries = ['xed'],
                define_macros = [('PYTHON', None)],
                sources = ['examples/xed-examples-util.c',
                           'examples/xed-nm-symtab.c',
                           'examples/xed-disas-raw.c',
                           'examples/xed-dot-prep.c',
                           'examples/xed-symbol-table.c',
                           'examples/xed-dot.c',
                           'examples/avltree.c',
                           'examples/xed-disas-elf.c',
                           'examples/xed-disas-macho.c'] +
                           (['examples/xed-disas-pecoff.cpp'] if system() == 'Windows' else [])
            )
        ]
    )

if __name__ == "__main__":
    buildpm = False
    if 'pymodule' in sys.argv:
        buildpm = True
        sys.argv.remove('pymodule')
        sys.argv.append('--extra-flags=-fPIC')

    retval = work()
    if retval:
        sys.exit(retval)

    if buildpm:
        buildPyModule()

