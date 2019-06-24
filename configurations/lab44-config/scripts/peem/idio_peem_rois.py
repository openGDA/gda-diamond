from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass

def Ratiod10(x1, x2):
    y=(x1)/(x2+1e-12);
    return y;

roi1io = DeviceFunctionClass("roi1io", "roi1","ca51sr", "Ratiod10")
roi2io = DeviceFunctionClass("roi2io", "roi2","ca51sr", "Ratiod10")
roi3io = DeviceFunctionClass("roi3io", "roi3","ca51sr", "Ratiod10")
roi4io = DeviceFunctionClass("roi4io", "roi4","ca51sr", "Ratiod10")

