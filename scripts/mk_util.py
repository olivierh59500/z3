############################################
# Copyright (c) 2012 Microsoft Corporation
# 
# Auxiliary scripts for generating Makefiles 
# and Visual Studio project files.
#
# Author: Leonardo de Moura (leonardo)
############################################
import os
import glob
import re
import getopt
import sys
import shutil
from mk_exception import *

BUILD_DIR='build'
REV_BUILD_DIR='..'
SRC_DIR='src'
IS_WINDOW=False
VERBOSE=False
DEBUG_MODE=False
SHOW_CPPS = True
VS_X64 = False
ONLY_MAKEFILES = False

if os.name == 'nt':
    IS_WINDOW=True
    # Visual Studio already displays the files being compiled
    SHOW_CPPS=False

def display_help():
    print "mk_make.py: Z3 Makefile generator\n"
    print "This script generates the Makefile for the Z3 theorem prover."
    print "It must be executed from the Z3 root directory."
    print "\nOptions:"
    print "  -h, --help                    display this message."
    print "  -v, --verbose                 be verbose."
    print "  -b <sudir>, --build=<subdir>  subdirectory where Z3 will be built (default: build)."
    print "  -d, --debug                   compile Z3 in debug mode."
    print "  -x, --x64                     create 64 binary when using Visual Studio."
    print "  -m, --makefiles               generate only makefiles."
    exit(0)

# Parse configuration option for mk_make script
def parse_options():
    global VERBOSE, DEBUG_MODE, IS_WINDOW, VS_X64, ONLY_MAKEFILES
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'b:dvxhm', ['build=', 
                                                                    'debug',
                                                                    'verbose',
                                                                    'x64',
                                                                    'help',
                                                                    'makefiles'
                                                                     ])
    for opt, arg in options:
        if opt in ('-b', '--build'):
            if arg == 'src':
                raise MKException('The src directory should not be used to host the Makefile')
            set_build_dir(arg)
        elif opt in ('-v', '--verbose'):
            VERBOSE = True
        elif opt in ('-d', '--debug'):
            DEBUG_MODE = True
        elif opt in ('-x', '--x64'):
            if not IS_WINDOW:
                raise MKException('x64 compilation mode can only be specified when using Visual Studio')
            VS_X64 = True
        elif opt in ('-h', '--help'):
            display_help()
        elif opt in ('-m', '--onlymakefiles'):
            ONLY_MAKEFILES = True
        else:
            raise MKException("Invalid command line option '%s'" % opt)

# Return a list containing a file names included using '#include' in
# the given C/C++ file named fname.
def extract_c_includes(fname):
    result = []
    # We look for well behaved #include directives
    std_inc_pat     = re.compile("[ \t]*#include[ \t]*\"(.*)\"[ \t]*")
    system_inc_pat  = re.compile("[ \t]*#include[ \t]*\<.*\>[ \t]*")
    # We should generate and error for any occurrence of #include that does not match the previous pattern.
    non_std_inc_pat = re.compile(".*#include.*")
    
    f = open(fname, 'r')
    linenum = 1
    for line in f:
        m1 = std_inc_pat.match(line)
        if m1:
            result.append(m1.group(1))
        elif not system_inc_pat.match(line) and non_std_inc_pat.match(line):
            raise MKException("Invalid #include directive at '%s':%s" % (fname, line))
        linenum = linenum + 1
    return result


# Given a path dir1/subdir2/subdir3 returns ../../..
def reverse_path(p):
    l = p.split('/')
    n = len(l)
    r = '..'
    for i in range(1, n):
        r = '%s/%s' % (r, '..')
    return r

def mk_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def set_build_dir(d):
    global BUILD_DIR, REV_BUILD_DIR
    BUILD_DIR = d
    REV_BUILD_DIR = reverse_path(d)

_UNIQ_ID = 0

def mk_fresh_name(prefix):
    global _UNIQ_ID
    r = '%s_%s' % (prefix, _UNIQ_ID)
    _UNIQ_ID = _UNIQ_ID + 1
    return r

_Id = 0
_Components = []
_ComponentNames = set()
_Name2Component = {}
_Processed_Headers = set()

