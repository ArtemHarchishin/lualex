# -*- coding: UTF-8 -*-
# @file:     LuaLexParser.py
# @author:   zombie.fml<zombiefml@gmail.com>
# @change:
#   2010-03-20
#   + initial version, supports most of Lua 5.1 lexical conventions.


from StrStream import StringStream
import string
import types

class LuaLexParser:
    '''A Lua lexical parser written in Python.

    This class implements a lexical parser compatiable with Lua 5.1.
    '''

    # Keywords
    KEYWORDS = ('and', 'break', 'do', 'else', 'elseif','end', 'false',
                'for', 'function', 'if', 'in', 'local', 'nil', 'not',
                'or', 'repeat','return', 'then', 'true', 'until', 'while')

    # Operators
    # '...', '..' is handled specially
    OPS = ('+', '-', '*', '/', '^', '%', '<', '<=', '>', '>=', '==',
          '~=', '#', '=', '...', '..')

    # Delimiters
    # '.' is handled specially
    DELIMITERS = ('(', ')', '[', ']', '{', '}', ',', ';', ':', '.')

    # Error messages
    MSGS = ('Malformed number',
            'Unexpected symbol',
            'Unfinished line string',
            'Unfinished block comment',
            'Unfinished block string')

    # Token types
    TOKENTYPE = ('KEYWORDS', 'OPS', 'DELIMITERS', 'MSGS', 'COMMENTS',
                'consts', 'strings', 'symbols', 'err_descs')

    CHARS = string.letters + string.digits + string.punctuation
    LINE_STRING = ("'", '"')


    def __init__(self, filename):
        '''Initialize per instance stuff.

        'filename' is lua source file.
        '''
        self.stream = StringStream(filename)
        self.filename = filename
        self.linenum = 1

        # Numerical constants list
        #
        # Each element is a constant.
        # Numbers represents real numbers(double-precision-floating-point by default)
        #
        # Note:
        # There's no duplicate elements in the list.
        self.consts= []

        # String literals
        #
        # Note:
        # There's no duplicate elements in the list
        self.strings = []

        # Valid symbol list
        #
        # Each element is a symbol, e.g. a variable name or something alike.
        #
        # Note:
        # There's no duplicate elements in the list.
        self.symbols = []

        # Unexpected symbol list
        #
        # Each element is an error descriptor:
        # {'symbol':??, 'err_idx':??}
        #
        # 'symbol' is the unexpected symbol
        # 'err_idx' is the index to the msgs tuple
        self.err_descs = []

        # Token descriptor table
        #
        # Each element is a TokenDesc:
        # {'type':??, 'index':??, 'line':??}
        #
        # 'type' is the index to TOKENTYPE
        # 'index' is the index to the corresponding list
        # 'line' is the line number of this token
        self.token_descs = []


    def __ProcessLineString(self, end):
        '''Retrieve a string from current line.

        -Return a tuple(string, status).
         If status is True, string holds the string.
         If status is False, string is the unexpected symbol.
         '''
        s, status = '', False
        c = self.stream.GetNextChar()
        ends = (end, '\n', '')
        while c not in ends:
            s += c
            if c == '\\':
                s += self.stream.GetNextChar()
            c = self.stream.GetNextChar()
        if c == end:
            status = True
        else:
            # For counting the line number
            self.stream.UnGetChar()

        return (s, status)



    def __ProcessLineComment(self):
        '''Skip current comment line.

        No return value.
        '''
        ends = ('\n', '')
        while self.stream.GetNextChar() not in ends:
            pass
        self.stream.UnGetChar()


    def __ProcessBlockComment(self, count):
        '''Skip a block comment.

        -Return True if a block comment delimiter is found.
        -Return False if no block commtn delimiter is found.
         In this case, we'll reach the EOF.
        '''
        c = self.stream.GetNextChar()
        while c != '':
            if c == ']':
                c = self.stream.GetNextChar()
                i = 0
                while i < count and c == '=':
                    c = self.stream.GetNextChar()
                    i += 1
                if i >= count and c == ']':
                    # Block comment is finished here
                    return True;
            elif c == '\n':
                self.linenum += 1

            c = self.stream.GetNextChar()
        else:
            # Unfinished block comment
            return False


    def __ProcessBlockString(self, count):
        '''Retrieve a block string.

        -Return a tuple(status, bstr).
         -If a corresponding block string delimiter is found,
          status is True and bstr holds the block string.
         -Otherwise, status is False and bstr is '<EOF>'.

        -If the first character of the block string is '\n',
         it is dropped intentionally(Lua does this trick).
        '''
        status, bstr = False, ''

        c = self.stream.GetNextChar()
        # Drop the first character if it is a linefeed
        if c == '\n':
            self.linenum += 1
            c = self.stream.GetNextChar()

        while c != '':
            if c == ']':
                buf = c
                c = self.stream.GetNextChar()
                i = 0
                while i < count and c == '=':
                    c = self.stream.GetNextChar()
                    buf += c
                    i += 1
                if i >= count and c == ']':
                    # Block string is finished here
                    status = True
                    break
                else:
                    # Not the expected block string delimiter,
                    # append buf to bstr
                    bstr += buf
            elif c == '\n':
                self.linenum += 1

            bstr += c
            c = self.stream.GetNextChar()
        else:
            # Unfinished block string
            bstr = '<EOF>'

        return (status, bstr)


    def __ProcessHex(self):
        '''Retrieve a hex number from stream.

        -Assume stream is started with '0x' or '0X'
        -Return a string that may be a hex number.
        '''
        buf = ''
        buf += self.stream.GetNextChar()
        buf += self.stream.GetNextChar()

        c = self.stream.GetNextChar()
        while c.isalnum():
            buf += c
            c = self.stream.GetNextChar()
        self.stream.UnGetChar()
        return buf


    def __ProcessFloat(self):
        '''Retrieve a floating-point number from stream.

        -Assume stream is started with digits|.|+|-
        -Return a string that may be a number
        '''
        ## re = '-?/d*(.?/d+(e|E)?(+|-)?/d+)?'
        buf = ''
        state = 1

        c = self.stream.GetNextChar()
        while c.isalnum() or (c in '+-.'):
            if state == 1:
                if c.isdigit():
                    state = 2
                elif c == '.':
                    state = 3
                elif c in '+-':
                    state = 9
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 2:
                if c.isdigit():
                    state = 2
                elif c == '.':
                    state = 3
                elif c in 'eE':
                    state = 5
                elif c.isalpha():
                    state = 8
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 3:
                if c.isdigit():
                    state = 4
                elif buf[-1].isdigit() and c.isalpha():
                    state = 8
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 4:
                if c.isdigit():
                    state = 4
                elif c in 'eE':
                    state = 5
                elif c.isalpha():
                    state = 8
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 5:
                if c.isalpha():
                    state = 8
                elif c in '+-':
                    state = 6
                elif c.isdigit():
                    state = 7
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 6:
                if c.isalpha():
                    state = 8
                elif c.isdigit():
                    state = 7
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 7:
                if c.isdigit():
                    state = 7
                elif c.isalpha():
                    state = 8
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 8:
                if c.isalnum():
                    state = 8
                else:
                    self.stream.UnGetChar()
                    break
                buf += c
                c = self.stream.GetNextChar()
            elif state == 9:
                if c.isdigit():
                    state = 1
                else:
                    self.stream.UnGetChar()
                    break
            else:
                # Unexpected state
                break
        else:
            self.stream.UnGetChar()

        return buf


    def __ConvertToNum(self, dic):
        '''Convert a string to a number if possible.

        -No return value, fills a token_desc in dic['token'] instead.
        -The string to be converted is in dic['str']
        '''
        num = 'NaN'
        str_num = dic['str']
        try:
            num = float(str_num)
        except ValueError:
            try:
                # Hex value must start with 0x or 0X in Lua
                if str_num[:2] in ('0x', '0X'):
                    num = float.fromhex(str_num)
                else:
                    num = 'NaN'
            except ValueError:
                num = 'NaN'

        if type(num) != types.FloatType:
            # Oops! Not a number
            err = {'symbol':str_num, 'err_id':0}
            if err not in self.err_descs:
                self.err_descs.append(err)
            dic['token']['type'] = self.TOKENTYPE.index('err_descs')
            dic['token']['index'] = self.err_descs.index(err)
        else:
            if num not in self.consts:
                self.consts.append(num)
            dic['token']['type'] = self.TOKENTYPE.index('consts')
            dic['token']['index'] = self.consts.index(num)


    def GetToken(self):
        '''Return the next token in the source file.

        -Return a token descriptor represented in a dict.
            {'type':??, 'index':??, 'line':??}
        -Return None if we reach the EOF.
        '''
        buf = ''
        token = {}

        # Skip non-printable chars
        c = self.stream.GetNextChar()
        while c not in self.CHARS:
            if c == '\n':
                self.linenum += 1
            c = self.stream.GetNextChar()
        else:
            if c == '': # EOF
                return None

        token['line'] = self.linenum
        buf += c

        if c.isalpha() or c == '_':
            # Starts with a letter or an underscore
            c = self.stream.GetNextChar()
            while c.isalnum() or c == '_':
                buf += c
                c = self.stream.GetNextChar()
            self.stream.UnGetChar()

            if buf in self.KEYWORDS:
                # It's a keyword
                token['type'] = self.TOKENTYPE.index('KEYWORDS')
                token['index'] = self.KEYWORDS.index(buf)
            else:
                # It's a user-defined keyword
                token['type'] = self.TOKENTYPE.index('symbols')
                if buf not in self.symbols:
                    self.symbols.append(buf)
                token['index'] = self.symbols.index(buf)
        elif c.isdigit() or c in '.':
            # It may be a number
            # Numbers can not start with a '+' in Lua
            # Accepts:
            #   real: 0.44, 7.9E2, .98, -9.9, 99
            #   hex: 0xFF
            str_num = None
            if c == '0':
                c1 = self.stream.GetNextChar()
                self.stream.UnGetChar(-2)
                if c1 in 'xX':
                    str_num = self.__ProcessHex()
                else:
                    str_num = self.__ProcessFloat()
            else:
                self.stream.UnGetChar()
                str_num = self.__ProcessFloat()

