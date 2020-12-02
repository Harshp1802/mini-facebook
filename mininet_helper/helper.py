for i in range(32):
    f = open('input' + str(i+1) + '.txt','a')
    f.write("2\n")
    f.write("iit{}\n".format(str(i+1)))
    f.write("pass{}\n".format(str(i+1)))
    f.write("pass{}\n".format(str(i+1)))
    f.write("0\n")
    f.write("0\n")
    f.close()