def get_cpp_files(path):
    return filter(lambda f: f.endswith('.cpp'), os.listdir(path))

def find_all_deps(name, deps):
    new_deps = []
    for dep in deps:
        if dep in _ComponentNames:
            if not (dep in new_deps):
                new_deps.append(dep)
            for dep_dep in _Name2Component[dep].deps:
                if not (dep_dep in new_deps):
                    new_deps.append(dep_dep)
        else:
            raise MKException("Unknown component '%s' at '%s'." % (dep, name))
    return new_deps

class Component:
    def __init__(self, name, path, deps):
        global BUILD_DIR, SRC_DIR, REV_BUILD_DIR
        if name in _ComponentNames:
            raise MKException("Component '%s' was already defined." % name)
        if path == None:
            path = name
        self.name = name
        self.path = path
        self.deps = find_all_deps(name, deps)
        self.build_dir = path
        self.src_dir   = '%s/%s' % (SRC_DIR, path)
        self.to_src_dir = '%s/%s' % (REV_BUILD_DIR, self.src_dir)

    # Find fname in the include paths for the given component.
    # ownerfile is only used for creating error messages.
    # That is, we were looking for fname when processing ownerfile
    def find_file(self, fname, ownerfile):
        global _Name2Component
        full_fname = '%s/%s' % (self.src_dir, fname)
        if os.path.exists(full_fname):
            return self
        for dep in self.deps:
            c_dep = _Name2Component[dep]
            full_fname = '%s/%s' % (c_dep.src_dir, fname)
            if os.path.exists(full_fname):
                return c_dep
        raise MKException("Failed to find include file '%s' for '%s' when processing '%s'." % (fname, ownerfile, self.name))

    # Display all dependencies of file basename located in the given component directory.
    # The result is displayed at out
    def add_cpp_h_deps(self, out, basename):
        includes = extract_c_includes('%s/%s' % (self.src_dir, basename))
        out.write('%s/%s' % (self.to_src_dir, basename))
        for include in includes:
            owner = self.find_file(include, basename)
            out.write(' %s/%s.node' % (owner.build_dir, include))

    # Add a rule for each #include directive in the file basename located at the current component.
    def add_rule_for_each_include(self, out, basename):
        fullname = '%s/%s' % (self.src_dir, basename)
        includes = extract_c_includes(fullname)
        for include in includes:
            owner = self.find_file(include, fullname)
            owner.add_h_rule(out, include)

    # Display a Makefile rule for an include file located in the given component directory.
    # 'include' is something of the form: ast.h, polynomial.h
    # The rule displayed at out is of the form
    #     ast/ast_pp.h.node : ../src/util/ast_pp.h util/util.h.node ast/ast.h.node
    #       @echo "done" > ast/ast_pp.h.node
    def add_h_rule(self, out, include):
        include_src_path   = '%s/%s' % (self.to_src_dir, include)
        if include_src_path in _Processed_Headers:
            return
        _Processed_Headers.add(include_src_path)
        self.add_rule_for_each_include(out, include)
        include_node = '%s/%s.node' % (self.build_dir, include)
        out.write('%s: ' % include_node)
        self.add_cpp_h_deps(out, include)              
        out.write('\n')
        out.write('\t@echo done > %s\n' % include_node)

    def add_cpp_rules(self, out, include_defs, cppfile):
        self.add_rule_for_each_include(out, cppfile)
        objfile = '%s/%s$(OBJ_EXT)' % (self.build_dir, os.path.splitext(cppfile)[0])
        srcfile = '%s/%s' % (self.to_src_dir, cppfile)
        out.write('%s: ' % objfile)
        self.add_cpp_h_deps(out, cppfile)
        out.write('\n')
        if SHOW_CPPS:
            out.write('\t@echo %s/%s\n' % (self.src_dir, cppfile))
        out.write('\t@$(CXX) $(CXXFLAGS) $(%s) $(CXX_OUT_FLAG)%s %s\n' % (include_defs, objfile, srcfile))

    def mk_makefile(self, out):
        include_defs = mk_fresh_name('includes')
        out.write('%s =' % include_defs)
        for dep in self.deps:
            out.write(' -I%s' % _Name2Component[dep].to_src_dir)
        out.write('\n')
        mk_dir('%s/%s' % (BUILD_DIR, self.build_dir))
        for cppfile in get_cpp_files(self.src_dir):
            self.add_cpp_rules(out, include_defs, cppfile)

    # Return true if the component should be included in the all: rule
    def main_component(self):
        return False

    # Return true if the component contains an AssemblyInfo.cs file that needs to be updated.
    def has_assembly_info(self):
        return False

