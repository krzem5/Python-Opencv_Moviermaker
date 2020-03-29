from .util import *
import cv2
import os



class Video:
	def __init__(self,src):
		self.src=os.path.abspath(src)
		if (self.src[len(self.src)-4:] not in Video.valid_formats()):
			raise Exception("Invalid video type")
		self.properties=self.get_properties()
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"moviemaker.video.Video(src={self.src}, size=(w={self.properties.size[0]}px, h={self.properties.size[1]}px), frame_count={self.properties.frame_count}, fps={self.properties.fps}, length=~{self.properties.length}s, speed={float(self.properties.speed)}x, crop=(start={self.properties.crop.start}, end={self.properties.crop.end}), optimized={self.properties.optimized})"



	def get_properties(self):
		cap=cv2.VideoCapture(self.src)
		size=(int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
		frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		fps=int(cap.get(cv2.CAP_PROP_FPS))
		length=int(frame_count/fps*100)/100
		cap.release()
		return AttrDict(size=size,frame_count=frame_count,fps=fps,length=length,speed=1,crop=AttrDict(start=0,end=frame_count),optimized=self.src.endswith(".mp4"))



	def optimize(self,log=False,override=False):
		n=self.src[:len(self.src)-len(self.src.split(".")[-1])-1]+".mp4"
		if (override==False and os.path.exists(n)==True and os.path.isfile(n)==True):
			self.src=n
			return self
		out=cv2.VideoWriter(n,cv2.VideoWriter_fourcc(*"mp4v"),self.properties.fps,self.properties.size)
		cap=cv2.VideoCapture(self.src)
		i=0
		l=-1
		while (True):
			if (log==True and int(i/self.properties.frame_count*100)>l):
				l=int(i/self.properties.frame_count*100)
				print(f"{l}% complete...")
			_,frame=cap.read()
			if (frame is None):
				break
			out.write(frame)
			i+=1
			cv2.waitKey(1)
		cap.release()
		out.release()
		self.src=n
		self.properties.optimized=True
		return self



	def preview(self):
		cv2.namedWindow("Preview - "+self.src.split("\\")[-1],cv2.WINDOW_NORMAL)
		cv2.resizeWindow("Preview - "+self.src.split("\\")[-1],self.properties.size)
		cap=cv2.VideoCapture(self.src)
		i=0
		while (True):
			if (i<self.properties.crop.start):continue
			if (i>self.properties.crop.end):break
			i+=1
			_,frame=cap.read()
			if (frame is None):
				break
			cv2.imshow("Preview - "+self.src.split("\\")[-1],frame)
			if (cv2.waitKey(1)&0xff==27):
				break
		cap.release()
		return self



	def set_crop(self,s,e):
		self.properties.crop.start=s
		self.properties.crop.end=e
		return self
	def set_speed(self,s):
		self.properties.speed=s
		return self
	def set_fps(self,fps):
		self.properties.fps=fps
		return self



	def get_crop(self):
		return self.properties.crop
	def get_speed(self):
		return self.properties.speed
	def get_fps(self):
		return self.properties.fps
	def get_frame_count(self):
		return self.properties.frame_count



	def save(self,p=None,log=False,override=False):
		n=os.path.abspath(p) if p!=None else self.src[:len(self.src)-len(self.src.split(".")[-1])-1]+".mp4"
		if (override==False and os.path.exists(n)==True and os.path.isfile(n)==True):
			return self
		cap=cv2.VideoCapture(self.src)
		out=cv2.VideoWriter(n,cv2.VideoWriter_fourcc(*"mp4v"),self.properties.fps,self.properties.size)
		i=0
		l=-1
		while (True):
			if (i<self.properties.crop.start):continue
			if (i>self.properties.crop.end):break
			if (log==True and int(i/self.properties.frame_count*100)>l):
				l=int(i/tl*100)
				print(f"{l}% complete...")
			i+=1
			_,frame=cap.read()
			if (frame is None):
				break
			out.write(frame)
			if (cv2.waitKey(1)&0xff==27):
				break
		cap.release()
		out.release()
		return self



	def iterator(self):
		return VideoIterator(self)



	@staticmethod
	def from_JSON(json):
		v=Video(json.src)
		for k in json.effects.__iter__():
			d=json.effects[k]
			if (not hasattr(Video,"set_"+k)):
				print("Invalid effect: "+k)
				continue
			if (k=="crop"):
				v.set_crop(d.start,d.end)
			elif (k=="speed"):
				v.set_speed(d)
			elif (k=="fps"):
				v.set_fps(d)
		return v
	def to_JSON(self):
		return {"type":"video","src":self.src,"effects":{"crop":self.properties.crop,"speed":self.properties.speed,"fps":self.properties.fps}}



	@staticmethod
	def list(d,c=lambda f:True):
		return [os.path.abspath(os.path.join(d,f)) for f in os.listdir(d) if f[len(f)-4:] in Video.valid_formats() and c(f)]
	@staticmethod
	def valid_formats():
		return [".mov",".mp4",".avi"]
	@staticmethod
	def null_frame(size):
		return np.zeros((size[1],size[0],3),np.uint8)



class VideoIterator:
	def __init__(self,v):
		self.v=v
		self.step=-1
		self.total=self.v.properties.crop.end-self.v.properties.crop.start
		self.done=False
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"video.VideoIterator(target={self.v}, step={self.step} total_steps={self.total})"



	def get(self):
		if (self.step==-1 or self.step>=self.total):
			self.done=True
			return None
		cap=cv2.VideoCapture(self.v.src)
		cap.set(1,(self.step+self.v.properties.crop.start))
		_,f=cap.read()
		cap.release()
		return f



	def start(self):
		self.step=max(self.step,0)



	def next(self):
		if (self.step==-1):
			return
		self.step+=1
		if (self.step>=self.total):
			self.done=True