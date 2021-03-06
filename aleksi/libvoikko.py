# -*- coding: utf-8 -*-
"""
Python interface to libvoikko, library of Finnish language tools.
This module can be used to perform various natural language analysis
tasks.

An example session demonstrating the use of this module:

 >>> import libvoikko
 >>> v = libvoikko.Voikko(u"fi")
 >>> v.analyze(u"kissa")
 [{'SIJAMUOTO': u'nimento', 'CLASS': u'nimisana', 'STRUCTURE': u'=ppppp'}]
 >>> v.spell(u"kissa")
 True
 >>> v.suggest(u"kisssa")
 [u'kissa', u'kissaa', u'kisassa', u'kisussa']
 >>> v.hyphenate(u"kissa")
 u'kis-sa'
 >>> v.terminate()

"""

# The contents of this file are subject to the Mozilla Public License Version 
# 1.1 (the "License"); you may not use this file except in compliance with 
# the License. You may obtain a copy of the License at 
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
# 
# The Original Code is Libvoikko: Library of natural language processing tools.
# The Initial Developer of the Original Code is Harri Pitkänen <hatapitk@iki.fi>.
# Portions created by the Initial Developer are Copyright (C) 2009 - 2011
# the Initial Developer. All Rights Reserved.
# 
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.

# This library requires Python version 2.7 or newer. It is compatible with
# Python 3 without modifications.

from __future__ import unicode_literals
from ctypes import addressof
from ctypes import byref
from ctypes import CDLL
from ctypes import c_int
from ctypes import c_char
from ctypes import c_char_p
from ctypes import c_wchar
from ctypes import c_wchar_p
from ctypes import c_size_t
from ctypes import c_void_p
from ctypes import create_unicode_buffer
from ctypes import pointer
from ctypes import POINTER
from ctypes import sizeof
from ctypes import string_at
from ctypes import Structure
import os
import platform
import sys

if sys.version_info < (3,):
	unicode_str = unicode
	binary_str = str
	def repr_conv(s):
		return s.encode("UTF-8")
else:
	unicode_str = str
	binary_str = bytes
	def repr_conv(s):
		return s

"""Maximum number of characters in a valid word"""
MAX_WORD_CHARS = 255

"""Maximum number of analyses that can be produced for a word"""
MAX_ANALYSIS_COUNT = 31

class Dictionary:
	"""Represents a morphological dictionary."""
	def __init__(self, language, script, variant, description):
		self.language = language
		self.script = script
		self.variant = variant
		self.description = description
	
	def __repr__(self):
		return repr_conv("<" + self.language + "," + self.script + "," + self.variant + "," + self.description + ">")
	
	def __lt__(self, other):
		if not isinstance(other, Dictionary):
			return False
		if self.language < other.language:
			return True
		if self.script < other.script:
			return True
		if self.variant < other.variant:
			return True
		return self.description < other.description
	
	def __eq__(self, other):
		return isinstance(other, Dictionary) and \
		       self.language == other.language and \
		       self.script == other.script and \
		       self.variant == other.variant and \
		       self.description == other.description
	
	def __hash__(self):
		return hash(self.variant) ^ hash(self.description) ^ hash(self.language) ^ hash(self.script)

class Token:
	"""Represents a token in tokenized natural language text."""
	NONE = 0
	WORD = 1
	PUNCTUATION = 2
	WHITESPACE = 3
	UNKNOWN = 4
	
	_TYPE_NAMES = ["NONE", "WORD", "PUNCTUATION", "WHITESPACE", "UNKNOWN"]
	
	def __init__(self, tokenText, tokenType):
		self.tokenText = tokenText
		self.tokenType = tokenType
	
	def __repr__(self):
		return repr_conv("<" + self.tokenText + "," + \
		       Token._TYPE_NAMES[self.tokenType] + ">")

