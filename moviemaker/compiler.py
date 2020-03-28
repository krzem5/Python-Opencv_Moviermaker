from .image import *
from .transitions import *
from .util import *
from .video import *
import cv2
import json as JSON
import os



class Compiler:
	def __init__(self):
		self.arr=ElementList()
		self.fps=30
		self.size=(1920,1080)
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"moviemaker.compiler.Compiler(elements={self.arr})"



	def add(self,e):
		self.arr.add(e)
		return self
	def remove(self,i):
		self.arr.delete(i)
		return self
	def insert(self,i,e):
		self.arr.insert(e,i)
		return self
	def list(self):
		return self.arr.list()



	def get_frame_count(self):
		f=0
		for i in self.arr.list():
			f+=i.get_frame_count()
		return f



	def from_JSON(self,p):
		json=None
		with open(p,"r") as f:
			json=AttrDict.convert(JSON.loads(f.read()))
		self.arr.clear()
		for d in json.data:
			if (d.type=="video"):
				self.arr.add(Video.from_JSON(d))
			elif (d.type=="image"):
				self.arr.add(Image.from_JSON(d))
			elif (d.type=="transition"):
				self.arr.add(Transition.from_JSON(d))
			else:
				print("Invalid type: "+d.type)
	def save_JSON(self,p):
		json={"data":[]}
		for e in self.arr.list():
			json["data"].append(e.to_JSON())
		with open(p,"w") as f:
			f.write(JSON.dumps(json,indent=4,sort_keys=True).replace("    ","\t"))



	def render(self,o,log=False,override=False):
		if (override==False and os.path.exists(o)==True and os.path.isfile(o)==True):
			return self
		out=cv2.VideoWriter(o,cv2.VideoWriter_fourcc(*"mp4v"),self.fps,self.size)
		i=0
		itrl=[]
		s=0
		for o in self.arr.list():
			if (hasattr(o,"iterator")):
				if (s==1):
					itrl.append(Transition.default())
				itrl.append(o.iterator())
				s=1
			elif (hasattr(o,"transition") and o.transition==True):
				if (s==0):
					continue
				itrl.append(o)
				s=0
			else:
				print("Unknown element: "+o+". Skipping...")
		if (s==0):
			del itrl[len(itrl)-1]
		itrl[0].start()
		j=0
		tl=self.get_frame_count()
		l=-1
		while (True):
			f=itrl[i].get()
			if (f is None):
				i+=2
				if (i>=len(itrl)):
					break
				itrl[i].start()
				for k in range(0,itrl[i-1].null_frame_c):
					out.write(itrl[i-1].run(Video.null_frame(self.size),0,0,self.size,self.fps))
					if (log==True and int(j/tl*100)>l):
						l=int(j/tl*100)
						print(f"{l}% complete...")
					j+=1
				f=itrl[i].get()
			if (i>0):
				f=itrl[i-1].run(f,1,itrl[i].step,self.size,self.fps)
			if (i+1<len(itrl)):
				f=itrl[i+1].run(f,0,itrl[i].total-itrl[i].step,self.size,self.fps)
			out.write(f)
			if (log==True and int(j/tl*100)>l):
				l=int(j/tl*100)
				print(f"{l}% complete...")
			j+=1
			for o in itrl:
				if (hasattr(o,"next")):
					o.next()
		out.release()
		cv2.destroyAllWindows()
		return self