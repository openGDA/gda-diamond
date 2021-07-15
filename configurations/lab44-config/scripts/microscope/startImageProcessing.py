'''
This method will be called from GDA at end of scan to start image processing and 
returns the results of this image processing to GDA for users to use.

see Config/src/externalProcess/imageProcessing.py for how it is used

Created on 8 Aug 2019

@author: xke49157
'''

def processImages(scanfilename, scannumber):
    #calling modules here
    # replace the following line with the results of image processing
    from image_stitching_program_hdf import process_stitching
    return_statement = process_stitching(scanfilename, scannumber)
    return str(return_statement)

if __name__ == '__main__':
    scanfilename = "/dls/i06/data/2019/cm22966-3/processing/optical_microscope/lab44-76.nxs"
    scannumber = 76
    image_data_path = processImages(scanfilename, scannumber)
    print(image_data_path)
