# Tests to read in stream
import pyaudio
import matplotlib
import matplotlib.pyplot as plt
import struct

matplotlib.use("macosx")
p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    print "Device:", i
    print p.get_device_info_by_index(i)["name"]

for c1 in [512, 2048, 4096, 8192]:
    print c1
    for c2 in [512, 2048, 4096, 8192]:
        print "\t", c2
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=c1)
        try:
            st = ""
            l = 0
            for i in range(0, int(44100 / 1024 * 2)):
                print "chunk:", c2, stream.get_read_available()
                data = stream.read(c2)
                st += data
                l += c2
            data2 = struct.unpack("%if" % l, st)
            plt.plot(data2)
            plt.show()
        except Exception as err:
            print "boooooooo"
        stream.stop_stream()
        stream.close()
