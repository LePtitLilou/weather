#Tests to read in stream 
import pyaudio
import matplotlib
matplotlib.use("macosx")
import matplotlib.pyplot as plt
import struct

p = pyaudio.PyAudio()

c1=512
c2=512

def create_stream(fpb=512,rate=44100,device=0):
  return p.open(format = pyaudio.paFloat32,channels=1,rate=44100,input=True,
      frames_per_buffer=fpb,start=False)#,input_device_index=device)

def read_N_sec(n,inStream=None,chunks=8192,device=0):
  if inStream is None:
    stream = create_stream(device=device)
  else:
    stream = inStream
  fpb = stream._frames_per_buffer
  rate= stream._rate
  st=""
  l=0
  N = int(n*rate/float(fpb))
  R = stream.get_read_available()
  print "Rate: %i, FpB: %i, Record Time:%i, Reads:%i" % (rate,fpb,n,N)
  print "Time:",stream.get_time(),R
  print "Chunks:",chunks
  stream.start_stream()
  for i in range(0,N):
    data = stream.read(chunks)
    st+=data
    l+=chunks
  data2 = struct.unpack("%if"%l,st)
  stream.stop_stream()
  if inStream is None:
    stream.close()
  return data2

## Ok now testing reading in a few seconds
stream = create_stream(c1)
n=input("How many seconds to you want to record?")
data = read_N_sec(n,stream,c2)
plt.plot(data)
plt.show()

stream.stop_stream()
stream.close()
