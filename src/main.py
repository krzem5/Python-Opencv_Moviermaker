import moviemaker



if (__name__=="__main__"):
	c=moviemaker.Compiler()
	c.from_JSON("./assets/v.json")
	moviemaker.Video("./output2.mp4").preview()
