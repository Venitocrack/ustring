from io import StringIO,BytesIO,UnsupportedOperation
from os import sep
import re
from sys import version_info
if version_info[0] != 3:raise ImportError("ustring only for python 3")
del(version_info)

class String():
	"""
	string class

	appends utilities to str and bytes
	it support str and bytes,but only python 3

	arguments:
		sob:str or bytes,constructor dont give support for
			a given String instance as sob,
			sob is the string (or bytes) to wrapp 
		unicode: bool default True
			encoded as unicode	
		encoding: string default utf-8
			default encoding for .encode() , .decode() , .tobytes(),etc
		changeifbytes: bool default False
			if this is true and sob is bytes and unicode True
			or sob is string and unicode False,
			sob is changed to respect unicode,
			else is the unicode changed 
		mutable: bool default True
			if mutable is true,you can mutate this string
			else you cant
		mattr_mutable: bool default False 
			if this is True the mutable attribute
			can be changed,else you cant
		show_string: bool default True
			if this is True,when in the 
			repr() shows the string wrapping
			else it did not 
		cursed: bool default False
			if this String has a cursor
			if this is true,the initial cursor
			position is defined via ´cursor´ and 
			its an integer 
		cursor: int default 0
			if a cursor exists,this is defined as
			the string cursor
		"""
	def __init__(self,sob="",unicode=True,encoding="utf-8",changeifbytes=False,
				 mutable=True,mattr_mutable=False,show_string=True,cursed=False,
				 cursor = 0):
		"""constructor of String"""
		if not(isinstance(sob,(bytes,str))):
			try:
				if unicode:
					sob = str(sob)
				else:
					sob = bytes(sob,encoding)
			except TypeError:
				raise TypeError("in sob expected str or bytes-like,got {}".format(type(sob)))
		self.string = sob 
		self.unicode = unicode 
		if unicode and isinstance(sob,bytes) and changeifbytes:
			self.string = str(sob)[2:-1]
		else:
			self.unicode = False 
		self._change_bytes = changeifbytes
		self.__show_string = show_string 
		self.__mutable = mutable 
		self.__mattr_mutable = mattr_mutable 
		self.encoding = encoding
		self.__cursed = cursed
		self.__cursor = cursor
		if not(self.unicode) and changeifbytes:
			self.string = bytes(sob,self.encoding)
	
	@property
	def mutable(self):
		"""return True if you can mutate this string"""
		return self.__mutable
	
	@mutable.setter 
	def mutable(self,other):
		"""
		if in the constructor the karg mattr_mutable is True,you can change the mutable value
		if not,raises ValueError
		"""
		if self.__mattr_mutable:
			self.__mutable = bool(other)
		else:
			raise ValueError(
				f"{self}.mutable is inmutable,do not try to change it.")

	@property 
	def mmutable(self):
		"""return True if you can change the mutable attribute"""
		return self.__mattr_mutable

	@property 
	def cursor(self):
		"""return the position of the cursor if created else raises IOError"""
		if self.__cursed:
			return self.__cursor 
		else:
			raise IOError(f"{self} has not cursor,to create one call self.create_cursor()")

	@cursor.setter 
	def cursor(self,v):
		"""set the position of the cursor if exists one else raises IOError"""
		v = int(v)
		if not(self.__cursed):
			raise IOError(f"{self} has not cursor,to create one call self.create_cursor()")
		self.__cursor = v

	def tostring(self):
		"""return this transformed to python str"""
		if not(isinstance(self.string,str)):
			return str(self.string)[2:-1]
		return self.string 
	
	def switch_unicode(self):
		"""if this String is bytes,it transforms itself to unicode"""
		if isinstance(self.string,bytes):
			self.string = self.tostring()
	
	def tobytes(self,encoding=-1):
		"""
		return this but as bytes
		good to know:
			the encoding used to this transformation 
			is the encoding passed in the constructor
			if no encoding given
		"""
		if isinstance(self.string,str):
			return bytes(self.string,self.encoding if encoding != -1 else encoding)
		return self.string

	def switch_bytes(self):
		"""if this String is str,it transforms itself to bytes"""
		if isinstance(self,str):
			self.string = self.tobytes()

	def switch(self):
		"""
		switch the type for str and bytes
		for example: 
			>>> s = String(b'hello')
			>>> s.isbytes()
			True
			>>> s.switch()
			>>> s.isbytes()
			False
			>>> s.switch()
			>>> s.isbytes()
			True
		"""
		if isinstance(self.string,str):
			self.switch_bytes()
		else:
			self.switch_unicode()
	
	def cursed(self):
		"""return if this string has a cursor"""
		return self.__cursed

	def isbytes(self):
		"""return true if this envolve bytes"""
		return isinstance(self.string,bytes)

	def tostringio(self):
		"""return a io.StringIO instance for self"""
		if not(self.cursed()):
			return StringIO(self.tostring())
		else:
			x = StringIO(self.tostring())
			x.seek(self.cursor)
			return x

	def create_cursor(self):
		"""creates a new cursor with value 0"""
		self.__cursed = True 

	def read(self,cursor=-1):
		"""
		arguments:
			cursor: int
				de cursor to start reading,
				default -1,this mean 
				it take the value of self.cursor
				if exists else 0
		return:
			str:
				the string readed for self
		"""
		if cursor == -1 and self.cursed():
			cursor = self.cursor 
		elif cursor == -1:
			cursor = 0 
		if self.cursed():
			self.cursor += cursor
			if self.cursor >= len(self.tostring()):
				self.cursor = len(self.tostring()[:-abs(self.cursor-len(self.tostring()))])
		try:
			return self.tostring()[cursor:]
		except IndexError:
			return ""

	def _normalize(self,s):
		"""
		transform s to the type of envolving data
		for example:
			>>> s1 = String(b'hello')
			>>> s2 = String('hello')
			>>> s3 = "hello"
			>>> s1._normalize(s3)
			b"hello"
			>>> s3 = b'hello'
			>>> s2._normalize(s3)
			'hello'
		"""
		if isinstance(s,String):
			return self._normalize(s.tostring())
		if isinstance(self.string,type(s)):
			return s
		else:
			if isinstance(self.string,bytes):
				return String(s).tobytes()
			elif isinstance(self.string,str):
				return String(s).tostring()
			else:
				raise ValueError("invalid data type for input :" + str(type(s)))

	def write(self,sob):
		"""
		arguments:
			sob : str or bytes
				the string to write in self
		return:
			None
		"""
		sob = self._normalize(sob)
		if not(self.mutable):
			raise IOError(f"{self} is not mutable.")
		else:
			if self.cursed():
				s = StringIO(self.tostring())
				s.seek(self.cursor)
				s.write(String(sob).tostring())
				self.string =self._normalize(s.getvalue())
			else:
				self.string = self.string + self._normalize(sob)

	def set_cursor(self,i):
		"""
		set the cursor in i value,if i is not an integer it 
		try to transform to an integer,if fails raises an TypeError
		and if self has not a cursor raises a IOError
		"""
		self.cursor = i 

	def __add__(self,sob):
		"""
		self + x
		supports:
			str
			bytes
			String
		"""
		sob = self._normalize(sob)
		return String(self.string + sob,mutable=self.mutable,cursed=self.cursed(),
				cursor=self.cursor if self.cursed() else 0,unicode=self.unicode,encoding=self.encoding,
				changeifbytes=self._change_bytes,mattr_mutable=self.__mattr_mutable,show_string=self.__show_string)

	def __len__(self):
		"""len(self)"""
		return len(self.string)

	def __eq__(self, value):
		"""self == x"""
		value = self._normalize(value)
		return self.string == value 

	def equals(self,sob):
		"""
		return if sob is equal to self.string
		using self == sob,normalize sob before checking
		this method doesnt normalize sob 
		Examples:
			>>> s = String("hello")
			>>> s == b"hello"
			True
			>>> s.equals(b"hello")
			False
			>>> s.equals("hello")
			True
		"""
		return self.string == sob

	def split_pattern(self,x,flags=0,on_match=""):
		"""
		split but taking x as a re pattern 
		flags:
			flags of re to search 
		on_match:
			thing appended in all matchs
		"""
		s = self.tostring()
		res = []
		curr = ""
		skips = 0 
		for c in range(len(s)):
			if skips:
				skips -= 1 
				continue
			match = re.match(x,s[c:],flags)
			if match:
				skips = len(match.group())-1
				res.append(curr+on_match)
				curr = ""
			else:
				curr += s[c]
		if curr != "":
			res.append(curr)
		return res

	def __iter__(self):
		"""iter(self)"""
		yield from iter(self.string)

	def __str__(self):
		"""str(self)"""
		return self.tostring()

	def __getitem__(self,ind):
		"""self[i]"""
		return self.string_instance(self.string[ind])

	def __setitem__(self,ind,item):
		"""self[i] = item"""
		if self.mutable:
			item = self._normalize(item)
			r = self._normalize("")
			for i in range(len(self.string)):
				if i == ind:
					r = r + item 
				else:
					r = r + self.string[i]
			self.string = r 
		else:raise IOError(
			f"{self} is not mutable")

	def setitem(self,ind,item,override=False):
		"""
		set the item just like would do
		using `self[ind] = item` if `override`
		is False,else set the item overriding
		the last item
		for Exmaple:
			>>> s = String("hello")
			>>> s[0] = "a"
			>>> s
			String(aello)
			>>> s.setitem(1,"a",override=True)
			>>> s
			String(aello)
			>>> s = String("how are you?")
			>>> s[0] = "lol"
			>>> s
			String(lolow are you?)
			>>> s = String("how are you?")
			>>> s.setitem(0,"lol",override=True)
			>>> s
			String(lol are you?)
		raises:
			IOError if self is not mutable
		"""
		if not(override):
			self.__setitem__(ind,item)
		else:
			if self.mutable:
				item = self._normalize(item)
				r = self._normalize("")
				skips = 0
				for i in range(len(self.string)):
					if skips:
						skips -= 1
						continue 
					if i == ind:
						r = r + item 
						skips = len(item)-1
					else:
						r = r + self.string[i]
				self.string = r 
			else:raise IOError(
				f"{self} is not mutable")
	
	def instance(self,cls):
		"""return if cls is instance of self.string"""
		return isinstance(self.string,cls)

	def __repr__(self):
		"""repr(self)"""
		return f"<{self.__class__.__name__}()>" if not(self.__show_string) else f"<{self.__class__.__name__}({self.tostring()})>"

	def write_on(self,file,mode="a"):
		"""
		giving a io.BytesIO or PathLike (and mode)
		writes in the file itself,
		raises ValueError if the mode is for reading
		"""
		if not(isinstance(file,BytesIO)):
			file = open(file,mode)
		try:
			if not("b" in file.mode):
				file.write(self.tostring())
			else:file.write(self.tobytes())
		except UnsupportedOperation:
			raise ValueError(
				"mode must be of writting,got reading")

	def split_literal(self,c,maxsplit=-1):
		"""
		split a string as a literal,not like re.Pattern or like int
		"""
		x = self.tostring().split(
			String(c).tostring(),maxsplit=maxsplit)
		r = []
		for i in x:
			r.append(String(i))
		return r

	def split(self,x,maxsplit=-1,flags=-1,on_match=""):
		"""
		split self into x
		x can be int,str,bytes and re.Pattern
		Exmaples:
			>>> s = String("hello there!  are you ok?")
			>>> s.split(" ")	
			['hello', 'there!', '', 'are', 'you', 'ok?']
			>>> s = String("have")
			>>> s.split(2)
			["ha","ve"]
			>>> s = String("we 894389234are 84584353845 bad.")
			>>> s.split(r"\d+",flags=0) #with setting the flags to 0 it split like a re pattern
			["we ","are "," bad."]
		if you are using self.split(r"\d+")
		to split in numbers,just like re.split,
		will dont work;you must compile it
		self.split(re.compile(r"\d+"))
		NOTE:
			if you are splitting bytes with an diferent for 
			one integer,this will not work,
			it is dont yet implemented
		"""
		if x == 1 or x == "":
			s = list(self.tostring())
			if maxsplit==-1:
				return s 
			else:
				try:
					r = String("")
					for i in s[maxsplit-1:]:
						r += i 
					s[maxsplit:] = []
					s[maxsplit-1] = r
					return s 
				except IndexError:
					return s 
		elif flags != -1:
			return self.split_pattern(x,flags=flags,on_match=on_match)
		try:
			if isinstance(x,int):
				res = []
				curr = self.string_instance("")
				for i in range(len(self.string)):
					#i is index
					if i % x == 0 and i != 0: #it has been produced x iterations 
						if len(res)==maxsplit: #if maxsplit is reached
							break
						res.append(curr)
						curr = self.string_instance("")
						curr += self.string[i]
					else:
						curr += self.string[i]
				if curr != self._normalize("") and not(len(res)==maxsplit):
					#len(self) %x != 0 
					res.append(curr)
				return res
			else:
				if not(isinstance(x,(str,re.Pattern,bytes))):
					raise TypeError(f"in String.split(x) x expected to be str,re.Pattern,int or bytes,got {type(x)}")
				if isinstance(x,bytes):
					x = str(x)[2:-1]
				if isinstance(x,re.Pattern):
					return self.split_pattern(x,flags=flags,on_match=on_match)
				else:
					return self.split_literal(x,maxsplit=maxsplit)
		except TypeError as e:
			if str(e) == f"in String.split(x) x expected to be str,re.Pattern,int or bytes,got {type(x)}":
				raise 
			else:
				raise TypeError(
					"String.split(int) when String wrappings bytes is not supported") from NotImplementedError(
					"wait to the version 0.2") 

	def splitspace(self,maxsplit=-1):
		"""splits this string by ' '."""
		return self.split(r"\s+",maxsplit=maxsplit,flags=0)
	
	def splitlines(self,maxsplit=-1):
		"""splits this string by new lines"""
		return self.split("\n",maxsplit=maxsplit)

	def match(self,pattern,flags=0):
		"""
		matches this string using pattern `pattern` and flags `flags`,
		similar to re.match(pattern,string,flags) where string is this
		instance
		"""
		return re.match(pattern,self.tostring(),flags)

	def compile(self):
		"""compile this string as a re.Pattern"""
		return re.compile(self.tostring())

	def search(self,regex,flags=0):
		"""search in the string the first match of ´regex´"""
		return re.search(regex,self.tostring(),flags)

	def searchall(self,regex,flags=0):
		"""
		NotImplemented::
			search all matches in this string searching for ´regex´
		"""
		return NotImplemented

	def string_instance(self,sob,**kargs):
		"""
		return a string instance wrapping ´sob´ and using
		by default the configuration of this string,
		if not given in **kargs,else uses de **kargs argument
		"""
		return String(sob,cursor = kargs.get("cursor",self.cursor if self.cursed() else 0),
				unicode=kargs.get("unicode",self.unicode),encoding=kargs.get("encoding",self.encoding),
				mutable=kargs.get("mutable",self.mutable),cursed=kargs.get("cursed",self.cursed()),
				changeifbytes=kargs.get("changeifbytes",self._change_bytes),mattr_mutable=kargs.get(
				"mattr_mutable",self.__mattr_mutable),show_string=kargs.get("show_string",self.__show_string))


	def sub(self,pattern,replace="",flags=0):
		"""
		same than re.sub(self.tostring(),regex,flags),
		but return a String instance
		"""
		return self.string_instance(re.sub(pattern,replace,self.tostring(),flags=flags))

	def subn(self,pattern,replace="",flags=0):
		"""		
		same than re.subn(self.tostring(),regex,flags),
		but return a String instance
		"""
		x = re.subn(pattern,replace,self.tostring(),flags=flags)
		x = list(x)
		x[0] = self.string_instance(x[0])
		return tuple(x)

	def findall(self,pattern,flags=0):
		"""
		findall pattern match searching in 
		this string
		"""
		x = re.findall(pattern,self.tostring(),flags=flags)
		r = []
		for s in x:
			r.append(self.string_instance(s))
		return r 

	def ordsum(self):
		"""
		return the sum of all ord characters
		"""
		c = 0
		for i in self.tostring():
			c+= ord(i)
		return c 
	
	def ord(self):
		"""
		String('c').ord() is the same than ord('c')
		but it supports bytes
		"""
		if not(len(self) == 1):
			raise ValueError(
				f"string of len 1 expected,got len {len(self.string)}")
		return self.ordsum()

	def encode(self,encoding=-1):
		"""
		same than str(x).encode(),
		but x supports bytes,
		so is usefull to change an encoding 
		of a bytes-like 
		for example:
			>>> s = String(b"hello")
			>>> s.string = s.encode("utf-8")
			>>> s.encode("ASCII")
			b'hello'
		"""
		if encoding == -1:
			encoding = self.encoding
		return bytes(self.tostring(),encoding)

	def decode(self,encoding=-1):
		"""
		decode this as bytes,
		usefull to interprete a bytes like
		as other encoding 
		"""
		if encoding == -1:
			encoding = self.encoding 
		return self.tobytes().decode(encoding)

	def __getattr__(self,attr):
		try:
			return getattr(self.string,attr)
		except AttributeError:
			raise AttributeError(
				f"String has not the attribute {attr}")

	def tobytesio(self,encoding=-1):
		"""
		return a io.BytesIO instance wrapping this string
		"""
		return BytesIO(self.encode(encoding))

	def json_load(self):
		"""
		load this string as json and return 
		the object codified
		"""
		import json
		return json.loads(self.tostring())

	def pickle_load(self,encoding=-1):
		"""
		load this string using pickle and return 
		the object returned by pickle.loads()
		"""
		import pickle as p 
		return p.loads(self.encode(encoding=encoding))

	def totkstringvar(self,master=None,name=None):
		"""
		return this as tk.StringVar
		"""
		import tkinter as tk 
		return tk.StringVar(value=self.tostring(),name=name,master=master)

	def isdigit(self):
		"""
		return if this is representing a integer number (base=10)
		"""
		return self.tostring().isdigit()

	def ishex(self):
		"""return if this string is representing an hexadecimal number"""
		x = self.tostring()
		s = set(x)
		for i in "0123456789AaBbCcDdEeFfx":
			if i in s:
				s.remove(i)
		if list(s) != []:
			return False 
		else:
			try:
				self.fromhex()
			except ValueError:return False
			else:return True

	def fromhex(self):
		"""return in int,this string,interpreted as hexadecimal"""
		try:
			g = {}
			if self.tostring().startswith("0x"):
				exec(f"a = {self.tostring()}",g)
				return g["a"]
			else:
				exec(f"a = 0x{self.tostring()}",g)
				return g["a"]
		except SyntaxError:
			raise ValueError(f"{self} is not an hex-like")
	
	hex = fromhex

	def add_chr(self,i):
		"""
		giving a integer:i 
		the character in unicode of that integer
		is aded to this string 
		"""
		i = int(i)
		self.switch_unicode()
		return self.string + chr(i)

	@classmethod 
	def bstr2str(cls,bs,encoding="utf-8"):
		"""
		transforms a string that is the first two hexadecimal digit
		translates it to str
		for Example:
			>>> b"\xFF"
			ÿ
			>>> String.bstr2str("FF")
			ÿ
		"""
		try:
			if not(bs.startswith(r"\x")):
				return cls(bs).tobytes(encoding=encoding)
			g = {}
			exec("a = b'"+bs+"'",g)
			return String(g["a"]).encode(encoding)
		except SyntaxError:
			raise ValueError(bs)

	@classmethod 
	def str2bytes(cls,str,encoding="utf-8"):
		"""
		transform a given str to a bytes,
		the encoding is given by `encoding`
		"""
		if not(isinstance(str,type(''))):
			raise TypeError(
				f"in str expected str,got {type(str)}")
		return cls(str).encode(encoding=encoding)

	@classmethod 
	def bytes2str(cls,bytes):
		"""
		transform a given bytes to a str
		"""
		if not(isinstance(bytes,type(b''))):
			raise TypeError(
				f"in bytes expected bytes-like,got {type(bytes)}")
		return str(bytes)[2:-1]

	def replace(self,a,b):
		"""
		same than str.replace(a,b) but support bytes
		if this is bytes,returns a String wrapping bytes
		"""
		return self.string_instance(self.tostring().replace(
				String(a).tostring(),String(b).tostring()),
				  changeifbytes=True,unicode=isinstance(self.string,str))

	def startswith(self,substring):
		"""same than str.startswith(substring) but with bytes support"""
		return self.tostring().startswith(
			String(substring).tostring() #bytes support
			)

	def endswith(self,substring):
		"""
		check if this ends with substring
		supports bytes
		"""
		substring = self._normalize(substring) #do not deepcopy
		return self.string[-(len(substring)):] == substring

	def remove_empty_lines(self):
		"""
		removes all empty lines in the string
		"""
		self._check_mutable()
		s = self.split("\n+",flags=0,on_match=chr(9000))
		r = ""
		l = []
		for i in s:
			l.append(re.sub(chr(9000),"\n",i))
		for i in l:
			r += i 
		self.switch_unicode()
		self.string = r

	def remove(self,pattern,flags=0):
		"""remove the pattern pattern for this string"""
		self._check_mutable()
		x = self.sub(pattern,"",flags)
		self.string = self._normalize(x.string)

	def count(self,pattern,flags=0):
		"""
		return the number of matches of pattern
		"""
		return len(self.findall(pattern,flags))

	def find_numbers(self,flags=0):
		"""
		return a generator of all the numbers in this string
		"""
		return self.findall(r"\d+",flags)

	def remove_last(self):
		"""
		remove the last element of the string
		"""
		self._check_mutable()
		self.string = self.string[:-1]

	def copy(self):
		"""
		return a copy of self
		not deepcopy
		"""
		return self.string_instance(self.string)

	def empty(self):
		"""
		return if this string is empty
		"""
		return self.string == self._normalize("")

	def _check_mutable(self):
		if not(self.mutable):
			raise ValueError(
				f"{repr(self)} is not mutable,please check <String()>.mutable\n"
				"\t    before using a function that changes this value")

	def apply(self,call,take_str=False,take_bytes=False,
				take_self=False,keep=True,encoding="utf-8"):
		"""
		applies a method to self,
		call must be callable,else raises a ValueError
		arguments:
			call:callable
				the method to call
			take_str:bool
				if this is true,
				to the method will be always given
				str
			take_bytes:bool
				if this is true,
				to the method will be always given
				bytes
			take_self:bool
				if this is true,
				to the method will be always given
				self
			keep:bool
				if this is true,
				the string keeps the data type,
				(if is in str or bytes)
				ignoring if the function returned bytes or str
			encoding:str
				this is the encoding of passing
				to bytes if take_bytes is true
		"""
		self._check_mutable()
		if not(callable(call)):
			raise ValueError("`call` must be callable,got"+str(type(call)))
		if (take_str and take_bytes) or (take_bytes and take_self) or (take_str and take_self):
			raise ValueError("take_str or take_bytes,cant be the two ones")
		if take_str:
			if keep:
				self.string = self._normalize(call(self.tostring()))
			else:
				self.string = call(self.tostring())
		elif take_bytes:
			if keep:
				self.string = self._normalize(call(self.tobytes(encoding=encoding)))
			else:
				self.string = call(self.tobytes(encoding=encoding))
		elif take_self:
			if keep:
				self.string = self._normalize(call(self))
			else:
				self.string = call(self)
		else:
			if keep:
				self.string = self._normalize(call(self.string))
			else:
				self.string = call(self.string)

	def apply_factory(self,take_bytes=False,take_str=False,
							take_self=False,keep=True,encoding="utf-8"):
		"""
		returns a function that,when called 
		applies the method given with the config seen here
		the args are the same than in the apply() method
		but the `call` one is given to the returning function
		"""
		self._check_mutable()
		def cached(call):
			self.apply(call,take_bytes=take_bytes,
							take_str=take_str,
							take_self=take_self,
							keep=keep,
							encoding=encoding)
		return cached

	def match_porcent(self,b):
		"""
		return the porcent of match of self and b
		"""
		match = 0.0
		#full normalizing ´b´
		other = self.string_instance(self._normalize(b))
		max_len = max(len(self),len(other))
		if len(self) > len(other):
			bigger = self 
		else:
			bigger = other 
		match_porcent = 1/max_len 
		diference = abs(len(self)-len(other))
		if diference:
			for indx in range(len(bigger[:diference])):
				try:
					if self[indx] == other[indx]:
						match += match_porcent
				except (IndexError):
					pass
		else:
			for indx in range(len(bigger)):
				if self[indx] == other[indx]:
					match += match_porcent
		return float("%2f" %(match*100))

	def hex_encode(self):
		"""
		return this string encoded as a hexadecimal
		LIST,not sum,sequence of hexadecimal numbers
		"""
		res = b''
		for char in self.tostring(): #normalize to string,always
			x= hex(ord(char))[2:] #ord(x) = 2 -> "0x2" -> "2" 
			x+="\\" #to make a split
			res += String(x).encode()
		res = res[:-1] #to dont end with "\\"
		return res

	def hex_decode(self):
		"""
		decode self parsing it as a SEQUENCE,not SUM
		of hexadecimal integers
		"""
		res = ""
		for numb in self.split("\\"): #no need to use flags=0
			if numb=="":
				continue
			numb = String(numb).hex() #hex-string convertion to int
			res += chr(numb)
		return res

	def encrypt(self,method="u-enc",depth=0):
		"""
		method can be:
			DontImplemented:"u-enc":default the default encryping of the string 
			"hex":encrypt it to hexadecimal,just as hex_encode and hex_decode
		depth:int 
			number of times repeting the encrypt process
		"""
		if method=="u-enc":
			return NotImplemented
		elif method =="hex":
			if depth == 0:
				self.apply(String.hex_encode,take_self=True)
			else:
				self.apply(String.hex_encode,take_self=True)
				self.encrypt(method,depth=depth-1)
		else:
			raise ValueError(
				"invaliv encrypt method : "+str(method))

	def unencrypt(self,method="u-enc",depth=0):
		"""
		unencrypt this string.
		using method `method`,
		method can be:
			DontImplemented:"u-enc":default,and default used by .encrypt()
			"hex":hexadecimal encrypt/decode
		depth:int 
			number of times repeting the unencrypt process
		"""
		if method=="u-enc":
			return NotImplemented
		elif method == "hex":
			if depth == 0:
				self.apply(String.hex_decode,take_self=True)
			else:
				self.apply(String.hex_decode,take_self=True)
				self.unencrypt(method,depth=depth-1)
		else:
			raise ValueError(
				"invaliv encrypt method : "+str(method))

	def compare(self,other,missing_key=" "):
		"""
		compare 2 strings and setting with `missing_key`
		the spaces that are diferent in self and other
		"""
		other = self.string_instance(self._normalize(other))
		res = String("")
		for i in range(len(other)):
			if i == len(self):
				break
			if self[i] == other[i]:
				res += self[i]
			else:
				res += missing_key
		return res

	def diferences(self,other,equals_key=" "):
		"""
		compare 2 strings and setting with `equals_key` the characters
		that match in the both strings
		"""
		other = self.string_instance(self._normalize(other))
		missing_key = equals_key
		res = String("")
		for i in range(len(other)):
			if i == len(self):
				break
			if self[i].tostring() != other[i].tostring():
				res += self[i]
			else:
				res += missing_key
		return res

	USES_DIFERENCES = False
	USES_DIFERENCES.__doc__ = """if this is True,when doing self != x return the result of the `diference` method
	this is no default to true,because would make problems in if statements"""

	def __ne__(self,other):
		if not(String.USES_DIFERENCES):
			return not(self == other) 
		else:
			return self.diference(other)

	def switch_elems(self,*elements,force_return=False):
		"""
		switch of position the elements *elements
		elements can be consecutive strings,(if this the number 
		of this consecutive strings need to be a factor of 2)
		or a list or pairs [old_character,new_character]
		"""
		pure = False
		for element in elements:
			if isinstance(element,(str,bytes,String)):
				pure = True
				break 
		if pure and len(elements) % 2 != 0:
			raise ValueError(
				"not enought elements to unpack")
		#pure = False;expect [["a","b"],[old,new],...]
		#pure = True ;expect "a","b" ,old,new,...
		if pure:
			l = []
			skip = False
			for el in range(len(elements)):
				if skip:
					skip = False 
					continue
				l.append([elements[el],elements[el+1]])
				skip = True
			elements = l 
		r = self.copy()
		for pair in elements:
			x = self.string_instance("")
			for i in self:
				if i == pair[0]:
					i = pair[1]
				elif i == pair[1]:
					i = pair[0]
				x+=i
			r.string = r._normalize(x)
		if not(self.mutable) or force_return:
			return r
		else:
			self.string = self._normalize(r)

	def path_iter(self,sep=sep):
		"""
		split and iter this as a path-like
		"""
		yield from self.split(sep) if sep in self else self.split("/")

	def path_like(self):
		"""
		return if this can be interpreted as a 
		path-like
		"""
		with_disk = self.match(r"[abcdefghijkolpnmvcxzqwrtyu]:")
		if with_disk:
			with_disk = with_disk.group()
		if with_disk and len(self)<=2:
			return False
		rute = list(self.path_iter())
		if with_disk:
			rute[0] = rute[0][2:]
		if rute[0] == self:
			return False
		return True

	def copy_mutable(self):
		"""
		return a copy of self,
		but mutable
		"""
		return self.string_instance(self.string,mutable=True)




