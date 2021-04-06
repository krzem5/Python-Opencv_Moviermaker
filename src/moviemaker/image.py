from .util import *
from PIL import Image as _Image
import cv2
import numpy as np
import os



__all__=["Image","ImageIterator"]



class Image:
	def __init__(self,src):
		self.src=os.path.abspath(src)
		if (self.src[len(self.src)-4:] not in Image.valid_formats()):
			raise Exception("Invalid image type")
		self.img=_Image.open(self.src)
		self.properties=self.get_properties()
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"moviemaker.image.Image(src={self.src}, size=(w={self.properties.size[0]}px, h={self.properties.size[1]}px), length={self.properties.length}s, fps={self.properties.fps}, pan=(start=(x={self.properties.pan.start.x}, y={self.properties.pan.start.y}), end=(x={self.properties.pan.end.x}, y={self.properties.pan.end.y})), pan_size=(w={self.properties.pan_size[0]}, h={self.properties.pan_size[1]}), scale=(start=(x={self.properties.scale.start.x}, y={self.properties.scale.start.y}), end=(x={self.properties.scale.end.x}, y={self.properties.scale.end.y})), optimized={self.properties.optimized})"



	def get_properties(self):
		size=(self.img.width,self.img.height)
		pan_size=(1920,1080)
		return AttrDict(size=size,fps=30,length=5,pan=AttrDict(start=AttrDict(x=0,y=0),end=AttrDict(x=size[0]-pan_size[0],y=size[1]-pan_size[1])),pan_size=pan_size,scale=AttrDict(start=AttrDict(x=1,y=1),end=AttrDict(x=1,y=1)),optimized=self.src.endswith(".png"))



	def optimize(self,override=False):
		n=self.src[:len(self.src)-len(self.src.split(".")[-1])-1]+".png"
		if (override==False and os.path.exists(n)==True and os.path.isfile(n)==True):
			self.src=n
			self.img=_Image.open(self.src)
			return self
		self.img.save(n)
		self.src=n
		self.img=_Image.open(self.src)
		self.properties.optimized=True
		return self



	def preview(self):
		def map(v,aa,ab,ba,bb):
			return (v-aa)/(ab-aa)*(bb-ba)+ba
		cv2.namedWindow("Preview - "+self.src.split("\\")[-1],cv2.WINDOW_NORMAL)
		cv2.resizeWindow("Preview - "+self.src.split("\\")[-1],self.properties.pan_size)
		i=0
		tl=self.properties.length*self.properties.fps
		while True:
			if (i>=tl):
				break
			c=(round(map(i,0,tl,self.properties.pan.start.x,self.properties.pan.end.x)),round(map(i,0,tl,self.properties.pan.start.y,self.properties.pan.end.y)),round(map(i,0,tl,self.properties.pan.start.x,self.properties.pan.end.x))+self.properties.pan_size[0]/map(i,0,tl,self.properties.scale.start.x,self.properties.scale.end.x),round(map(i,0,tl,self.properties.pan.start.y,self.properties.pan.end.y))+self.properties.pan_size[1]/map(i,0,tl,self.properties.scale.start.y,self.properties.scale.end.y))
			frame=np.array(self.img.copy().crop(c))[:,:,::-1].copy()
			frame=cv2.resize(frame,self.properties.pan_size)
			i+=1
			cv2.imshow("Preview - "+self.src.split("\\")[-1],frame)
			if (cv2.waitKey(1)&0xff==27):
				break
		return self



	def set_length(self,l):
		self.properties.length=l
		return self
	def set_pan(self,sx,sy,ex,ey):
		self.properties.pan.start.x=sx
		self.properties.pan.start.y=sy
		self.properties.pan.end.x=ex
		self.properties.pan.end.y=ey
		return self
	def set_pan_size(self,w,h):
		self.properties.pan_size=(w if w!=-1 else self.properties.pan_size[0],h if h!=-1 else self.properties.pan_size[1])
		return self
	def set_fps(self,fps):
		self.properties.fps=fps
		return self
	def set_scale(self,sx,sy,ex,ey):
		self.properties.scale.start.x=sx
		self.properties.scale.start.y=sy
		self.properties.scale.end.x=ex
		self.properties.scale.end.y=ey
		return self



	def get_size(self):
		return self.properties.size
	def get_length(self):
		return self.properties.length
	def get_pan(self):
		return self.properties.pan
	def get_pan_size(self):
		return self.properties.pan_size
	def get_fps(self):
		return self.properties.fps
	def get_scale(self):
		return self.properties.scale
	def get_frame_count(self):
		return self.properties.length*self.properties.fps



	def save(self,p=None,log=False,override=False):
		def map(v,aa,ab,ba,bb):
			return (v-aa)/(ab-aa)*(bb-ba)+ba
		n=os.path.abspath(p) if p!=None else self.src[:len(self.src)-len(self.src.split(".")[-1])-1]+".mp4"
		if (override==False and os.path.exists(n)==True and os.path.isfile(n)==True):
			return self
		out=cv2.VideoWriter(n,cv2.VideoWriter_fourcc(*"mp4v"),self.properties.fps,self.properties.pan_size)
		i=0
		l=-1
		tl=self.properties.length*self.properties.fps
		while (True):
			if (i>=tl):
				break
			if (log==True and int(i/tl*100)>l):
				l=int(i/tl*100)
				print(f"{l}% complete...")
			c=(round(map(i,0,tl,self.properties.pan.start.x,self.properties.pan.end.x)),round(map(i,0,tl,self.properties.pan.start.y,self.properties.pan.end.y)),round(map(i,0,tl,self.properties.pan.start.x,self.properties.pan.end.x))+self.properties.pan_size[0]/map(i,0,tl,self.properties.scale.start.x,self.properties.scale.end.x),round(map(i,0,tl,self.properties.pan.start.y,self.properties.pan.end.y))+self.properties.pan_size[1]/map(i,0,tl,self.properties.scale.start.y,self.properties.scale.end.y))
			frame=np.array(self.img.copy().crop(c))[:,:,::-1].copy()
			frame=cv2.resize(frame,self.properties.pan_size)
			out.write(frame)
			i+=1
			cv2.waitKey(1)
		out.release()
		return self



	def iterator(self):
		return ImageIterator(self)



	@staticmethod
	def from_JSON(json):
		i=Image(json.src)
		for k in json.effects.__iter__():
			d=json.effects[k]
			if (not hasattr(Image,"set_"+k)):
				print("Invalid effect: "+k)
				continue
			if (k=="length"):
				i.set_length(d)
			elif (k=="pan"):
				i.set_pan(d.start.x,d.start.y,d.end.x,d.end.y)
			elif (k=="pan_size"):
				i.set_pan_size(d.w,d.h)
			elif (k=="fps"):
				i.set_fps(d)
			elif (k=="scale"):
				i.set_scale(d.start.x,d.start.y,d.end.x,d.end.y)
		return i
	def to_JSON(self):
		return {"type":"image","src":self.src,"effects":{"length":self.properties.length,"pan":self.properties.pan,"pan_size":{"w":self.properties.pan_size[0],"h":self.properties.pan_size[1]},"fps":self.properties.fps,"scale":self.properties.scale}}



	@staticmethod
	def list(d,c=lambda f:True):
		return [os.path.abspath(os.path.join(d,f)) for f in os.listdir(d) if f[len(f)-4:] in Image.valid_formats() and c(f)]
	@staticmethod
	def valid_formats():
		return [".png",".jpg",".bmp",".tiff"]



