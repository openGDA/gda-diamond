# NEED TO FIX PROBLEM OF PNAME STRING EXISTING WITHIN A DIFFERENT PNAME - LOOK AT TOKENS?

import numpy as np
import copy
try:
    from lmfit import minimize, Parameters, Parameter, report_fit
except:
    print "=== lmfit must be installed. Try 'easy_install -U lmfit' from terminal "

class fit_func():
    #method to add multiple fit functions
    def __init__(self,name,pnames,funcstring,initfuncstring=None):
        '''
        A wrapper for curve fitting with the lmfit package. This class creates a fit function from strings.
        'name': name of the function
        'pnames': a list of paramater name strings
        'funcstring': function definition as a string in terms of pnames 
        'initfuncstring' string expression which assigns initial values to the paramaters
                
        After fitting:
            self.p gives the parameter values
            self.err gives error estimates
        For a report on the fit type report_fit(self.params)

        main user methods:
            fit:        do a fit
            __repr__:   standard string representation of function and parameters
            __call__:   evaluate fit function
            
        Caveat: variable name strings must not be sub-strings of any of the names in expression given
            i.e. var and var1 cannot be used but var1 and var2 is OK
            Quickfit needs coding properly by a grown-up
        '''
        self.name=name
        self.pnames=pnames
        self.funcstring=funcstring
        self.params=Parameters()
        self.method='leastsq' #default fitting routine    
        self.initfuncstring=initfuncstring
        self.p=np.zeros(len(self.pnames))
        self.errors=np.zeros(len(self.pnames))
        self.maxchar=0
        for name in self.pnames:        
            self.params.add(name)   #create parameters from parameter names
            if len(name)>self.maxchar:
                self.maxchar=len(name)
        #convert functring (then initfuncstring) to full explicit form for evaluation
        self.funcstring_full=self.funcstring
        for name in self.pnames: 
            self.funcstring_full=self.funcstring_full.replace(name,"self.params['"+name+"'].value")       
        if self.initfuncstring!=None:
            self.initfuncstring_full=self.initfuncstring
            for name in self.pnames: 
                self.initfuncstring_full=self.initfuncstring_full.replace(name,"self.params['"+name+"'].value")       
   
    def __call__(self,x):
        'self(x) evaluates function over values in x'
        #print '\nString to evaluate:\n'+self.funcstring_full
        return eval(self.funcstring_full)

    def get_init_params(self,x,y,pin=None):
        #print "pin:", pin        
        pin=copy.copy(pin)   # otherwise it is eaten
        if pin==None or pin=='new': #get new initial values
            if self.initfuncstring!=None:
                exec(self.initfuncstring_full)
            else:
                for name in self.pnames: #set initial params to zero
                    self.params[name].value=0                 
        elif pin=='keep':
            pass            #keep current values           
        elif pin != None:               #use specifie values
            for name in self.pnames: 
                self.params[name].value=pin.pop(0)   #assign specified values        

    def minfunc(self,params,x,y):
        #function to minimize
        self.params=params
        return self(x)-y
        
    def fit(self, x, y, pin=None):
        self.get_init_params(x, y, pin)
        self.result = minimize(self.minfunc, self.params, method=self.method, args=(x, y))
        self.p=[self.params[name].value for name in self.pnames]
        self.err=[self.params[name].stderr for name in self.pnames]
        return self.__repr__()  #return string representation of fit summary
        
    def __repr__(self): #nice string output
        #This might be improved by substituting largest strings first, one by one, and checking for syntax error
        self.out='Function name: '+self.name+'\n'
        for name in self.pnames:
            self.out+='%-10s:  ' % name+str(self.params[name].value)+' +/- '+str(self.params[name].stderr)+'\n'
        return self.out 
            

testfunc=fit_func('wavy line',['amp','omega','shift','decay'],
                    'amp*np.sin(x*omega+shift)*np.exp(-x*x*decay)',
                    'amp,omega,shift,decay=10,.1,.4,3')
                    
gauss_c=fit_func('gaussian + const',['area','centre','width','constant'],
                    'area/width*np.sqrt(4*np.log(2)/np.pi)*np.exp(-4*np.log(2)*((x-centre)/width)**2)+constant',
                    '[centre, width, sum, height, area, m, c, constant]=peak(x,y)')

###### syntax agreed as an example fit function at scisoft meeting 12/2/14 ########
# def gauss_c(x,area,centre,width,constant):
#     return area/width*np.sqrt(4*np.log(2)/np.pi)*np.exp(-4*np.log(2)*((x-centre)/width)**2)+constant
# def gaus_init(x,y):
#     centre, width, sum, height, area, m, c, constant=peak(x,y)')
#     return [centre, width, sum, height, area, m, c, constant]
# gauss_c_new=fit_func(gauss_c, 'gaussian + const',['area','centre','width','constant'],




                    
lor_c=fit_func('Lorentzian + const',['area','centre','width','constant'],                   
                'area/width/(np.pi/2)/(1+4*((x-centre)/width)**2)+constant',
                '[centre, width, sum, height, area, m, c, constant]=peak(x,y)')            
                
