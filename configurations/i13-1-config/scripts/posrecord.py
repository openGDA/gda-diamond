'''posrecord.py
reads and write positions to/from files
'''
def __init__():
    pass

def poswrite(posns,fname):
#     print "hello"
    with open(fname,"w") as f:
        for x in posns:
#             print x
            f.write(`x` + "\n")
    f.close()