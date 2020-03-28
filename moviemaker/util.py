import numpy as np



class AttrDict(dict):
	def __getattr__(self,i):
		return self[i]
	def __setattr__(self,i,v):
		self[i]=v
	def __delattr__(self,i):
		del self[i]


	@staticmethod
	def convert(d):
		nd=AttrDict(d)
		for a in nd.__iter__():
			if (type(nd[a])==dict):
				nd[a]=AttrDict.convert(nd[a])
			if (type(nd[a])==list):
				l=[]
				for e in nd[a]:
					l.append(AttrDict.convert(e))
				nd[a]=l
		return nd



class ElementList:
	def __init__(self):
		self.length=0
		self.a=[]
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		s="["
		for e in self.a:
			s+=str(e)+", "
		s=s[:len(s)-2]+"]"
		if (len(s)==1):s="[]"
		return f"moviemaker.util.ElementList(length={self.length}, elements={s})"
	def __getitem__(self,i):
		return self.a[i]



	def add(self,e):
		self.length+=1
		self.a.append(e)
	def delete(self,i):
		self.length-=1
		del self.a[i]
	def insert(self,i,e):
		self.length+=1
		self.a.insert(i,e)
	def list(self):
		return self
	def clear(self):
		self.a=[]