# Requires wxPython.  This sample demonstrates:
#
# - single file exe using wxPython as GUI.

from distutils.core import setup
import py2exe
import sys
from glob import glob

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "0.6.1"
        self.company_name = "zombie.fml<zombiefml@gmail.com>"
        self.copyright = "Copyright(C) 2010 zombie.fml"
        self.name = "LuaLex"

################################################################
# A program using wxPython

# The manifest will be inserted as resource into test_wx.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# test_wx.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
	</dependentAssembly>
</dependency>
<dependency>
	<dependentAssembly>
		<assemblyIdentity
			type="win32"
			name="Microsoft.VC90.CRT"
			version="9.0.21022.8"
			processorArchitecture="x86"
			publicKeyToken="1fc8b3b9a1e18e3b"
			language="*"
		/>
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

LuaLex = Target(
    # used for the versioninfo resource
    description = "A sample Lua lexical parser",

    # what to build
    script = "LexApp.pyw",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="LuaLex"))],
	icon_resources = [(112, "res/app.ico"), (112, "res/app_big.ico")],
    dest_base = "LuaLex")

################################################################

setup(
    options = {"py2exe": {"compressed": 1,
                          "optimize": 2,
                          "ascii": 1,
                          "bundle_files": 1}},
    zipfile = 'lib/shared.zip',
    data_files = [("data", glob(r"*.lua")),
		("res", glob(r"res/*.*")),
		("Microsoft.VC90.CRT", glob(r"Microsoft.VC90.CRT\*.*"))],
    windows = [LuaLex],
    )
