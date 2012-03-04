# -*- coding: utf-8 -*-
# @file:    KeywordFrame.py
# @author:  zombie.fml<zombiefml@gmail.com>
# @change:
#   2010-4-4
#   + initial version

import wx
import wx.gizmos as gizmos
from LuaLexParser import LuaLexParser

class ListPanel(wx.Panel):
    '''This class implements a simple panel with a TreeListCtrl.

    Keywords are listed in the embeded TreeListCtrl.
    '''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # Resize the TreeListCtrl
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1, style =
                                        wx.TR_DEFAULT_STYLE
                                        | wx.TR_HAS_BUTTONS
                                        | wx.TR_ROW_LINES
                                        | wx.TR_FULL_ROW_HIGHLIGHT)

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,
                                                      wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,
                                                      wx.ART_OTHER, isz))
        fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,
                                                      wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il

        # create some columns
        self.tree.AddColumn("Reserved keywords")
        self.tree.AddColumn("Comment")
        self.tree.SetMainColumn(0) # the one with the tree in it...

        self.root = self.tree.AddRoot("Class")
        self.tree.SetItemImage(self.root, fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx, which = wx.TreeItemIcon_Expanded)

        child = self.tree.AppendItem(self.root, 'Keywords')
        self.tree.SetItemText(child, 'Lua 5.1 keywords', 1)
        self.tree.SetItemImage(child, fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)
        for k in LuaLexParser.KEYWORDS:
            self.tree.AppendItem(child, k)

        child = self.tree.AppendItem(self.root, 'Operators')
        self.tree.SetItemText(child, 'Lua 5.1 operators', 1)
        self.tree.SetItemImage(child, fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)
        for k in LuaLexParser.OPS:
            self.tree.AppendItem(child, k)

        child = self.tree.AppendItem(self.root, 'Delimiters')
        self.tree.SetItemText(child, 'Lua 5.1 delimiters', 1)
        self.tree.SetItemImage(child, fldridx, which = wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(child, fldropenidx, which = wx.TreeItemIcon_Expanded)
        for k in LuaLexParser.DELIMITERS:
            self.tree.AppendItem(child, k)

        self.tree.Expand(self.root)

        self.tree.SetColumnWidth(0, 200)

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())


class ListFrame(wx.Frame):
    '''A simple frame.
    '''
    def __init__(self, parent):
        '''parent can NOT be None.
        '''
        wx.Frame.__init__(self, parent, title = 'Reserved keywords',
                          style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX
                          | wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT)

        icon = wx.Icon('./res/app.ico', type = wx.BITMAP_TYPE_ICO )
        self.SetIcon(icon)

        p = ListPanel(self)


if __name__ == '__main__':
    app = wx.App(False)
    win = ListFrame()
    win.Show()

    app.MainLoop()

