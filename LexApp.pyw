# -*- coding:utf-8 -*-
# @file:    LexApp.pyw
# @author:  zombie.fml<zombiefml@gmail.com>
# @change:
#   2010-4-19
#   + initial version


import wx
from LexFrame import LexFrame

if __name__ == '__main__':
    app = wx.App(False)

    win = LexFrame(None, title = 'Lua Lexical Parser')
    win.Maximize()
    win.Show()

    app.MainLoop()