pv_c=fit_func('Pseudo-Voigt + const',['area','centre','width','lfrac','constant'],
              'area/width/(lfrac*np.pi/2+(1-lfrac)*np.sqrt(np.pi/4/np.log(2)))*(lfrac/(1+4*((x-centre)/width)**2)+(1-lfrac)*np.exp(-4*np.log(2)*((x-centre)/width)**2))+constant',
              '[centre, width, sum, height, area, m, c, constant]=peak(x,y); lfrac=1')  

pv_l=fit_func('Pseudo-Voigt + line',['area','centre','width','lfrac','cx', 'mx'],
              'area/width/(lfrac*np.pi/2+(1-lfrac)*np.sqrt(np.pi/4/np.log(2)))*(lfrac/(1+4*((x-centre)/width)**2)+(1-lfrac)*np.exp(-4*np.log(2)*((x-centre)/width)**2))+cx+mx*x',
              '[centre, width, sum, height, area, m, cc, constant]=peak(x,y); lfrac=1; mx=0; cx=0')  

              
g_plus_l_c=fit_func('PV + gaussian + const',['centre','areag','widthg', 'areal','widthl','constant'],
                    'areag/widthg*np.sqrt(4*np.log(2)/np.pi)*np.exp(-4*np.log(2)*((x-centre)/widthg)**2)+areal/widthl/(np.pi/2)/(1+4*((x-centre)/widthl)**2)+constant',
                    '[centre, widthg, sum, height, areag, m, c, constant]=peak(x,y); areal=areag/4; widthl=widthg')                    

cos_c=fit_func('cosine + const',['amp','period','phase', 'constant'], 'amp*np.cos(2*np.pi*(x-phase)/period)+constant')

pv2_c=fit_func('Two Pseudo-Voigt + const',['area1','centre1','width1','lfrac1','area2','centre2','width2','lfrac2','constant'],
              'area1/width1/(lfrac1*np.pi/2+(1-lfrac1)*np.sqrt(np.pi/4/np.log(2)))*(lfrac1/(1+4*((x-centre1)/width1)**2)+(1-lfrac1)*np.exp(-4*np.log(2)*((x-centre1)/width1)**2))+area2/width2/(lfrac2*np.pi/2+(1-lfrac2)*np.sqrt(np.pi/4/np.log(2)))*(lfrac2/(1+4*((x-centre2)/width2)**2)+(1-lfrac2)*np.exp(-4*np.log(2)*((x-centre2)/width2)**2))+constant'
              )

cos_sin_cos_sin_c=fit_func('cosx + sinx +cos2x +sin2x + const',['cosx_amp','sinx_amp','cos2x_amp','sin2x_amp','constant'],
              'cosx_amp*np.cos(x) + sinx_amp*np.sin(x) + cos2x_amp*np.cos(2*x) + sin2x_amp*np.sin(2*x) + constant'
              )  



#def cos_c_fun1(x,p):
#    'amplitude can be -ve - useful if phase fixed'
#    return p[0]*cos(2*pi*(x-p[2])/p[1])+p[3] 


def peak(xdat,ydat,nbgpts=1):
    '''
    [centre, width, sum, height, area, m, c, bg]=peak(x,y,nbgpts=1)
    Returns centre, width, sum, height, area after subtracting a sloping
    linear background from the fist and nbgpts data points, the background parameters (m, c)
    and the mean background (bg)
    The width is derived from the standard deviation, asuming a gaussian shape
    xdat, ydat are 1d arrays or lists
    '''
    #print 'in peak=============',type(array)
    x=np.array(xdat); 
    y=np.array(ydat); 
    npts=len(x); 
    xspan=x[-1]-x[0];                    #copy data into arrays
    m=(np.mean(y[npts-nbgpts:npts])-np.mean(y[0:nbgpts]))/(np.mean(x[npts-nbgpts:npts])-np.mean(x[0:nbgpts]))    #slope for linear b/g
    c=np.mean(y[0:nbgpts])-np.mean(x[0:nbgpts])*m;                            #intercept
    y=y-m*x-c;                                            #subtract background
    sumdat=sum(y);                                            #peak sum
    area=sumdat*xspan/npts;                                        #peak integral
    centre=sum(x*y)/sumdat;                                    #centroid calc.
    sigma=np.sqrt(sum((x-centre)**2*y)/sumdat);                            #standard deviation
    height=max(y);                                            #max y value after linear b/g
    width=sigma*np.sqrt(8*np.log(2));                                    #calculate fwhm from sd assuming normal distribution
    bg=np.mean(y[0:nbgpts]+y[npts-nbgpts:npts])                            #mean background
    return [centre, width, sumdat, height, area, m, c, bg]
                
            
     
