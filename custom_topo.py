from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import *
from mininet.node import OVSController
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.clean import cleanup   
import time
from multiprocessing.pool import ThreadPool as Pool


class CustomTopo( Topo ):
    def __init__(self):
        Topo.__init__(self)
        S = self.addHost("s1")
        A1 = self.addSwitch("a1")
        B1 = self.addSwitch("b1")
        B2 = self.addSwitch("b2")

        for i in range(1,5):
            exec("C{} = self.addSwitch('c{}')".format(i,i))

        for i in range(1,9):
            exec("D{} = self.addSwitch('d{}')".format(i,i))

        for i in range(1,17):
            exec("E{} = self.addSwitch('e{}')".format(i,i))
        
        for i in range(1,33):
            exec("H{} = self.addHost('h{}')".format(i,i))

        bandwidth = 800

        self.addLink(S,A1,bw=bandwidth)
        self.addLink(A1,B1,bw=bandwidth/2)
        self.addLink(A1,B2,bw=bandwidth/2)

        for i in range(1,3):
            exec("self.addLink(B{}, C{}, bw=bandwidth/4)".format(i,2*(i-1) + 1))
            exec("self.addLink(B{}, C{}, bw=bandwidth/4)".format(i,2*(i-1) + 2))
        
        for i in range(1,5):
            exec("self.addLink(C{}, D{}, bw=bandwidth/8)".format(i,2*(i-1) + 1))
            exec("self.addLink(C{}, D{}, bw=bandwidth/8)".format(i,2*(i-1) + 2))

        for i in range(1,9):
            exec("self.addLink(D{}, E{}, bw=bandwidth/16)".format(i,2*(i-1) + 1))            
            exec("self.addLink(D{}, E{}, bw=bandwidth/16)".format(i,2*(i-1) + 2))

        for i in range(1,17):
            exec("self.addLink(E{}, H{}, bw=bandwidth/32)".format(i,2*(i-1) + 1))
            exec("self.addLink(E{}, H{}, bw=bandwidth/32)".format(i,2*(i-1) + 2))
        
if __name__ == "__main__":
    setLogLevel("info")
    topo = CustomTopo()
    net = Mininet(topo,link = TCLink, controller = OVSController)
    net.start()
    print(net.hosts)
    net.hosts[-1].sendCmd("python3 server_mini.py &")
    print("Starting Server")

    for i in range(32):
        net.hosts[i].sendCmd("python3 client.py {} &".format(i+1))
    time.sleep(5)
    cleanup()