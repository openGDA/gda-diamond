
#For m7 Hexapod legs
m7leg1.setOutputFormat(["%10.6f"]);
m7leg2.setOutputFormat(["%10.6f"]);
m7leg3.setOutputFormat(["%10.6f"]);
m7leg4.setOutputFormat(["%10.6f"]);
m7leg5.setOutputFormat(["%10.6f"]);
m7leg6.setOutputFormat(["%10.6f"]);

#To add branchline device position to the SRS file header
branchMirrorList = [m7x, m7pitch, m7qg]; fileHeader.add(branchMirrorList);

branchDiodeList = [d9y, d10y, d11y]; fileHeader.add(branchDiodeList);

branchExitSlitList = [s6y, s6ygap]; fileHeader.add(branchExitSlitList);
