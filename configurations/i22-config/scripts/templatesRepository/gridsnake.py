hornum=5
vernum=2

horspace=20
verspace=20

originx= -30.7
originy1=62.4
originy2=112.3

## open shutter?
print "starting"
for row in range(vernum):
    pos base_y originy1+(verspace*row)
    for vcol in range(hornum):
        if row % 2 == 0:
            col = vcol
        else:
            col = hornum - 1 - vcol
        pos base_x originx+(horspace*col)
        sample = "row %02d column %02d" % (row + 1, col +1)
        setTitle(sample)
        print "exposing: "+sample
        staticscan ncddetectors
        #rscan base_y -0.5 0.5 0.5 base_x -0.5 0.5 0.5 ncddetectors base_x base_y
        
for row in range(vernum):
    pos base_y originy2+(verspace*row)
    for vcol in range(hornum):
        if row % 2 == 0:
            col = vcol
        else:
            col = hornum - 1 - vcol
        pos base_x originx+(horspace*col)
        sample = "row %02d column %02d" % (row + 1, col +1)
        setTitle(sample)
        print "exposing: "+sample
        staticscan ncddetectors
        #rscan base_y -0.5 0.5 0.5 base_x -0.5 0.5 0.5 ncddetectors base_x base_y
## close shutter?
## close shutter?
print "done"

pos base_x originx base_y originy1 