class LibComponent(Component):
    def __init__(self, name, path, deps):
        Component.__init__(self, name, path, deps)

    def mk_makefile(self, out):
        Component.mk_makefile(self, out)
        # generate rule for lib
        objs = []
        for cppfile in get_cpp_files(self.src_dir):
            objfile = '%s/%s$(OBJ_EXT)' % (self.build_dir, os.path.splitext(cppfile)[0])
            objs.append(objfile)

        libfile = '%s/%s$(LIB_EXT)' % (self.build_dir, self.name)
        out.write('%s:' % libfile)
        for obj in objs:
            out.write(' ')
            out.write(obj)
        out.write('\n')
        out.write('\t@$(AR) $(AR_FLAGS) $(AR_OUTFLAG)%s' % libfile)
        for obj in objs:
            out.write(' ')
            out.write(obj)
        out.write('\n')
        out.write('%s: %s\n\n' % (self.name, libfile))

# Auxiliary function for sort_components
def comp_components(c1, c2):
    id1 = _Name2Component[c1].id
    id2 = _Name2Component[c2].id
    return id2 - id1

# Sort components based on (reverse) definition time
def sort_components(cnames):
    return sorted(cnames, cmp=comp_components)

class ExeComponent(Component):
    def __init__(self, name, exe_name, path, deps):
        Component.__init__(self, name, path, deps)
        if exe_name == None:
            exe_name = name
        self.exe_name = exe_name

    def mk_makefile(self, out):
        global _Name2Component
        Component.mk_makefile(self, out)
        # generate rule for exe

        exefile = '%s$(EXE_EXT)' % self.exe_name
        out.write('%s:' % exefile)
        deps = sort_components(self.deps)
        objs = []
        for cppfile in get_cpp_files(self.src_dir):
            objfile = '%s/%s$(OBJ_EXT)' % (self.build_dir, os.path.splitext(cppfile)[0])
            objs.append(objfile)
        for obj in objs:
            out.write(' ')
            out.write(obj)
        for dep in deps:
            c_dep = _Name2Component[dep]
            out.write(' %s/%s$(LIB_EXT)' % (c_dep.build_dir, c_dep.name))
        out.write('\n')
        out.write('\t$(LINK) $(LINK_OUT_FLAG)%s $(LINK_FLAGS)' % exefile)
        for obj in objs:
            out.write(' ')
            out.write(obj)
        for dep in deps:
            c_dep = _Name2Component[dep]
            out.write(' %s/%s$(LIB_EXT)' % (c_dep.build_dir, c_dep.name))
        out.write(' $(LINK_EXTRA_FLAGS)\n')
        out.write('%s: %s\n\n' % (self.name, exefile))

    # All executables are included in the all: rule
    def main_component(self):
        return True

class DLLComponent(Component):
    def __init__(self, name, dll_name, path, deps):
        Component.__init__(self, name, path, deps)
        if dll_name == None:
            dll_name = name
        self.dll_name = dll_name

    def mk_makefile(self, out):
        global _Name2Component
        Component.mk_makefile(self, out)
        # generate rule for (SO_EXT)
        if IS_WINDOW:
            dllfile = '%s$(SO_EXT)' % self.dll_name
        else:
            dllfile = 'lib%s$(SO_EXT)' % self.dll_name
        out.write('%s:' % dllfile)
        deps = sort_components(self.deps)
        objs = []
        for cppfile in get_cpp_files(self.src_dir):
            objfile = '%s/%s$(OBJ_EXT)' % (self.build_dir, os.path.splitext(cppfile)[0])
            objs.append(objfile)
        for obj in objs:
            out.write(' ')
            out.write(obj)
        for dep in deps:
            c_dep = _Name2Component[dep]
            out.write(' %s/%s$(LIB_EXT)' % (c_dep.build_dir, c_dep.name))
        out.write('\n')
        out.write('\t$(LINK) $(SLINK_OUT_FLAG)%s $(SLINK_FLAGS)' % dllfile)
        for obj in objs:
            out.write(' ')
            out.write(obj)
        for dep in deps:
            c_dep = _Name2Component[dep]
            out.write(' %s/%s$(LIB_EXT)' % (c_dep.build_dir, c_dep.name))
        out.write(' $(SLINK_EXTRA_FLAGS)')
        if IS_WINDOW:
            out.write(' /DEF:%s/%s.def' % (self.to_src_dir, self.name))
        out.write('\n')
        out.write('%s: %s\n\n' % (self.name, dllfile))

    # All DLLs are included in the all: rule
    def main_component(self):
        return True

