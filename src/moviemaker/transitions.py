import cv2
import numpy as np



class _Transition:
	def __init__(self,type_,null_frame_c):
		self.t=type_
		self.null_frame_c=null_frame_c
		self.transition=True
	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return f"moviemaker.transition.Transition.{self.t.title()}(type={self.t}, null_frame_count={self.null_frame_c})"



	def get_frame_count(self):
		return self.null_frame_c



	def to_JSON(self):
		return {"type":"transition","name":self.t.lower()}



	def run(self,f,m,i,s,p):
		return f



class _Jump(_Transition):
	def __init__(self):
		super().__init__("jump",0)
	def run(self,frame,mode,index,size,fps):
		return frame



class _Flythrough(_Transition):
	def __init__(self):
		super().__init__("flythrough",10)
	def run(self,frame,mode,index,size,fps):
		def map(v,aa,ab,ba,bb):
			return (v-aa)/(ab-aa)*(bb-ba)+ba
		start_small_buffor_min=13
		start_small_buffor_max=7
		end_small_buffor_min=9
		end_small_buffor_max=3
		small_tb_diff=100
		small_w=100
		main_buffor=10
		main_tb_diff=100
		w=size[0]
		h=size[1]
		c=(240,240,240)
		if (mode==0):
			if (index<=start_small_buffor_min):
				x=map(index,start_small_buffor_min,start_small_buffor_max,w,-small_tb_diff)
				pts=np.array([[x,0],[x+small_w+small_tb_diff,0],[x+small_w+small_tb_diff*2,h],[x+small_tb_diff,h]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
			if (index<=main_buffor):
				x=map(index,main_buffor,0,w,-main_tb_diff)
				pts=np.array([[x,0],[x+w+main_tb_diff,0],[x+w+main_tb_diff*2,h],[x+main_tb_diff,h]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
		if (mode==1):
			if (index<=end_small_buffor_min):
				x=map(index,end_small_buffor_min,end_small_buffor_max,-small_tb_diff,w)
				pts=np.array([[x,0],[x+small_w+small_tb_diff,0],[x+small_w+small_tb_diff*2,h],[x+small_tb_diff,h]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
			if (index<=main_buffor):
				x=map(index,main_buffor,0,0,w+main_tb_diff)
				pts=np.array([[x,h],[x-main_tb_diff,0],[x-w-main_tb_diff*2,0],[x-w-main_tb_diff,h]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
		return frame



class _Flythrough_Inverted(_Transition):
	def __init__(self):
		super().__init__("flythrough_inverted",10)
	def run(self,frame,mode,index,size,fps):
		def map(v,aa,ab,ba,bb):
			return (v-aa)/(ab-aa)*(bb-ba)+ba
		start_small_buffor_min=13
		start_small_buffor_max=7
		end_small_buffor_min=9
		end_small_buffor_max=3
		small_tb_diff=100
		small_w=100
		main_buffor=10
		main_tb_diff=100
		w=size[0]
		h=size[1]
		c=(240,240,240)
		if (mode==0):
			if (index<=start_small_buffor_min):
				x=map(index,start_small_buffor_min,start_small_buffor_max,w,-small_tb_diff)
				pts=np.array([[x,h],[x+small_w+small_tb_diff,h],[x+small_w+small_tb_diff*2,0],[x+small_tb_diff,0]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
			if (index<=main_buffor):
				x=map(index,main_buffor,0,w,-main_tb_diff)
				pts=np.array([[x,h],[x+w+main_tb_diff,h],[x+w+main_tb_diff*2,0],[x+main_tb_diff,0]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
		if (mode==1):
			if (index<=end_small_buffor_min):
				x=map(index,end_small_buffor_min,end_small_buffor_max,-small_tb_diff,w)
				pts=np.array([[x,h],[x+small_w+small_tb_diff,h],[x+small_w+small_tb_diff*2,0],[x+small_tb_diff,0]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
			if (index<=main_buffor):
				x=map(index,main_buffor,0,0,w+main_tb_diff)
				pts=np.array([[x,0],[x-main_tb_diff,h],[x-w-main_tb_diff*2,h],[x-w-main_tb_diff,0]],np.int32).reshape((-1,1,2))
				cv2.fillPoly(frame,[pts],c)
		return frame



class Transition:
	default=_Jump
	Jump=_Jump
	Flythrough=_Flythrough
	Flythrough_Inverted=_Flythrough_Inverted



	@staticmethod
	def from_JSON(json):
		n=json.name.split("_")
		i=0
		for s in n:
			n[i]=s.title()
			i+=1
		n="_".join(n)
		if (hasattr(Transition,n)):
			return getattr(Transition,n)()
		print("Invalid transition: "+n)
		return Transition.default()