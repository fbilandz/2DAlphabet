import os
import math
import ROOT
from ROOT import * 

class LinearFit:

  def __init__(self, init_var, range_min, range_max, name, Opt):
    self.Opt = Opt
    self.rm = range_min
    self.rp = range_max
    self.name = name
    self.fit = TF1("LinearFit_"+self.name, "[0]+ [1]*x",self.rm,self.rp)
    self.fit.SetParameter(0, init_var[0]) 
    self.fit.SetParameter(1, init_var[0])
  def Converter(self, fitter):
    self.ErrUp = TF1("QuadrarticFitErrorUp"+self.name, "[0]+ [1]*x + sqrt(([2]*[2]) + (2*x*[5]) + (x*x*[3]*[3]))",self.rm,self.rp)
    self.ErrUp.SetParameter(0, self.fit.GetParameter(0))
    self.ErrUp.SetParameter(1, self.fit.GetParameter(1))
    self.ErrUp.SetParameter(2, self.fit.GetParErrors()[0])
    self.ErrUp.SetParameter(3, self.fit.GetParErrors()[1])
    self.ErrUp.SetParameter(4, fitter.CovMatrix(0,1))
    self.ErrDn = TF1("QuadrarticFitErrorDn"+self.name, "[0]+ [1]*x - sqrt(([2]*[2]) + (2*x*[5]) + (x*x*[3]*[3]))",self.rm,self.rp)
    self.ErrDn.SetParameter(0, self.fit.GetParameter(0))
    self.ErrDn.SetParameter(1, self.fit.GetParameter(1))
    self.ErrDn.SetParameter(2, self.fit.GetParErrors()[0])
    self.ErrDn.SetParameter(3, self.fit.GetParErrors()[1])
    self.ErrDn.SetParameter(4, fitter.CovMatrix(0,1))
    # def MakeConvFactor(self, var, center):
    #   X = var + "-" + str(center)
    #   self.ConvFact = "({0:4.18f} + (({3})*{1:4.18f}) + (({3})*({3})*{2:4.18f}))".format(self.ErrUp.GetParameter(0),self.ErrUp.GetParameter(1),self.ErrUp.GetParameter(2),X)
    #   self.ConvFactUp = "({0:4.18f} + (({9})*{1:4.18f}) + (({9})*({9})*{2:4.18f}) + (({3:4.18f}*{3:4.18f}) + (2*({9})*{6:4.18f}) + (({9})*({9})*{4:4.18f}*{4:4.18f}) + (2*({9})*({9})*{7:4.18f}) + (2*({9})*({9})*({9})*{8:4.18f}) + (({9})*({9})*({9})*({9})*{5:4.18f}*{5:4.18f}))^0.5)".format(self.ErrUp.GetParameter(0),self.ErrUp.GetParameter(1),self.ErrUp.GetParameter(2),self.ErrUp.GetParameter(3),self.ErrUp.GetParameter(4),self.ErrUp.GetParameter(5),self.ErrUp.GetParameter(6),self.ErrUp.GetParameter(7),self.ErrUp.GetParameter(8),X)
    #   self.ConvFactDn = "({0:4.18f} + (({9})*{1:4.18f}) + (({9})*({9})*{2:4.18f}) - (({3:4.18f}*{3:4.18f}) + (2*({9})*{6:4.18f}) + (({9})*({9})*{4:4.18f}*{4:4.18f}) + (2*({9})*({9})*{7:4.18f}) + (2*({9})*({9})*({9})*{8:4.18f}) + (({9})*({9})*({9})*({9})*{5:4.18f}*{5:4.18f}))^0.5)".format(self.ErrUp.GetParameter(0),self.ErrUp.GetParameter(1),self.ErrUp.GetParameter(2),self.ErrUp.GetParameter(3),self.ErrUp.GetParameter(4),self.ErrUp.GetParameter(5),self.ErrUp.GetParameter(6),self.ErrUp.GetParameter(7),self.ErrUp.GetParameter(8),X)
