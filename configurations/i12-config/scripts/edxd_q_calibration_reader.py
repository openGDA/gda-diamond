'''
Created on 20 Sep 2011

@author: ssg37927
'''
import os
import scisoftpy as dnp


def load_edxd_q_calibration_file(filename):
    f = open(filename)
    elements = {}
    for line in f:
        vals = line.split(',')
        element = int(vals[0])
        a = float(vals[1])
        b = float(vals[2])
        c = float(vals[3])
        elements[element] = (a,b,c)
    return elements

def generate_element_q_axis(elements, element_number, size):
    result = []
    a = elements[element_number][0]
    b = elements[element_number][1]
    c = elements[element_number][2]
    for i in range(size):
        result.append(a*i*i + b*i + c)
    return result

def create_example_output(filename, nxsFileName, outputDir):
    datapoints = dnp.io.load(nxsFileName)
    elements = load_edxd_q_calibration_file(filename)
    for i in range(1,24):
        data = datapoints["/entry1/EDXD_Element_%02i/data" % i]
        data = data[...]
        counts = data.sum(0)
        axis = generate_element_q_axis(elements, i, counts.shape[0])
        file = open(os.path.join(outputDir, "element_%02i.dat" % i), 'w')
        for j in range(counts.shape[0]):
            file.write("%f, %f\n"% (axis[j], counts.get([j])))
        file.close()
        dnp.plot.line(dnp.array(axis), dnp.array(counts))

def set_edxd_q_calibration(filename, detector):
    vals = load_edxd_q_calibration_file(filename)
    for i in range(0,23):
        q = dnp.array(generate_element_q_axis(vals, i+1, 4096))
        detector.getSubDetector(i).setQMapping(q.data)
    print "setting detector element ", i
    # Set a fake data for the 24th element
    q = dnp.array(generate_element_q_axis(vals, 1, 4096))
    detector.getSubDetector(23).setQMapping(q.data)
    print "finished calibration"

if __name__ == "__main__" :
    print "testing"
    import pprint
    vals = load_edxd_q_calibration_file("/tmp/test.txt")
    pprint.pprint(vals)
    import scisoftpy as dnp
    x = dnp.arange(4096)
    y1 = dnp.array(generate_element_q_axis(vals, 1, 4096))
    y2 = dnp.array(generate_element_q_axis(vals, 5, 4096))
    y3 = dnp.array(generate_element_q_axis(vals, 10, 4096))
    y4 = dnp.array(generate_element_q_axis(vals, 15, 4096))
    y5 = dnp.array(generate_element_q_axis(vals, 20, 4096))
    dnp.plot.line(x,[y1, y2, y3, y4, y5])
    
    create_example_output("/tmp/test.txt","/home/ssg37927/sda/edxd/test_data/6600.nxs" , "/tmp/")
    
    
