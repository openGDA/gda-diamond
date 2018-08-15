print "Conditioning pyrocarbon in slot 4 to 4e-7 mbar"
pos s1_xgap 0
pos s1_ygap 6
pos d1motor 60.5
deg=Degas(s1_xgap, 6.000, gauge02, 4e-7, P=1e5, I=10000)
deg.run()

print "Conditioning pyrocarbon in slot 5 to 4e-7 mbar"
pos s1_xgap 0
pos s1_ygap 6
pos d1motor 77.53
deg=Degas(s1_xgap, 6.000, gauge02, 4e-7, P=1e5, I=10000)
deg.run()

print "Conditioning pyrocarbon in slot 6 to 4e-7 mbar"
pos s1_xgap 0
pos s1_ygap 6
pos d1motor 93.00
deg=Degas(s1_xgap, 6.000, gauge02, 4e-7, P=1e5, I=10000)
deg.run()

print "Conditioning pyrocarbon in slot 4 to 8e-8 mbar"
pos s1_xgap 0
pos s1_ygap 6
pos d1motor 60.5
deg=Degas(s1_xgap, 6.000, gauge02, 8e-8, P=1e5, I=10000)
deg.run()

print "Conditioning pyrocarbon in slot 5 to 8e-8 mbar"
pos s1_xgap 0
pos s1_ygap 6
pos d1motor 77.53
deg=Degas(s1_xgap, 6.000, gauge02, 8e-8, P=1e5, I=10000)
deg.run()

print "Conditioning pyrocarbon in slot 6 to 8e-8 mbar"
pos s1_xgap 0
pos s1_ygap 6
pos d1motor 93.00
deg=Degas(s1_xgap, 6.000, gauge02, 8e-8, P=1e5, I=10000)
deg.run()

print "All done!"