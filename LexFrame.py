# -*- coding: UTF-8 -*-
# @file:     LexFrame.py
# @author:   zombie.fml<zombie.fml@gmail.com>
# @change:
#   2010-03-23
#   + initial version
#   2010-04-28
#   + add syntax highlighting to source code edit control


import wx
import os
import tempfile
import sys
from LuaLexParser import LuaLexParser
from KeywordFrame import ListFrame
from LuaSTC import LuaSTC


class LexFrame(wx.Frame):
    '''Main frame for Lua lexcial parser.
    '''

    ID_LEX_ANALYZE = 1001
    ID_LEX_OPEN_FILE = 1002
    ID_LEX_SAVE_RESULT = 1003
    ID_LEX_KEYWORDS = 1004
    ID_LEX_FILTER = 1005
    ID_LEX_ABOUT = 1006
    ID_LEX_TOKENS = 1007
    ID_LEX_ERRORS = 1008

    def __init__(
        self, parent, title, ID = -1, pos = wx.DefaultPosition,
        size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE):

        self.sym_table = []

        wx.Frame.__init__(self, parent, ID, title, pos, size, style)

        icon = wx.Icon('./res/app.ico', type = wx.BITMAP_TYPE_ICO )
        self.SetIcon(icon)

	self.SetMinSize(wx.Size(800, 600))

        # Add a toolbar
        toolbar = self.CreateToolBar(wx.TB_TEXT | wx.TB_FLAT)

        tb_size = (32, 32)
        toolbar.SetToolBitmapSize(tb_size)

        open_bmp = wx.Bitmap('./res/open.png')
        save_bmp = wx.Bitmap('./res/save.png')
        analyze_bmp = wx.Bitmap('./res/analyze.png')
        keyword_bmp = wx.Bitmap('./res/keyword.png')
        about_bmp = wx.Bitmap('./res/about.png')

        toolbar.AddLabelTool(self.ID_LEX_OPEN_FILE, 'Open', open_bmp,
                            shortHelp = 'Open a Lua source file')
        toolbar.AddLabelTool(self.ID_LEX_SAVE_RESULT, 'Save', save_bmp,
                             shortHelp = 'Save lexical analysis result')
        toolbar.AddSeparator()
        toolbar.AddLabelTool(self.ID_LEX_ANALYZE, 'Analyze', analyze_bmp,
                             shortHelp = 'Start lexical analysis')
        toolbar.AddSeparator()
        toolbar.AddLabelTool(self.ID_LEX_KEYWORDS, 'Keywords', keyword_bmp,
                             shortHelp = 'Show keywords')
        toolbar.AddSeparator()

        filter_list = [('Unfiltered', 'All'), ('Keywords', 'KEYWORDS'),
                       ('Operator', 'OPS'), ('Delimiters', 'DELIMITERS'),
                       ('Errors', 3),('Constant', 'consts'),
                       ('Strings', 'strings'),('Symbols', 'symbols')
                       ]
        cb = wx.ComboBox(
                toolbar, self.ID_LEX_FILTER, value = 'All',
                size = (150, -1), choices = [],
                style = wx.CB_DROPDOWN | wx.CB_READONLY)
        for k, v in filter_list:
            cb.Append(k, v)
        cb.SetSelection(0)
        self.filter = cb

        toolbar.AddControl(cb)

        toolbar.AddSeparator()
        toolbar.AddLabelTool(self.ID_LEX_ABOUT, 'About', about_bmp,
                             shortHelp = 'About Lua lexical parser')

        toolbar.Realize()

        # Add controls
        panel = wx.Panel(self, -1)
        sizer = wx.GridBagSizer(4, 4)

        self.tokens = wx.ListCtrl(panel, self.ID_LEX_TOKENS,
                                  style = wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.tokens.InsertColumn(0, 'Id')
        self.tokens.InsertColumn(1, 'Class')
        self.tokens.InsertColumn(2, 'Index')
        self.tokens.InsertColumn(3, 'Symbol')
        self.tokens.InsertColumn(4, 'Line number')
        for i in range(5):
            self.tokens.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)

        self.src = LuaSTC(panel, -1)
        font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.src.SetFont(font)
        self.error = wx.ListCtrl(panel, self.ID_LEX_ERRORS, size = (-1, -1),
                            style = wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.error.InsertColumn(0, 'Result')

        sizer.Add(self.tokens, (0, 0), (4, 1),
                  flag = wx.TOP | wx.LEFT | wx.BOTTOM | wx.EXPAND,
                  border = 4)
        sizer.Add(self.src, (0, 1), (3, 1),
                  flag = wx.TOP | wx.RIGHT | wx.LEFT | wx.EXPAND,
                  border = 4)
        sizer.Add(self.error, (3, 1),
                  flag = wx.TOP | wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.EXPAND,
                  border = 4)

        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        for i in range(4):
            sizer.AddGrowableRow(i)
        panel.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_TOOL, self.OnOpenLuaFile, id = self.ID_LEX_OPEN_FILE)
        self.Bind(wx.EVT_TOOL, self.OnSaveResult, id = self.ID_LEX_SAVE_RESULT)
        self.Bind(wx.EVT_TOOL, self.OnLexAnalyze, id = self.ID_LEX_ANALYZE)
        self.Bind(wx.EVT_TOOL, self.OnPopupKeywords, id = self.ID_LEX_KEYWORDS)
        self.Bind(wx.EVT_COMBOBOX, self.OnTokenFilter, id = self.ID_LEX_FILTER)
        self.Bind(wx.EVT_TOOL, self.OnAbout, id = self.ID_LEX_ABOUT)

        self.tokens.Bind(wx.EVT_LEFT_DCLICK, self.OnTokensDoubleClick)
        self.error.Bind(wx.EVT_LEFT_DCLICK, self.OnErrorDoubleClick)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)


    def OnCloseWindow(self, event):
        '''Do some cleaning up before we exit.
        '''
        # TODO
        self.Destroy()

    def OnOpenLuaFile(self, event):
        '''Open a lua source file.
        '''
        dirname = ''
        dlg = wx.FileDialog(self, 'Choose a Lua source file', dirname,
                            '', 'Lua Source File(*.Lua)|*.Lua', wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
              self.src.LoadFile(dlg.GetPath())
        dlg.Destroy()


    def OnSaveResult(self, event):
        '''Save lexical analysis result to a file.
        '''
        dlg = wx.FileDialog(self, 'Save result to...', '', '', 'Text Files(*.txt)|*.txt|All Files(*.*)|*.*',
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            fullpath = dlg.GetPath()
            # Open the file and write result to it
            f = open(fullpath, 'w')
            f.write('idx, (type_id[type_name], sym_idx): "sym_value", line\n\n')
            idx = 1
            for type_id, type_name, sym_idx, sym_value, line in self.sym_table:
                s = '%d, (%d[%s], %d): "%s", %d\n' % \
                    (idx, type_id, type_name, sym_idx, str(sym_value), line)
                f.write(s)
                idx += 1

            # Write summary
            err_count = self.error.GetItemCount()
            sym_count = len(self.sym_table) - err_count
            s = '\n%d symbol(s) found.\n%d error(s) found.\n' % (sym_count, err_count)
            f.write(s)

            f.close()

        dlg.Destroy()


    def OnLexAnalyze(self, event):
        '''Start lexical analysis.
        '''
        # Get a tmp file name
        tmpfile = tempfile.NamedTemporaryFile(suffix = 'lxa', delete = False)
        tmpname = tmpfile.name
        tmpfile.close()
        self.src.SaveFile(tmpname)
        # Append a '\n', thus omitting some special handling while parsing
        f = open(tmpname, 'a')
        f.write('\n')
        f.close()

        # Parse file and build a symbol table
        parser = LuaLexParser(tmpname)
        token = parser.GetToken()
        self.sym_table = []
        while token:
            if not parser.IsCommentToken(token):
                info = parser.GetTokenInfo(token)
                self.sym_table.append(info)
            token = parser.GetToken()

        # Delete tmp file
        os.remove(tmpname)

        # Add to our ListCtrls
        self.tokens.DeleteAllItems()
        self.error.DeleteAllItems()
        item_idx = 0
        sym_filter = self.filter.GetClientData(self.filter.GetSelection())

        for type_id, type_name, sym_idx, sym_value, line in self.sym_table:
            # Dirty trick to handle error messages
            name = type_name
            if type_id == 3:
                name = 3

            # Update items in the listctrl
            if sym_filter == 'All' or sym_filter == name:
                item_idx = self.tokens.InsertStringItem(sys.maxint, str(item_idx + 1))
                self.tokens.SetStringItem(item_idx, 1, '%d(%s)' % (type_id, type_name))
                self.tokens.SetStringItem(item_idx, 2, str(sym_idx))
                self.tokens.SetStringItem(item_idx, 3, str(sym_value))
                self.tokens.SetStringItem(item_idx, 4, str(line))

                if parser.IsErrorTypeId(type_id):
                    # Mark errors with red color
                    item = self.tokens.GetItem(item_idx)
                    item.SetTextColour(wx.RED)
                    self.tokens.SetItem(item)

                # Next item
                item_idx += 1

            # Insert into error list
            if parser.IsErrorTypeId(type_id):
                index = self.error.InsertStringItem(sys.maxint,
                            'Line[%d] : "%s" : error %d: %s' % \
                            (line, sym_value, sym_idx, type_name))
                item = self.error.GetItem(index)
                item.SetTextColour(wx.RED)
                self.error.SetItem(item)

        err_count = self.error.GetItemCount()
        sym_count = len(self.sym_table) - err_count
        if err_count > 0:
            self.error.InsertStringItem(sys.maxint, '')
        self.error.InsertStringItem(sys.maxint, '%d symbol(s) found.' % sym_count)
        self.error.InsertStringItem(sys.maxint, '%d error(s) found.' % err_count)

        self.tokens.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.tokens.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.tokens.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.tokens.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.tokens.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)

        self.error.SetColumnWidth(0, wx.LIST_AUTOSIZE)

        # Delete the parser
        del parser

    def OnPopupKeywords(self, event):
        '''Show keywords and other reserved characters in a popup dialog.
        '''
        lf = ListFrame(self)
        lf.Centre(wx.BOTH)
        lf.Show()

    def OnTokenFilter(self, event):
        '''Filter lexical analysis results.
        '''
        cb = event.GetEventObject()
        data = cb.GetClientData(cb.GetSelection())
        if not self.sym_table:
            return

        self.tokens.DeleteAllItems()
        item_idx = 0
        for type_id, type_name, sym_idx, sym_value, line in self.sym_table:
            # Dirty trick to handle error messages
            name = type_name
            if type_id == 3:
                name = 3

            # Update items in the listctrl
            if data == 'All' or name == data:
                self.tokens.InsertStringItem(item_idx, str(item_idx + 1))
                self.tokens.SetStringItem(item_idx, 1, '%d(%s)' % (type_id, type_name))
                self.tokens.SetStringItem(item_idx, 2, str(sym_idx))
                self.tokens.SetStringItem(item_idx, 3, str(sym_value))
                self.tokens.SetStringItem(item_idx, 4, str(line))

                if type_id == 3:
                    # Mark errors with red color
                    item = self.tokens.GetItem(item_idx)
                    item.SetTextColour(wx.RED)
                    self.tokens.SetItem(item)

                item_idx += 1

        self.tokens.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.tokens.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.tokens.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.tokens.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.tokens.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)


    def OnAbout(self, event):
        '''Popup an about dialog.
        '''
        info = wx.AboutDialogInfo()
        info.Name = 'Lua Lexical Parser'
        info.Version = '1.1.0'
        info.Copyright = '(C) 2010 zombie.fml'
        info.Description = '''\nA Simple Lua 5.1 Lexical Parser.\n
Written in Python.
GUI Powered by wxPython.'''
        info.Developers = ['zombie.fml<zombie.fml@gmail.com>']

        wx.AboutBox(info)


    def OnTokensDoubleClick(self, event):
        '''Handles the tokens listctrl double click event.

        Goto the token line.
        '''
        ctrl = event.GetEventObject()
        idx = ctrl.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
        if idx != -1:
            item = ctrl.GetItem(idx, 4)
            line = int(item.GetText())
            self.GotoLine(self.src, line)


    def OnErrorDoubleClick(self, event):
        '''Handles error listctrl double click event.

        Goto the error line
        '''
        ctrl = event.GetEventObject()
        idx = ctrl.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
        if idx != -1:
            item = ctrl.GetItem(idx, 0)
            s = item.GetText()
            a = s.find('[') + 1
            b = s.find(']')

            # Not found
            if a >= b:
                return

            line = int(s[a:b])
            self.GotoLine(self.src, line)



    def GotoLine(self, ctrl, line):
        '''Goto line in a TextCtrl.

        line is the line number.
        '''
        if ctrl == None:
            return

        lines = ctrl.GetLineCount()
        if line >= lines:
            return

        pos = 0
        for i in range(0, line - 1):
            pos += len(ctrl.GetLine(i))

        ctrl.SetSelection(pos, pos + len(ctrl.GetLine(line - 1)) - 1)
        ctrl.SetFocus()
	ctrl.ScrollToLine((line - 5 and [line - 5] or [line - 1])[0])


if __name__ == '__main__':
    app = wx.App(False)

    win = LexFrame(None, title = 'Lua Lexical Parser')
    win.Maximize()
    win.Show()

    app.MainLoop()
