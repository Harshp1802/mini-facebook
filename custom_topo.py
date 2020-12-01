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
        S = self.addHost("h1")
        A1 = self.addSwitch("a1")
        B1 = self.addSwitch("b1")
        B2 = self.addSwitch("b2")

        for i in range(1,5):
            exec("C{} = self.addHost('c{}')".format(i,i))
        # C1 = self.addSwitch("c1")
        # C2 = self.addSwitch("c2")
        # C3 = self.addSwitch("c3")
        # C4 = self.addSwitch("c4")

        for i in range(1,9):
            exec("D{} = self.addHost('d{}')".format(i,i))
        # D1 = self.addSwitch("d1")
        # D2 = self.addSwitch("d2")
        # D3 = self.addSwitch("d3")
        # D4 = self.addSwitch("d4")
        # D5 = self.addSwitch("d5")
        # D6 = self.addSwitch("d6")
        # D7 = self.addSwitch("d7")
        # D8 = self.addSwitch("d8")

        for i in range(1,17):
            exec("E{} = self.addHost('e{}')".format(i,i))
        # E1 = self.addSwitch("e1")
        # E2 = self.addSwitch("e2")
        # E3 = self.addSwitch("e3")
        # E4 = self.addSwitch("e4")
        # E5 = self.addSwitch("e5")
        # E6 = self.addSwitch("e6")
        # E7 = self.addSwitch("e7")
        # E8 = self.addSwitch("e8")
        # E9 = self.addSwitch("e9")
        # E10 = self.addSwitch("e10")
        # E11 = self.addSwitch("e11")
        # E12 = self.addSwitch("e12")
        # E13 = self.addSwitch("e13")
        # E14 = self.addSwitch("e14")
        # E15 = self.addSwitch("e15")
        # E16 = self.addSwitch("e16")
        
        for i in range(1,33):
            exec("H{} = self.addHost('h{}')".format(i,i))
        # H1 = self.addHost("h1")
        # H2 = self.addHost("h2")
        # H3 = self.addHost("h3")
        # H4 = self.addHost("h4")
        # H5 = self.addHost("h5")
        # H6 = self.addHost("h6")
        # H7 = self.addHost("h7")
        # H8 = self.addHost("h8")
        # H9 = self.addHost("h9")
        # H10 = self.addHost("h10")
        # H11 = self.addHost("h11")
        # H12 = self.addHost("h12")
        # H13 = self.addHost("h13")
        # H14 = self.addHost("h14")
        # H15 = self.addHost("h15")
        # H16 = self.addHost("h16")
        # H17 = self.addHost("h17")
        # H18 = self.addHost("h18")
        # H19 = self.addHost("h19")
        # H20 = self.addHost("h20")
        # H21 = self.addHost("h21")
        # H22 = self.addHost("h22")
        # H23 = self.addHost("h23")
        # H24 = self.addHost("h24")
        # H25 = self.addHost("h25")
        # H26 = self.addHost("h26")
        # H27 = self.addHost("h27")
        # H28 = self.addHost("h28")
        # H29 = self.addHost("h29")
        # H30 = self.addHost("h30")
        # H31 = self.addHost("h31")
        # H32 = self.addHost("h32")

        bandwidth = 800

        self.addLink(S,A1,bw=bandwidth)
        self.addLink(A1,B1,bw=bandwidth/2)
        self.addLink(A1,B2,bw=bandwidth/2)

        for i in range(1,3):
            exec("self.addLink(B{}, C{}, bw=bandwidth/4)".format(i,2*(i-1) + 1))
        
        for i in range(1,5):
            exec("self.addLink(C{}, D{}, bw=bandwidth/8)".format(i,2*(i-1) + 1))

        for i in range(1,9):
            exec("self.addLink(D{}, E{}, bw=bandwidth/16)".format(i,2*(i-1) + 1))            

        for i in range(1,17):
            exec("self.addLink(E{}, H{}, bw=bandwidth/32)".format(i,2*(i-1) + 1))

        

def xecute(X):
    h = X[0]
    i = X[1]
    print("Exec" ,i)
    h[i].sendCmd("python3 tcp_client_" + str(i) +"_mini.py")
    return "Done"

if __name__ == "__main__":
    setLogLevel("info")
    topo = CustomTopo()
    net = Mininet(topo,link = TCLink, controller = OVSController)
    net.start()
    net.pingAll()
    h1 = net.hosts[0]
    h1.sendCmd("python3 tcp_threadserver_mini.py")
    print("Starting")
    p = Pool(6)
    print(net.hosts)
    result = p.map(xecute, [[net.hosts, i] for i in [1, 4, 6, 7]])
    time.sleep(20)
    net
    cleanup()