class ImageIterator:
	def __init__(self,i):
		self.i=i
		self.step=-1
		self.total=self.i.properties.length*self.i.properties.fps
		self.done=False
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"moviemaker.image.ImageIterator(target={self.i}, step={self.step} total_steps={self.total})"



	def get(self):
		def map(v,aa,ab,ba,bb):
			return (v-aa)/(ab-aa)*(bb-ba)+ba
		if (self.step==-1 or self.step>=self.total):
			self.done=True
			return None
		c=(round(map(self.step,0,self.total,self.i.properties.pan.start.x,self.i.properties.pan.end.x)),round(map(self.step,0,self.total,self.i.properties.pan.start.y,self.i.properties.pan.end.y)),round(map(self.step,0,self.total,self.i.properties.pan.start.x,self.i.properties.pan.end.x))+self.i.properties.pan_size[0]/map(self.step,0,self.total,self.i.properties.scale.start.x,self.i.properties.scale.end.x),round(map(self.step,0,self.total,self.i.properties.pan.start.y,self.i.properties.pan.end.y))+self.i.properties.pan_size[1]/map(self.step,0,self.total,self.i.properties.scale.start.y,self.i.properties.scale.end.y))
		return cv2.resize(np.array(self.i.img.copy().crop(c))[:,:,::-1].copy(),self.i.properties.pan_size)



	def start(self):
		self.step=max(self.step,0)



	def next(self):
		if (self.step==-1):
			return
		self.step+=1
		if (self.step>=self.total):
			self.done=True