class Sentence:
	"""Represents a sentence in natural language text."""
	NONE = 0
	NO_START = 1
	PROBABLE = 2
	POSSIBLE = 3
	
	_TYPE_NAMES = ["NONE", "NO_START", "PROBABLE", "POSSIBLE"]
	
	def __init__(self, sentenceText, nextStartType):
		self.sentenceText = sentenceText
		self.nextStartType = nextStartType
	
	def __repr__(self):
		return repr_conv("<" + self.sentenceText + "," + \
		       Sentence._TYPE_NAMES[self.nextStartType] + ">")

class SuggestionStrategy:
	"""Strategies for generating suggestions for incorrectly spelled words."""
	TYPO = 0
	"""Suggestion strategy for correcting human typing errors."""
	OCR = 1
	"""Suggestion strategy for correcting errors in text produced by
	optical character recognition software."""

class GrammarError:
	"""Grammar error from grammar checker."""
	
	def __repr__(self):
		return repr_conv("<" + self.toString() + ">")
	
	def toString(self):
		s = '[code=%i, level=0, descr="", stpos=%i, len=%i, suggs={' \
		    % (self.errorCode, self.startPos, self.errorLen)
		first = True
		for suggestion in self.suggestions:
			if not first:
				s = s + ','
				first = False
			s = s + '"' + suggestion + '"'
		s = s + "}]"
		return s

class VoikkoException(Exception):
	"""Thrown when someting exceptional happens within libvoikko."""
	pass

def _boolToInt(bool):
	if bool:
		return 1
	else:
		return 0

def _anyStringToUtf8(anyString):
	if not anyString:
		return None
	if type(anyString) == unicode_str:
		return anyString.encode("UTF-8")
	else:
		return anyString

def _anyStringToPath(anyString):
	if not anyString:
		return None
	if type(anyString) == unicode_str:
		return anyString.encode(sys.getfilesystemencoding())
	else:
		return anyString

