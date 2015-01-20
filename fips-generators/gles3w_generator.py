"""
NOTE: this script has copied code from gles3w/gles3w_gen.py because the
original script doesn't expose functions which can be called from here.
It would be better to keep this gles3w_generator.py small by importing
gles3w/gles3w_gen.py and calling into there via functions.
"""


Version = 4 

import genutil as util
import re
import os
import urllib2

#-------------------------------------------------------------------------------
def parseProcs(rootPath) :
    # download gl3.h file
    gl3Path = rootPath + 'gl3.h'
    if not os.path.exists(gl3Path) :
        web = urllib2.urlopen('https://www.khronos.org/registry/gles/api/GLES3/gl3.h')
        with open(gl3Path, 'wb') as f :
            f.writelines(web.readlines())

    gl3platformPath = rootPath + 'gl3platform.h'
    if not os.path.exists(gl3platformPath) :
        web = urllib2.urlopen('https://www.khronos.org/registry/gles/api/GLES3/gl3platform.h')
        with open(gl3Path, 'wb') as f :
            f.writelines(web.readlines())

    khrPath = rootPath + '../KHR/'
    khrplatformPath = khrPath + 'khrplatform.h'
    if not os.path.exists(khrplatformPath) :
        web = urllib2.urlopen('https://www.khronos.org/registry/egl/api/KHR/khrplatform.h')
        with open(khrplatformPath, 'wb') as f :
            f.writelines(web.readlines())

    # parse function names gl3.h
    procs = []
    p = re.compile(r'GL_APICALL\s+(.*)GL_APIENTRY\s+(\w+)\s+(.*);')
    with open(gl3Path, 'r') as f:
        for line in f :
            m = p.match(line)
            if m :
                a = m.group(1), m.group(2), m.group(3)
                procs.append(a)
    return procs

#-------------------------------------------------------------------------------
def proc_t(proc) :
    return { 'p': proc[1],
             'p_a': proc[2],
             'p_r': proc[0],
             'p_s': 'gles3w' + proc[1][2:],
             'p_t': 'PFN' + proc[1].upper() + 'PROC' }

#-------------------------------------------------------------------------------
def generateHeader(hdrPath, rootPath) :
    
    # parse procs from gl3.h
    procs = parseProcs(rootPath)
    
    # generate gl3w.h
    with open(hdrPath, 'wb') as f :
        f.write("// #version:{}#\n".format(Version))
        f.write(r'''#ifndef __gles3w_h_
#define __gles3w_h_
#include <GLES3/gl3.h>
#ifdef __cplusplus
extern "C" {
#endif
/* OpenGL|ES functions */
''')
    
        for proc in procs :
            pt = proc_t(proc)
            f.write('typedef %(p_r)s(GL_APIENTRY* %(p_t)s) %(p_a)s;\n' % pt)
            f.write('extern %(p_t)s %(p_s)s;\n' % pt)
        f.write('\n')
        for proc in procs :
            f.write('#define %(p)-40s %(p_s)s\n' % proc_t(proc))
        f.write(r'''
extern void gles3wInit();
#ifdef __cplusplus
}
#endif

#endif
''')

#-------------------------------------------------------------------------------
def generateSource(srcPath, rootPath) :
    
    # parse procs from gl3.h
    procs = parseProcs(rootPath)

    with open(srcPath, 'wb') as f :
        f.write('// #version:{}#\n'.format(Version))
        f.write('''
#include "gles3w.h"

#ifdef __cplusplus
extern "C" {
#endif
''')

        for proc in procs :
            f.write('%(p_t)-44s %(p_s)s;\n' % proc_t(proc))
        f.write(r'''
void gles3Init()
{
''')
        for proc in procs:
            f.write('    %(p_s)-41s = (%(p_t)s) GLES3W_IMPLEMENTATION("%(p)s");\n' % proc_t(proc))
        f.write(r'''}
#ifdef __cplusplus
}
#endif
''')

#-------------------------------------------------------------------------------
def generate(directory, name) :
    print("GENERATING GLES3W")
    selfPath = directory + name + '.py'
    hdrPath  = directory + name + '.h'
    srcPath  = directory + name + '.cc'
    if util.isDirty([selfPath], Version, hdrPath, srcPath) :
        # need to re-generate source files
        generateHeader(hdrPath, directory)
        generateSource(srcPath, directory)
    else :
        # all uptodate
        pass