class DotNetDLLComponent(Component):
    def __init__(self, name, dll_name, path, deps, assembly_info_dir):
        Component.__init__(self, name, path, deps)
        if dll_name == None:
            dll_name = name
        if assembly_info_dir == None:
            assembly_info_dir = "."
        self.dll_name          = dll_name
        self.assembly_info_dir = assembly_info_dir 

    def mk_makefile(self, out):
        if IS_WINDOW:
            # TODO
            return
    
    def main_component(self):
        return IS_WINDOW

    def has_assembly_info(self):
        return True
    

def reg_component(name, c):
    global _Id, _Components, _ComponentNames, _Name2Component
    c.id = _Id
    _Id = _Id + 1
    _Components.append(c)
    _ComponentNames.add(name)
    _Name2Component[name] = c
    if VERBOSE:
        print "Processed '%s'" % name

def add_lib(name, deps=[], path=None):
    c = LibComponent(name, path, deps)
    reg_component(name, c)

def add_exe(name, deps=[], path=None, exe_name=None):
    c = ExeComponent(name, exe_name, path, deps)
    reg_component(name, c)

def add_dll(name, deps=[], path=None, dll_name=None):
    c = DLLComponent(name, dll_name, path, deps)
    reg_component(name, c)

def add_dot_net_dll(name, deps=[], path=None, dll_name=None, assembly_info_dir=None):
    c = DotNetDLLComponent(name, dll_name, path, deps, assembly_info_dir)
    reg_component(name, c)

# Copy configuration correct file to BUILD_DIR
def cp_config_mk():
    if IS_WINDOW:
        if VS_X64:
            # TODO
            return
        else:
            if DEBUG_MODE:
                shutil.copyfile('scripts/config-vs-debug.mk', '%s/config.mk' % BUILD_DIR)
            else:
                shutil.copyfile('scripts/config-vs-release.mk', '%s/config.mk' % BUILD_DIR)
    else:
        if DEBUG_MODE:
            shutil.copyfile('scripts/config-debug.mk', '%s/config.mk' % BUILD_DIR)
        else:
            shutil.copyfile('scripts/config-release.mk', '%s/config.mk' % BUILD_DIR)

# Generate the Z3 makefile
def mk_makefile():
    mk_dir(BUILD_DIR)
    cp_config_mk()
    if VERBOSE:
        print "Writing %s/Makefile" % BUILD_DIR
    out = open('%s/Makefile' % BUILD_DIR, 'w')
    out.write('# Automatically generated file. Generator: scripts/mk_make.py\n')
    out.write('include config.mk\n')
    # Generate :all rule
    out.write('all:')
    for c in _Components:
        if c.main_component():
            out.write(' %s' % c.name)
    out.write('\n\n')
    # Generate components
    for c in _Components:
        c.mk_makefile(out)
    # Finalize
    if VERBOSE:
        print "Makefile was successfully generated."
        if DEBUG_MODE:
            print "  compilation mode: Debug"
        else:
            print "  compilation mode: Release"
        if IS_WINDOW:
            print "Type 'cd %s && nmake to build Z3" % BUILD_DIR
        else:
            print "Type 'cd %s; make' to build Z3" % BUILD_DIR
        
# Generate automatically generated source code
def mk_auto_src():
    if not ONLY_MAKEFILES:
        mk_pat_db()