class Voikko(object):
	def __getLib():
		if os.name == 'nt':
			fileName = "libvoikko-1.dll"
			if platform.architecture()[0] == "64bit":
				optionalDependencies = ["libgcc_s_seh-1.dll", "libstdc++-6.dll", "zlib1.dll", "libarchive-13.dll", "libhfstospell-5.dll"]
			else:
				optionalDependencies = ["libgcc_s_sjlj-1.dll", "libstdc++-6.dll", "zlib1.dll", "libarchive-13.dll", "libhfstospell-5.dll"]
		elif sys.platform == 'darwin':
			fileName = "libvoikko.1.dylib"
			optionalDependencies = ["libtinyxml2.3.dylib", "libarchive.13.dylib", "libhfstospell.5.dylib"]
		else:
			fileName = "libvoikko.so.1"
			optionalDependencies = []
		if Voikko._sharedLibrarySearchPath is not None:
			try:
				return CDLL(Voikko._sharedLibrarySearchPath + os.sep + fileName)
			except:
				optDeps = []
				for optionalDep in optionalDependencies:
					try:
						optDeps.append(CDLL(Voikko._sharedLibrarySearchPath + os.sep + optionalDep))
					except:
						pass
				try:
					cdll = CDLL(Voikko._sharedLibrarySearchPath + os.sep + fileName)
					cdll.voikkoDeps = optDeps
					return cdll
				except:
					pass
		return CDLL(fileName)
	__getLib = staticmethod(__getLib)
	
	"""Set the path to a directory that should be used to search for the native library
	before trying to load it from the default (OS specific) lookup path.
	"""
	def setLibrarySearchPath(searchPath):
		Voikko._sharedLibrarySearchPath = searchPath
	setLibrarySearchPath = staticmethod(setLibrarySearchPath)
	
	"""Represents an instance of Voikko. The instance has state, such as
	settings related to spell checking and hyphenation, and methods for performing
	various natural language analysis operations. One instance should not be
	used simultaneously from multiple threads.
	"""
	def __init__(self, language, path = None):
		"""Creates a new Voikko instance with the following optional parameters:
		   language  BCP 47 language tag to be used.
		   path      Extra path that will be checked first when looking for linguistic
		             resources."""
		self.__lib = Voikko.__getLib()
		
		self.__lib.voikkoInit.argtypes = [POINTER(c_char_p), c_char_p, c_char_p]
		self.__lib.voikkoInit.restype = c_void_p
		
		self.__lib.voikkoTerminate.argtypes = [c_void_p]
		self.__lib.voikkoTerminate.restype = None
		
		self.__lib.voikkoSpellUcs4.argtypes = [c_void_p, c_wchar_p]
		self.__lib.voikkoSpellUcs4.restype = c_int
		
		self.__lib.voikkoSuggestUcs4.argtypes = [c_void_p, c_wchar_p]
		self.__lib.voikkoSuggestUcs4.restype = POINTER(c_wchar_p)
		
		self.__lib.voikko_free_suggest_ucs4.argtypes = [POINTER(c_wchar_p)]
		self.__lib.voikko_free_suggest_ucs4.restype = None
		
		self.__lib.voikkoNextGrammarErrorUcs4.argtypes = [c_void_p, c_wchar_p,
		                                   c_size_t, c_size_t, c_int]
		self.__lib.voikkoNextGrammarErrorUcs4.restype = c_void_p
		
		self.__lib.voikkoGetGrammarErrorCode.argtypes = [c_void_p]
		self.__lib.voikkoGetGrammarErrorCode.restype = c_int
		
		self.__lib.voikkoGetGrammarErrorStartPos.argtypes = [c_void_p]
		self.__lib.voikkoGetGrammarErrorStartPos.restype = c_size_t
		
		self.__lib.voikkoGetGrammarErrorLength.argtypes = [c_void_p]
		self.__lib.voikkoGetGrammarErrorLength.restype = c_size_t
		
		self.__lib.voikkoGetGrammarErrorSuggestions.argtypes = [c_void_p]
		self.__lib.voikkoGetGrammarErrorSuggestions.restype = POINTER(c_char_p)
		
		self.__lib.voikkoFreeGrammarError.argtypes = [c_void_p]
		self.__lib.voikkoFreeGrammarError.restype = None
		
		self.__lib.voikkoGetGrammarErrorShortDescription.argtypes = [c_void_p, c_char_p]
		self.__lib.voikkoGetGrammarErrorShortDescription.restype = POINTER(c_char)
		
		self.__lib.voikkoHyphenateUcs4.argtypes = [c_void_p, c_wchar_p]
		self.__lib.voikkoHyphenateUcs4.restype = POINTER(c_char)
		
		self.__lib.voikkoFreeCstr.argtypes = [POINTER(c_char)]
		self.__lib.voikkoFreeCstr.restype = None
		
		self.__lib.voikkoAnalyzeWordUcs4.argtypes = [c_void_p, c_wchar_p]
		self.__lib.voikkoAnalyzeWordUcs4.restype = POINTER(c_void_p)
		
		self.__lib.voikkoFreeErrorMessageCstr.argtypes = [POINTER(c_char)]
		self.__lib.voikkoFreeErrorMessageCstr.restype = None
		
		self.__lib.voikko_free_mor_analysis.argtypes = [POINTER(c_void_p)]
		self.__lib.voikko_free_mor_analysis.restype = None
		
		self.__lib.voikko_mor_analysis_keys.argtypes = [c_void_p]
		self.__lib.voikko_mor_analysis_keys.restype = POINTER(c_char_p)
		
		self.__lib.voikko_mor_analysis_value_ucs4.argtypes = [c_void_p, c_char_p]
		self.__lib.voikko_mor_analysis_value_ucs4.restype = c_wchar_p
		
		self.__lib.voikkoNextTokenUcs4.argtypes = [c_void_p, c_wchar_p, c_size_t,
		                                           POINTER(c_size_t)]
		self.__lib.voikkoNextTokenUcs4.restype = c_int
		
		self.__lib.voikkoNextSentenceStartUcs4.argtypes = [c_void_p, c_wchar_p, c_size_t, POINTER(c_size_t)]
		self.__lib.voikkoNextSentenceStartUcs4.restype = c_int
		
		self.__lib.voikkoSetBooleanOption.argtypes = [c_void_p, c_int, c_int]
		self.__lib.voikkoSetBooleanOption.restype = c_int
		
		self.__lib.voikkoSetIntegerOption.argtypes = [c_void_p, c_int, c_int]
		self.__lib.voikkoSetIntegerOption.restype = c_int
		
		error = c_char_p()
		self.__handle = self.__lib.voikkoInit(byref(error), _anyStringToUtf8(language), _anyStringToPath(path))
		if error.value != None:
			self.__handle = 0
			raise VoikkoException("Initialization of Voikko failed: " + unicode_str(error.value, "UTF-8"))
	
	def __del__(self):
		# Ensure that resources are freed before this object is deleted.
		self.terminate()
	
	def setBooleanOption(self, option, value):
		"""Sets a boolean option to specified value (True or False). This is a low level function
		available for applications that know about the numerical option codes. The same options can also
		be set using option specific setter methods.
		"""
		result = self.__lib.voikkoSetBooleanOption(self.__handle, option, _boolToInt(value))
		if result == 0:
			raise VoikkoException("Could not set boolean option " + unicode_str(option) + " to value " + unicode_str(value) + ".")
	
	def setIntegerOption(self, option, value):
		"""Sets a integer option to specified value. This is a low level function
		available for applications that know about the numerical option codes. The same options can also
		be set using option specific setter methods.
		"""
		result = self.__lib.voikkoSetIntegerOption(self.__handle, option, value)
		if result == 0:
			raise VoikkoException("Could not set integer option " + unicode_str(option) + " to value " + unicode_str(value) + ".")
	
	def __isValidInput(self, text):
		return "\0" not in text
	
	def terminate(self):
		"""Releases the resources allocated by libvoikko for this instance. The instance cannot be used anymore
		after this method has been called. The resources are released automatically when the Python object is
		deleted. This method may be used to make sure that the resources are immediately released since they
		may take significant amount of memory and timely object deletion by Python runtime cannot always be
		relied upon.
		"""
		if (self.__handle != 0):
			self.__lib.voikkoTerminate(self.__handle)
			self.__handle = 0
			# Replace __lib with a dummy object that throws exception when any method is called. This ensures
			# that nothing bad happens if methods of a Voikko instance are called after termination.
			class DummyLib:
				def __getattr__(obj, name):
					raise VoikkoException("Attempt to use Voikko instance after terminate() was called")
			self.__lib = DummyLib()
	
	def listDicts(path = None):
		"""Return a list of Dictionary objects representing the available
		dictionary variants. If path is specified, it will be searched first
		before looking from the standard locations.
		"""
		lib = Voikko.__getLib()
		lib.voikko_list_dicts.argtypes = [c_char_p]
		lib.voikko_list_dicts.restype = POINTER(c_void_p)
		lib.voikko_free_dicts.argtypes = [POINTER(c_void_p)]
		lib.voikko_free_dicts.restype = None
		lib.voikko_dict_language.argtypes = [c_void_p]
		lib.voikko_dict_language.restype = c_char_p
		lib.voikko_dict_script.argtypes = [c_void_p]
		lib.voikko_dict_script.restype = c_char_p
		lib.voikko_dict_variant.argtypes = [c_void_p]
		lib.voikko_dict_variant.restype = c_char_p
		lib.voikko_dict_description.argtypes = [c_void_p]
		lib.voikko_dict_description.restype = c_char_p
		
		cDicts = lib.voikko_list_dicts(_anyStringToPath(path))
		dicts = []
		i = 0
		while bool(cDicts[i]):
			cDict = cDicts[i]
			language = unicode_str(lib.voikko_dict_language(cDict), "UTF-8")
			script = unicode_str(lib.voikko_dict_script(cDict), "UTF-8")
			variant = unicode_str(lib.voikko_dict_variant(cDict), "ASCII")
			description = unicode_str(lib.voikko_dict_description(cDict), "UTF-8")
			dicts.append(Dictionary(language, script, variant, description))
			i = i + 1
		lib.voikko_free_dicts(cDicts)
		return dicts
	listDicts = staticmethod(listDicts)
	
	def __libForSupportedLanguages():
		lib = Voikko.__getLib()
		lib.voikkoFreeCstrArray.argtypes = [POINTER(c_char_p)]
		lib.voikkoFreeCstrArray.restype = None
		return lib
	__libForSupportedLanguages = staticmethod(__libForSupportedLanguages)
	
	def __listSupportedLanguagesForOperation(path, lib, operation):
		languages = []
		cLanguages = operation(_anyStringToPath(path))
		i = 0
		while bool(cLanguages[i]):
			languages.append(unicode_str(cLanguages[i], "UTF-8"))
			i = i + 1
		lib.voikkoFreeCstrArray(cLanguages)
		return languages
	__listSupportedLanguagesForOperation = staticmethod(__listSupportedLanguagesForOperation)
	
	def listSupportedSpellingLanguages(path = None):
		"""Return a list of language codes representing the languages for which
		at least one dictionary is available for spell checking.
		If path is specified, it will be searched first before looking from
		the standard locations.
		"""
		lib = Voikko.__libForSupportedLanguages()
		lib.voikkoListSupportedSpellingLanguages.argtypes = [c_char_p]
		lib.voikkoListSupportedSpellingLanguages.restype = POINTER(c_char_p)
		def listOperation(p):
			return lib.voikkoListSupportedSpellingLanguages(p)
		return Voikko.__listSupportedLanguagesForOperation(path, lib, listOperation)
	listSupportedSpellingLanguages = staticmethod(listSupportedSpellingLanguages)

	def listSupportedHyphenationLanguages(path = None):
		"""Return a list of language codes representing the languages for which
		at least one dictionary is available for hyphenation.
		If path is specified, it will be searched first before looking from
		the standard locations.
		"""
		lib = Voikko.__libForSupportedLanguages()
		lib.voikkoListSupportedHyphenationLanguages.argtypes = [c_char_p]
		lib.voikkoListSupportedHyphenationLanguages.restype = POINTER(c_char_p)
		def listOperation(p):
			return lib.voikkoListSupportedHyphenationLanguages(p)
		return Voikko.__listSupportedLanguagesForOperation(path, lib, listOperation)
	listSupportedHyphenationLanguages = staticmethod(listSupportedHyphenationLanguages)

	def listSupportedGrammarCheckingLanguages(path = None):
		"""Return a list of language codes representing the languages for which
		at least one dictionary is available for grammar checking.
		If path is specified, it will be searched first before looking from
		the standard locations.
		"""
		lib = Voikko.__libForSupportedLanguages()
		lib.voikkoListSupportedGrammarCheckingLanguages.argtypes = [c_char_p]
		lib.voikkoListSupportedGrammarCheckingLanguages.restype = POINTER(c_char_p)
		def listOperation(p):
			return lib.voikkoListSupportedGrammarCheckingLanguages(p)
		return Voikko.__listSupportedLanguagesForOperation(path, lib, listOperation)
	listSupportedGrammarCheckingLanguages = staticmethod(listSupportedGrammarCheckingLanguages)

	def getVersion():
		"""Return the version number of the Voikko library."""
		lib = Voikko.__getLib()
		lib.voikkoGetVersion.argtypes = []
		lib.voikkoGetVersion.restype = c_char_p
		cVersion = lib.voikkoGetVersion()
		return unicode_str(cVersion, "UTF-8")
	getVersion = staticmethod(getVersion)
	
	def spell(self, word):
		"""Check the spelling of given word. Return true if the word is correct,
		false if it is incorrect.
		"""
		if not self.__isValidInput(word):
			return False
		
		result = self.__lib.voikkoSpellUcs4(self.__handle, word)
		if result == 0:
			return False
		elif result == 1:
			return True
		else:
			raise VoikkoException("Internal error returned from libvoikko")
	
	def suggest(self, word):
		"""Generate a list of suggested spellings for given (misspelled) word.
		If the given word is correct, the list contains only the word itself.
		"""
		if not self.__isValidInput(word):
			return []
		
		cSuggestions = self.__lib.voikkoSuggestUcs4(self.__handle, word)
		pSuggestions = []
		
		if not bool(cSuggestions):
			return pSuggestions
		
		i = 0
		while bool(cSuggestions[i]):
			pSuggestions.append(cSuggestions[i])
			i = i + 1
		
		self.__lib.voikko_free_suggest_ucs4(cSuggestions)
		return pSuggestions
	
	def __getGrammarError(self, cGrammarError, language):
		gError = GrammarError()
		gError.errorCode = self.__lib.voikkoGetGrammarErrorCode(cGrammarError)
		gError.startPos = self.__lib.voikkoGetGrammarErrorStartPos(cGrammarError)
		gError.errorLen = self.__lib.voikkoGetGrammarErrorLength(cGrammarError)
		gError.suggestions = []
		cSuggestions = self.__lib.voikkoGetGrammarErrorSuggestions(cGrammarError)
		if bool(cSuggestions):
			i = 0
			while bool(cSuggestions[i]):
				gError.suggestions.append(unicode_str(cSuggestions[i], "UTF-8"))
				i = i + 1
		cErrorShortDescription = self.__lib.voikkoGetGrammarErrorShortDescription(cGrammarError, _anyStringToUtf8(language))
		gError.shortDescription = unicode_str(string_at(cErrorShortDescription), "UTF-8")
		self.__lib.voikkoFreeErrorMessageCstr(cErrorShortDescription)
		return gError
	
	def __grammarParagraph(self, paragraph, offset, language):
		paragraphLen = len(paragraph)
		skipErrors = 0
		errorList = []
		while True:
			cError = self.__lib.voikkoNextGrammarErrorUcs4(self.__handle,
			        paragraph, paragraphLen, 0, skipErrors)
			if not bool(cError):
				return errorList
			gError = self.__getGrammarError(cError, language)
			gError.startPos = offset + gError.startPos
			errorList.append(gError)
			self.__lib.voikkoFreeGrammarError(cError)
			skipErrors = skipErrors + 1
	
	def grammarErrors(self, text, language):
		"""Check the given text for grammar errors and return a
		list of GrammarError objects representing the errors that were found.
		Unlike the C based API this method accepts multiple paragraphs
		separated by newline characters.
		"""
		if not self.__isValidInput(text):
			return []
		
		textUnicode = unicode_str(text)
		errorList = []
		offset = 0
		for paragraph in textUnicode.split("\n"):
			errorList = errorList + self.__grammarParagraph(paragraph, offset, language)
			offset = offset + len(paragraph) + 1
		return errorList
	
	def analyze(self, word):
		"""Analyze the morphology of given word and return the list of
		analysis results. The results are represented as maps having property
		names as keys and property values as values.
		"""
		if not self.__isValidInput(word):
			return []
		
		cAnalysisList = self.__lib.voikkoAnalyzeWordUcs4(self.__handle, word)
		pAnalysisList = []
		
		if not bool(cAnalysisList):
			return pAnalysisList
		
		i = 0
		while bool(cAnalysisList[i]):
			cAnalysis = cAnalysisList[i]
			cKeys = self.__lib.voikko_mor_analysis_keys(cAnalysis)
			pAnalysis = {}
			j = 0
			while bool(cKeys[j]):
				key = cKeys[j]
				value = self.__lib.voikko_mor_analysis_value_ucs4(cAnalysis, key)
				pAnalysis[unicode_str(key, 'ASCII')] = value
				j = j + 1
			pAnalysisList.append(pAnalysis)
			i = i + 1
		
		self.__lib.voikko_free_mor_analysis(cAnalysisList)
		return pAnalysisList
	
	def tokens(self, text):
		"""Split the given natural language text into a list of Token objects."""
		startIndex = 0
		tokens = []
		while True:
			i = text.find("\0", startIndex)
			if i == -1:
				break
			tokens = tokens + self.__splitTokens(text[startIndex:i])
			tokens.append(Token("\0", Token.UNKNOWN))
			startIndex = i + 1
		tokens = tokens + self.__splitTokens(text[startIndex:])
		return tokens
	
	def __splitTokens(self, text):
		uniText = unicode_str(text)
		uniTextPtr = create_unicode_buffer(uniText)
		wcharSize = sizeof(c_wchar)
		result = []
		textLen = len(uniText)
		tokenLen = c_size_t()
		position = 0
		while textLen > 0:
			tokenType = self.__lib.voikkoNextTokenUcs4(self.__handle,
			            c_wchar_p(addressof(uniTextPtr) + position * wcharSize), textLen, byref(tokenLen))
			if tokenType == Token.NONE:
				break
			tokenText = uniText[position:position+tokenLen.value]
			result.append(Token(tokenText, tokenType))
			position = position + tokenLen.value
			textLen = textLen - tokenLen.value
		return result
	
	def sentences(self, text):
		"""Split the given natural language text into a list of Sentence objects."""
		if not self.__isValidInput(text):
			return [Sentence(text, Sentence.NONE)]
		
		uniText = unicode_str(text)
		result = []
		textLen = len(uniText)
		sentenceLen = c_size_t()
		position = 0
		while textLen > 0:
			sentenceType = self.__lib.voikkoNextSentenceStartUcs4(self.__handle,
			            uniText[position:], textLen, byref(sentenceLen))
			sentenceText = uniText[position:position+sentenceLen.value]
			result.append(Sentence(sentenceText, sentenceType))
			if sentenceType == Sentence.NONE:
				break
			position = position + sentenceLen.value
			textLen = textLen - sentenceLen.value
		return result
	
	def getHyphenationPattern(self, word):
		"""Return a character pattern that describes the hyphenation of given word.
		  ' ' = no hyphenation at this character,
		  '-' = hyphenation point (character at this position
		        is preserved in the hyphenated form),
		  '=' = hyphentation point (character at this position
		        is replaced by the hyphen.)
		"""
		if not self.__isValidInput(word):
			return "".ljust(len(word))
		
		cHyphenationPattern = self.__lib.voikkoHyphenateUcs4(self.__handle, word)
		hyphenationPattern = string_at(cHyphenationPattern)
		self.__lib.voikkoFreeCstr(cHyphenationPattern)
		return unicode_str(hyphenationPattern, 'ASCII')
	
	def hyphenate(self, word):
		"""Return the given word in fully hyphenated form."""
		pattern = self.getHyphenationPattern(word)
		hyphenated = ""
		for i in range(len(pattern)):
			patternC = pattern[i]
			if patternC == ' ':
				hyphenated = hyphenated + word[i]
			elif patternC == '-':
				hyphenated = hyphenated + "-" + word[i]
			elif patternC == '=':
				hyphenated = hyphenated + "-"
		return hyphenated
	
	def setIgnoreDot(self, value):
		"""Ignore dot at the end of the word (needed for use in some word processors).
		If this option is set and input word ends with a dot, spell checking and
		hyphenation functions try to analyse the word without the dot if no results
		can be obtained for the original form. Also with this option, string tokenizer
		will consider trailing dot of a word to be a part of that word.
		Default: false
		"""
		self.setBooleanOption(0, value)
	
	def setIgnoreNumbers(self, value):
		"""Ignore words containing numbers.
		Default: false
		"""
		self.setBooleanOption(1, value)
	
	def setIgnoreUppercase(self, value):
		"""Accept words that are written completely in uppercase letters without checking
		them at all.
		Default: false
		"""
		self.setBooleanOption(3, value)
	
	def setAcceptFirstUppercase(self, value):
		"""Accept words even when the first letter is in uppercase (start of sentence etc.)
		Default: true
		"""
		self.setBooleanOption(6, value)
	
	def setAcceptAllUppercase(self, value):
		"""Accept words even when all of the letters are in uppercase. Note that this is
		not the same as setIgnoreUppercase: with this option the word is still
		checked, only case differences are ignored.
		Default: true
		"""
		self.setBooleanOption(7, value)
	
	def setIgnoreNonwords(self, value):
		"""(Spell checking only): Ignore non-words such as URLs and email addresses.
		Default: true
		"""
		self.setBooleanOption(10, value)
	
	def setAcceptExtraHyphens(self, value):
		"""(Spell checking only): Allow some extra hyphens in words. This option relaxes
		hyphen checking rules to work around some unresolved issues in the underlying
		morphology, but it may cause some incorrect words to be accepted. The exact
		behaviour (if any) of this option is not specified.
		Default: false
		"""
		self.setBooleanOption(11, value)
	
	def setAcceptMissingHyphens(self, value):
		"""(Spell checking only): Accept missing hyphens at the start and end of the word.
		Some application programs do not consider hyphens to be word characters. This
		is reasonable assumption for many languages but not for Finnish. If the
		application cannot be fixed to use proper tokenisation algorithm for Finnish,
		this option may be used to tell libvoikko to work around this defect.
		Default: false
		"""
		self.setBooleanOption(12, value)
	
	def setAcceptTitlesInGc(self, value):
		"""(Grammar checking only): Accept incomplete sentences that could occur in
		titles or headings. Set this option to true if your application is not able
		to differentiate titles from normal text paragraphs, or if you know that
		you are checking title text.
		Default: false
		"""
		self.setBooleanOption(13, value)
	
	def setAcceptUnfinishedParagraphsInGc(self, value):
		"""(Grammar checking only): Accept incomplete sentences at the end of the
		paragraph. These may exist when text is still being written.
		Default: false
		"""
		self.setBooleanOption(14, value)
	
	def setAcceptBulletedListsInGc(self, value):
		"""(Grammar checking only): Accept paragraphs if they would be valid within
		bulleted lists.
		Default: false
		"""
		self.setBooleanOption(16, value)
	
	def setNoUglyHyphenation(self, value):
		"""Do not insert hyphenation positions that are considered to be ugly but correct
		Default: false
		"""
		self.setBooleanOption(4, value)
	
	def setHyphenateUnknownWords(self, value):
		"""(Hyphenation only): Hyphenate unknown words.
		Default: true
		"""
		self.setBooleanOption(15, value)
	
	def setMinHyphenatedWordLength(self, value):
		"""The minimum length for words that may be hyphenated. This limit is also enforced on
		individual parts of compound words.
		Default: 2
		"""
		self.setIntegerOption(9, value)
	
	def setSpellerCacheSize(self, value):
		"""Controls the size of in memory cache for spell checking results. 0 is the default size,
		1 is twice as large as 0 etc. -1 disables the spell checking cache entirely."""
		self.setIntegerOption(17, value)
	             
	def setSuggestionStrategy(self, value):
		"""Set the suggestion strategy to be used when generating spelling suggestions.
		Default: SuggestionStrategy.TYPO
		"""
		if value == SuggestionStrategy.OCR:
			self.setBooleanOption(8, True)
		elif value == SuggestionStrategy.TYPO:
			self.setBooleanOption(8, False)
		else:
			raise VoikkoException("Invalid suggestion strategy")

Voikko._sharedLibrarySearchPath = None
