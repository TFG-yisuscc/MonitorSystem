from Metrics.VGENMetrics import *
from Metrics.mpstatMetrics import *
import time
m = mpstatMetrics()
v = VCGENMetrics()
while True:
    m.update()
    v.update()
    print(m.__str__())
    print(v.__str__())
    time.sleep(1)
