# -*- coding: UTF-8 -*-
# @file:    StrStream.py
# @author:  zombie.fml<zombiefml@gmail.com>
# @change:
#   2010-03-19
#   + initial version, can handle most unicode encodings.
#     StringStream supports only ASCIIs.

import cStringIO

class StringStream:
    '''This is a simple wrapper of cStringIO.

    -Supported encodings:
        ANSI, Unicode, Unicode-big-endian, UTF-8, UTF-8 with signature.

    [Note]:
    -Handles only USA-ASCIIs!
    -This class does NOT support files containing multi-byte characters
    e.g. CJK characters. It depends on some dirty tricks! Maybe I will
    rewrite the total class someday, but it depends.
    '''

    def __init__(self, filename):
        '''Read in the whole file and construct a cStringIO object.'''
        try:
            f = open(filename)
            self.s = f.read()
        except IOError:
            self.s = ''
        else:
            f.close()

        self.data = cStringIO.StringIO(self.s)

        # Handle the UTF-8 signature and Unicode BOM
        sig = self.data.read(3)
        self.csize = 1 # How many bytes do we read each time?
        self.little_endian = True
        if sig[:2] in ('\xFF\xFE', '\xFE\xFF'):
            # This file is saved in Unicode
            self.csize = 2
            self.data.seek(2)

            if sig[:2] == '\xFE\xFF': # Big Endian
                self.little_endian = False
        elif sig != '\xEF\xBB\xBF': # This file has no signature
            self.data.seek(0)

    def __del__(self):
        '''Close StringIO object.'''
        self.data.close()


    def GetNextChar(self):
        '''Return the next character in the buffer.

        If EOF is encounted, an empty string(e.g. '') is returned.
        '''
        c = self.data.read(1)
        if self.csize == 2:
            # Skip half of the Unicode character
            # I DO assume the file contains only USA-ASCIIs!
            c1 = self.data.read(1)

        # Make sure the 'a' in 'bool and a or b' is NOT False
        return (self.little_endian and [c] or [c1])[0]


    def UnGetChar(self, offset = -1):
        '''Seek back in the string stream.

        'offset' must be negative.
        Seek back abs(offset) bytes from current position.
        '''
        if offset >= 0:
            return

        pos = self.data.tell() + offset
        if pos < 0:
            return

        self.data.seek(pos)



if __name__ == '__main__':
    import sys
    s = StringStream(sys.argv[1])
    c = s.GetNextChar()
    while c != '':
        sys.stdout.write(c) # The print statement will add a space before c
        c = s.GetNextChar()

