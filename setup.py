""" 
@file: setup.py
@author: Christian He
@time: 2017/11/30 
@description: with this script you can generate .exe with py2exe. 
1, Type "python setup.py py2exe" in the command line to generate exe file. 
2, Add mkl_*.dll and libiomp5md.dll into the dist folder.
3, Add config, log and platforms into the dist folder.
Then the main.exe is able to be running in both the WinXP and Win7 OS.

Q&A:
打包时如遇报错“python setup.py py2exe Invalid Syntax (asyncsupport.py, line 22)”
尝试如下：
Looking at what is likely at line 22 on the github package:
async def concat_async(async_gen):
This is making use of the async keyword which was added in python 3.5, however py2exe only supports up to python 3.4. 
Now jinja looks to be extending the python language in some way (perhaps during runtime?) to support this async keyword in 
earlier versions of python. py2exe cannot account for this language extension.

The Fix:
async support was added in jinja2 version 2.9 according to the documentation. So I tried installing an earlier version of jinja (version 2.8) which I downloaded here.
I made a backup of my current jinja installation by moving the contents of %PYTHONHOME%\Lib\site-packages\jinja2 to some other place. 
extract the previously downloaded tar.gz file and install the package via pip:
cd .\Downloads\dist\Jinja2-2.8 # or wherever you extracted jinja2.8
python setup.py install
"""  

from distutils.core import setup  
import py2exe
import glob 
import matplotlib

# Include 'gzip', 'lxml.etree', 'lxml._elementpath' for lxml module, refer to http://www.py2exe.org/index.cgi/WorkingWithVariousPackagesAndModules
opts = {  
    'py2exe': { "includes" : ["gzip", 'lxml.etree', 'lxml._elementpath',
							  "sip",
							  "numpy",
							  "PyQt5.QtGui", 
							  "matplotlib.backends",  "matplotlib.backends.backend_qt5agg",  
                              "matplotlib.figure","matplotlib.pyplot","pylab"],
				## with budle_files equal to 2, the exe file is unable to run normally.
				#"bundle_files": 2
              }  
       } 
 
# Note: for packing Matplotlib with py2exe, refer to http://www.py2exe.org/index.cgi/MatPlotLib
# for the details. 
data_files = matplotlib.get_py2exe_datafiles()
  
# for console program use 'console = [{"script" : "scriptname.py"}]  
setup(windows=[{"script" : "main.py"}], 
	  options=opts, 
	  data_files=data_files)  