# TODO: delete after src/ast/pattern/expr_pattern_match
# database.smt ==> database.h
def mk_pat_db():
    c = _Name2Component['pattern']
    fin  = open('%s/database.smt2' % c.src_dir, 'r')
    fout = open('%s/database.h'  % c.src_dir, 'w')
    fout.write('char const * g_pattern_database =\n')
    for line in fin:
        fout.write('"%s\\n"\n' % line.strip('\n'))
    fout.write(';\n')    
    if VERBOSE:
        print "Generated '%s/database.h'" % c.src_dir

# Update version numbers
def update_version(major, minor, build, revision):
    if not ONLY_MAKEFILES:
        mk_version_dot_h(major, minor, build, revision)
        update_all_assembly_infos(major, minor, build, revision)
        
# Update files with the version number
def mk_version_dot_h(major, minor, build, revision):
    c = _Name2Component['util']
    fout = open('%s/version.h' % c.src_dir, 'w')
    fout.write('// automatically generated file.\n')
    fout.write('#define Z3_MAJOR_VERSION   %s\n' % major)
    fout.write('#define Z3_MINOR_VERSION   %s\n' % minor)
    fout.write('#define Z3_BUILD_NUMBER    %s\n' % build)
    fout.write('#define Z3_REVISION_NUMBER %s\n' % revision)
    if VERBOSE:
        print "Generated '%s/version.h'" % c.src_dir

# Update version number in AssemblyInfo.cs files
def update_all_assembly_infos(major, minor, build, revision):
    for c in _Components:
        if c.has_assembly_info():
            assembly = '%s/%s/AssemblyInfo.cs' % (c.src_dir, c.assembly_info_dir)
            if os.path.exists(assembly):
                # It is a CS file
                update_assembly_info_version(assembly,
                                             major, minor, build, revision, False)
            else:
                assembly = '%s/%s/AssemblyInfo.cpp' % (c.src_dir, c.assembly_info_dir)
                if os.path.exists(assembly):
                    # It is a cpp file
                    update_assembly_info_version(assembly,
                                                 major, minor, build, revision, True)
                else:
                    raise MKException("Failed to find assembly info file at '%s/%s'" % (c.src_dir, c.assembly_info_dir))
                    
                
# Update version number in the given AssemblyInfo.cs files
def update_assembly_info_version(assemblyinfo, major, minor, build, revision, is_cpp=False):
    if is_cpp:
        ver_pat   = re.compile('[assembly:AssemblyVersionAttribute\("[\.\d]*"\) *')
        fver_pat  = re.compile('[assembly:AssemblyFileVersionAttribute\("[\.\d]*"\) *')
    else:
        ver_pat   = re.compile('[assembly: AssemblyVersion\("[\.\d]*"\) *')
        fver_pat  = re.compile('[assembly: AssemblyFileVersion\("[\.\d]*"\) *')
    fin  = open(assemblyinfo, 'r')
    tmp  = '%s.new' % assemblyinfo
    fout = open(tmp, 'w')
    num_updates = 0
    for line in fin:
        if ver_pat.match(line):
            if is_cpp:
                fout.write('[assembly:AssemblyVersionAttribute("%s.%s.%s.%s")];\n' % (major, minor, build, revision))
            else:
                fout.write('[assembly: AssemblyVersion("%s.%s.%s.%s")]\n' % (major, minor, build, revision))
            num_updates = num_updates + 1
        elif fver_pat.match(line):
            if is_cpp:
                fout.write('[assembly:AssemblyFileVersionAttribute("%s.%s.%s.%s")];\n' % (major, minor, build, revision))
            else:
                fout.write('[assembly: AssemblyFileVersion("%s.%s.%s.%s")]\n' % (major, minor, build, revision))
            num_updates = num_updates + 1
        else:
            fout.write(line)
    if VERBOSE:
        print "%s version numbers updated at '%s'" % (num_updates, assemblyinfo)
    assert num_updates == 2, "unexpected number of version number updates"
    fin.close()
    fout.close()
    shutil.move(tmp, assemblyinfo)
    if VERBOSE:
        print "Updated %s" % assemblyinfo