##            if str_num == '+':
##                token['type'] = self.TOKENTYPE.index('OPS')
##                token['index'] = self.OPS.index(str_num)
            if str_num == '.':
                c = self.stream.GetNextChar()
                if c == '.':
                    # It's '..' or '...'
                    c = self.stream.GetNextChar()
                    if c == '.':
                        str_num = '...'
                    else:
                        self.stream.UnGetChar()
                        str_num = '..'
                    token['type'] = self.TOKENTYPE.index('OPS')
                    token['index'] = self.OPS.index(str_num)
                else:
                    self.stream.UnGetChar()
                    token['type'] = self.TOKENTYPE.index('DELIMITERS')
                    token['index'] = self.DELIMITERS.index(str_num)
            else:
                # Convert it to a real number if possible
                self.__ConvertToNum({'token':token, 'str':str_num})

        elif c in self.LINE_STRING:
            # It may be a line string
            s, status = self.__ProcessLineString(c)
            if status:
                if s not in self.strings:
                    self.strings.append(s)
                token['type'] = self.TOKENTYPE.index('strings')
                token['index'] = self.strings.index(s)
            else:
                # Oops! Unfinished string?
                err = {'symbol':s, 'err_id':2}
                if err not in self.err_descs:
                    self.err_descs.append(err)
                token['type'] = self.TOKENTYPE.index('err_descs')
                token['index'] = self.err_descs.index(err)
        elif c == '-':
            # It may be a comment or a number
            c1 = self.stream.GetNextChar()
            if c1 == '-':
                c1 = self.stream.GetNextChar()
                if c1 == '[':
                    i = 0
                    c1 = self.stream.GetNextChar()
                    while c1 == '=':
                        i += 1
                        c1 = self.stream.GetNextChar()
                    if c1 == '[':
                        # Try to process block comments
                        status = self.__ProcessBlockComment(i)
                        token['line'] = self.linenum
                        if not status:
                            # Unfinished block comment
                            err = {'symbol':'<EOF>', 'err_id':3}
                            if err not in self.err_descs:
                                self.err_descs.append(err)
                            token['type'] = self.TOKENTYPE.index('err_descs')
                            token['index'] = self.err_descs.index(err)
                            self.token_descs.append(token)
                            return token
                    else:
                        # It is a line comment
                        self.stream.UnGetChar() # Don't miss the '\n'
                        self.__ProcessLineComment()
                else:
                    self.stream.UnGetChar()
                    self.__ProcessLineComment()
                token['type'] = self.TOKENTYPE.index('COMMENTS')
                token['index'] = -1
                # Do not append to token table
                return token
            else:
                if c1.isdigit():
                    self.stream.UnGetChar(-2)
                    str_num = self.__ProcessFloat()
                    self.__ConvertToNum({'token':token, 'str':str_num})
                else:
                    # It's an operator, '-'
                    self.stream.UnGetChar()
                    token['type'] = self.TOKENTYPE.index('OPS')
                    token['index'] = self.OPS.index(c)
        elif c == '[':
            # It may be a block string
            c1 = self.stream.GetNextChar()
            i = 0
            while c1 == '=':
                i += 1
                c1 = self.stream.GetNextChar()
            if c1 == '[':
                # Block string starts
                status, s = self.__ProcessBlockString(i)
                token['line'] = self.linenum
                if status:
                    # Store the string
                    token['type'] = self.TOKENTYPE.index('strings')
                    if s not in self.strings:
                        self.strings.append(s)
                    token['index'] = self.strings.index(s)
                else:
                    # Unfinished block string
                    err = {'symbol':s, 'err_id':4}
                    if err not in self.err_descs:
                        self.err_descs.append(err)
                    token['type'] = self.TOKENTYPE.index('err_descs')
                    token['index'] = self.err_descs.index(err)
            else:
                # It's a delimiter, '['
                self.stream.UnGetChar(-i-1)
                token['type'] = self.TOKENTYPE.index('DELIMITERS')
                token['index'] = self.DELIMITERS.index(c)
        elif c in self.DELIMITERS:
            # It's a delimiter or an operator
            token['type'] = self.TOKENTYPE.index('DELIMITERS')
            token['index'] = self.DELIMITERS.index(c)
        elif c in self.OPS or c == '~':
            # It's an operator
            if c == '~':
                c1 = self.stream.GetNextChar()
                if c1 != '=':
                    # Unexpected symbols '~'
                    self.stream.UnGetChar()
                    err = {'symbol':c, 'err_id':1}
                    if err not in self.err_descs:
                        self.err_descs.append(err)
                    token['type'] = self.TOKENTYPE.index('err_descs')
                    token['index'] = self.err_descs.index(err)
                else:   # It's '~='
                    token['type'] = self.TOKENTYPE.index('OPS')
                    token['index'] = self.OPS.index('~=')
            else:
                token['type'] = self.TOKENTYPE.index('OPS')
                c1 = self.stream.GetNextChar()
                op = c + c1
                if op in self.OPS:
                    token['index'] = self.OPS.index(op)
                else:
                    token['index'] = self.OPS.index(c)
                    self.stream.UnGetChar()
        else:
            # Unexpected symbols
            err = {'symbol':c, 'err_id':1}
            if err not in self.err_descs:
                self.err_descs.append(err)
            token['type'] = self.TOKENTYPE.index('err_descs')
            token['index'] = self.err_descs.index(err)

        # Add token to token table
        self.token_descs.append(token)
        return token


    def GetTokenInfo(self, token_desc):
        '''Retrieve the information of a given token descriptor.

        -Return a tuple containing all related information.
            (type_id, type_name, sym_idx, sym_value, line_num)
         If the token represents an error, then token_name
         holds the error message.
        -Return None if token_desc is invalid.
        '''
        if (token_desc not in self.token_descs) and \
           token_desc['type'] != self.TOKENTYPE.index('COMMENTS'):
            return None
        else:
            line_num = token_desc['line']
            if token_desc['type'] == self.TOKENTYPE.index('err_descs'):
                # Special handle needed for error messages
                type_id = self.TOKENTYPE.index('MSGS')
                err = self.err_descs[token_desc['index']]
                sym_idx = err['err_id']
                sym_value = err['symbol']
                type_name = self.MSGS[sym_idx]
                return (type_id, type_name, sym_idx, sym_value, line_num)
            elif token_desc['type'] == self.TOKENTYPE.index('COMMENTS'):
                # Special handle needed for comments
                type_id = token_desc['type']
                type_name = self.TOKENTYPE[type_id]
                sym_idx, sym_value = None, None
                return (type_id, type_name, sym_idx, sym_value, line_num)
            else:
                type_id = token_desc['type']
                type_name = self.TOKENTYPE[type_id]
                sym_idx = token_desc['index']
                sym_list = getattr(self, self.TOKENTYPE[type_id])
                sym_value = sym_list[sym_idx]
                return (type_id, type_name, sym_idx, sym_value, line_num)


    def IsCommentToken(self, token_desc):
        '''Return True if the token is a comment.
        '''
        return self.TOKENTYPE[token_desc['type']] == 'COMMENTS'


    def IsErrorTypeId(self, type_id):
        '''Return True if the token represents an error message.
        '''
        return self.TOKENTYPE[type_id] == 'MSGS'


def __main():
    import sys

    if len(sys.argv) != 3:
        return

    f = open(sys.argv[2], 'w')
    lex = LuaLexParser(sys.argv[1])
    token = lex.GetToken()
    while token:
        info = lex.GetTokenInfo(token)
        f.write(repr(info))
        f.write('\n')
        token = lex.GetToken()
    f.close()


if __name__ == '__main__':
    __main()
