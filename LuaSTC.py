# -*-coding: utf-8 -*-
# @file:        LuaSTC.py
# @author:      zombie.fml<zombiefml@gmail.com>
# @change:
#	2010-04-28
#	+ initial version, can do syntax highlighting for Lua source code


import wx
import wx.stc as stc

class LuaSTC(stc.StyledTextCtrl):
	KEYWORDS = ('and', 'break', 'do', 'else', 'elseif','end', 'false',
                'for', 'function', 'if', 'in', 'local', 'nil', 'not',
                'or', 'repeat','return', 'then', 'true', 'until', 'while')

	faces = {'times':'Times New Roman',
			'mono' : 'Courier New',
			'helv' : 'Arial',
			'other': 'Comic Sans MS',
			'size' : 10,
			'size2': 8}


	def __init__(self, parent, ID, pos = wx.DefaultPosition,
			size = wx.DefaultSize, style = 0):


		stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

		# setup our lexer
		self.SetLexer(stc.STC_LEX_LUA)
		self.SetProperty('fold.compact', '1')
		self.SetKeyWords(0, ' '.join(self.KEYWORDS))

		# setup some parameters
		self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
		self.SetEdgeColumn(80)
		self.SetEdgeColour(wx.Colour(0xFF, 0xFF, 0xCD))
		#self.SetUseHorizontalScrollBar(False)
		self.SetUseAntiAliasing(True)

		# line numbers in the margin
		self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
		self.SetMarginWidth(1, 25)

		# make some styles
		self.StyleClearAll()

		# Global default styles for all languages
		self.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                                  "face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,
                                  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % self.faces)
		self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR,
                                  "face:%(helv)s" % self.faces)
		self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,
                                  "fore:#FFFFFF,back:#0000FF")
		self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,
                                  "fore:#000000,back:#FF0000,bold")

		# Single quoted string
		self.StyleSetSpec(stc.STC_LUA_CHARACTER,
                                  "fore:#dd0000,face:%(mono)s,size:%(size)d" % self.faces)
		# Comments
		self.StyleSetSpec(stc.STC_LUA_COMMENT,
								  "fore:#00aa00,face:%(helv)s,size:%(size)d,italic" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_COMMENTLINE,
                                  "fore:#00aa00,face:%(helv)s,size:%(size)d,italic" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_COMMENTDOC,
                                  "fore:#00aa00,face:%(helv)s,size:%(size)d,italic" % self.faces)
		# Default
		self.StyleSetSpec(stc.STC_LUA_DEFAULT,
                                  "fore:#000000,face:%(mono)s,size:%(size)d" % self.faces)
		# Identifiers
		self.StyleSetSpec(stc.STC_LUA_IDENTIFIER,
                                  "fore:#000000,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_LITERALSTRING,
                                  "fore:#7F007F,face:%(mono)s,size:%(size)d" % self.faces)
		# Number
		self.StyleSetSpec(stc.STC_LUA_NUMBER,
                                  "fore:#007F7F,size:%(size)d" % self.faces)
		# Operators
		self.StyleSetSpec(stc.STC_LUA_OPERATOR,
                                  "size:%(size)d" % self.faces)
		# Pre-processor
		self.StyleSetSpec(stc.STC_LUA_PREPROCESSOR,
                                  "fore:#ff8000,size:%(size)d" % self.faces)
		# String
		self.StyleSetSpec(stc.STC_LUA_STRING,
                                  "fore:#dd0000,face:%(mono)s,size:%(size)d" % self.faces)
		# End of line where string is not closed
		self.StyleSetSpec(stc.STC_LUA_STRINGEOL,
                                  "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % self.faces)
		# Keyword
		self.StyleSetSpec(stc.STC_LUA_WORD,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD2,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD3,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD4,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD5,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD6,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD7,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)
		self.StyleSetSpec(stc.STC_LUA_WORD8,
                                  "fore:#ff7700,face:%(mono)s,size:%(size)d" % self.faces)


class LuaSTCFrame(wx.Frame):
	def __init__(self, parent, ID, title):
		wx.Frame.__init__(self, parent, ID, title, size = wx.DefaultSize)

		edit = LuaSTC(self, -1)
		self.Centre()
		self.Show()


if __name__ == '__main__':
	app = wx.App(False)
	LuaSTCFrame(None, -1, "Lua")
	app.MainLoop()
