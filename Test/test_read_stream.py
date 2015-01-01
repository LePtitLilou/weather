#Tests to read in stream 

for c1 in [512,2048,4096,8192,16384]:
  for c2 in [512,2048,4096,8192,16384]:
    stream = p.open(format = pyaudio.paInt16,channels=2,rate=44100,input=True,frames_per_buffer=c1)
    try:
      for i in range(0,int(44100/1024*2)):
        data = stream.read(c2)
        pass
      except:
        print "boooooooo"
      stream.stop_stream()
      stream.close()

