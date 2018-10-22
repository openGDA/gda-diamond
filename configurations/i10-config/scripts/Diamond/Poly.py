"""
Polynomial evaluator for use with GDA at Diamond Light Source
"""
    
class Poly(list):
    def __init__(self, coeffs, power0first=False):
        # self.coeffs are powers degree .. 0, i.e. power)first=False 
        if power0first:
            coeffs.reverse()
        if len(coeffs) == 0:
            coeffs = [0]
        self.coeffs = coeffs
        self.degree = len(self.coeffs)-1
        
    def __repr__(self):
        terms = [str(coeff) for coeff in self.coeffs]
        return "Poly(coeffs=[" + ", ".join(terms) + "], power0first=False)"
    
    def __str__(self):
        # self.coeffs are powers degree .. 0
        terms = ["(("+str(self.coeffs[i])+")*x**"+str(self.degree-i)+")" \
                 for i in range(len(self.coeffs)) \
                 if self.coeffs[i]<>0]
        return "0" if len(terms)==0 else "+".join(terms)
        
    def __call__(self,val):    
        return apply(eval("lambda x:" + self.__str__()), (val,))
