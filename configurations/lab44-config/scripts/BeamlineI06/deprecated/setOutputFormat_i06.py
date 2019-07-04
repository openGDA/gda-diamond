
#For m3 Hexapod legs
m3leg1.setOutputFormat(["%10.6f"]);
m3leg2.setOutputFormat(["%10.6f"]);
m3leg3.setOutputFormat(["%10.6f"]);
m3leg4.setOutputFormat(["%10.6f"]);
m3leg5.setOutputFormat(["%10.6f"]);
m3leg6.setOutputFormat(["%10.6f"]);

#To add extra device position to the SRS file header

#To add branchline device position to the SRS file header
peemMirrorList = [m3x, m3pitch, m3qg]; fileHeader.add(peemMirrorList);

peemDiodeList = [d5x, d6y, d7x, d7ax]; fileHeader.add(peemDiodeList);

peemExitSlitList = [s4y, s4ygap]; fileHeader.add(peemExitSlitList);
