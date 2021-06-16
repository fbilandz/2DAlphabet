import ROOT as r
import numpy as np
from time import sleep
from QuadraticFit import *
from QubicFit import *

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0000)

def rebinHisto(hNameToRebin,hModel,inFile,name):
    g = r.TFile.Open(inFile)
    hToRebin = g.Get(hNameToRebin)
    hRes = hModel.Clone(name)
    hRes.Reset()
    xaxis = hToRebin.GetXaxis()
    yaxis = hToRebin.GetYaxis()
    xaxis_re = hRes.GetXaxis()
    yaxis_re = hRes.GetYaxis()
    for i in range(1,hToRebin.GetNbinsX()+1):
        for j in range(1,hToRebin.GetNbinsY()+1):
            x = xaxis.GetBinCenter(i)
            y = yaxis.GetBinCenter(j)
            i_re = xaxis_re.FindBin(x)
            j_re = yaxis_re.FindBin(y)
            value = hToRebin.GetBinContent(i,j)
            if(value<0.):
                value = 0.
            err = hToRebin.GetBinError(i,j)
            err_re = np.sqrt(hRes.GetBinError(i_re,j_re)*hRes.GetBinError(i_re,j_re)+err*err)
            hRes.Fill(x,y,value)
            hRes.SetBinError(i_re,j_re,err_re)
    hRes.SetDirectory(0)
    g.Close()
    return hRes


def get1DRpf(inputFile,outputFile,tag_pass,tag_fail,binsX=15,xLo=60,xUp=360,binsY=22,yLo=800,yUp=3000):
    #hModel   = r.TH2F("hModel","",len(customMJYbins)-1,customMJYbins,len(customMJJbins)-1,customMJJbins)
    hModel   = r.TH2F("hModel","",binsX,xLo,xUp,binsY,yLo,yUp)

    hFail = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_fail),hModel,inputFile,"QCD_{0}".format(tag_fail))
    if("LplusT" in outputFile):
        hPass = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_pass),hModel,inputFile,"QCD_{0}".format(tag_pass))
        hTemp = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_pass.replace("_L","_T")),hModel,inputFile,"QCD_{0}".format(tag_pass.replace("_L","_T")))
        hPass.Add(hTemp)
        tag_pass = tag_pass.replace("_L","_LplusT")
    else:
        hPass = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_pass),hModel,inputFile,"QCD_{0}".format(tag_pass))


    hFail1D = hFail.ProjectionX("QCD_mJY_mJJ_{0}_nom".format(tag_fail))
    hPass1D = hPass.ProjectionX("QCD_mJY_mJJ_{0}_nom".format(tag_pass))

    #customMJYbins = np.array([60.,80.,100.,120.,140.,160.,180.,200.,220.,240.,260.,300.,360.],dtype='float64')
    customMJYbins = np.array([60.,80.,100.,120.,160.,200.,240.,300.,360.],dtype='float64')
    customMJYbins = np.array([60.,80.,100.,120.,160.,220.,280.,360.],dtype='float64')#for data-driven Rpf


    customMJJbins = np.linspace(yLo,yUp,num=binsY+1,endpoint=True,dtype='float64')

    hFail1D = hFail1D.Rebin(len(customMJYbins)-1,"QCD_mJY_mJJ_{0}_nom_reb".format(tag_fail),customMJYbins)
    hPass1D = hPass1D.Rebin(len(customMJYbins)-1,"QCD_mJY_mJJ_{0}_nom_reb".format(tag_pass),customMJYbins)


    hRatio1D = hPass1D.Clone("hRatio1D_{0}".format(tag_pass))
    hRatio1D.GetXaxis().SetTitle("M_{JY} [GeV]")
    hRatio1D.GetYaxis().SetTitle("R_{P/F}")
    hRatio1D.GetYaxis().SetTitleOffset(1.3)
    hRatio1D.Divide(hFail1D)

    #TFitResult class
    #fitRes = hRatio1D.Fit("f2","S")
    #q = QuadraticFit([0.00211473, 0.00279319, 0.00933092], 60, 360, "quadfit", "EMRFNEX0")
    q = QubicFit([0.002, 0.0, 0.0,0.0], 60, 360, "qubicfit", "EMRFNEX0")
    fitRes = hRatio1D.Fit(q.fit,"S")
    chi2   = fitRes.Chi2()/fitRes.Ndf()
    print(fitRes.Chi2()/fitRes.Ndf())
    q.Converter(fitRes)
    fitfun = q.fit
    errup = q.ErrUp
    errdown = q.ErrDn
    c = ROOT.TCanvas('rpf_TT_fitted', 'c', 800, 600)
    c.cd()
    hRatio1D.SetTitle("#Chi^{2}/NDOF = %.2f" %chi2)
    hRatio1D.Draw('e1')
    hRatio1D.SetMinimum(0.0)
    hRatio1D.SetMaximum(max(hRatio1D.GetMaximum()+0.01,0.03))
    errup.SetLineStyle(4)
    errdown.SetLineStyle(4)
    errup.SetLineColor(r.kBlue)
    errdown.SetLineColor(r.kBlue)
    errup.Draw("lsame")
    errdown.Draw("lsame")
    c.SaveAs(outputFile.replace(".root",".pdf"))



    rpf_2D = hModel.Clone("rpf_{0}_{1}".format(tag_fail,tag_pass))
    rpf_2D_up = hModel.Clone("rpf_{0}_{1}_up".format(tag_fail,tag_pass))
    rpf_2D_down = hModel.Clone("rpf_{0}_{1}_down".format(tag_fail,tag_pass))
    for i in range(1,rpf_2D.GetNbinsX()+1):
        for j in range(1,rpf_2D.GetNbinsY()+1):
            xVal    = rpf_2D.GetXaxis().GetBinCenter(i)
            rpf_val = fitfun.Eval(xVal)
            rpf_up = errup.Eval(xVal)
            rpf_down = errdown.Eval(xVal)
            if(rpf_val<0.0001):
                rpf_val=0.0002
            if(rpf_up<0.0001):
                rpf_up=0.001
            if(rpf_down<0.0001):
                rpf_down=0.0001
            rpf_2D.SetBinContent(i,j,rpf_val)
            rpf_2D_up.SetBinContent(i,j,rpf_up)
            rpf_2D_down.SetBinContent(i,j,rpf_down)

    hPassFromFail = hFail.Clone("QCD_PassFromFail_{0}".format(tag_pass))
    hPassFromFailUp = hFail.Clone("QCD_PassFromFail_{0}_up".format(tag_pass))
    hPassFromFailDown = hFail.Clone("QCD_PassFromFail_{0}_down".format(tag_pass))
    hPassFromFail.Multiply(rpf_2D)
    hPassFromFailUp.Multiply(rpf_2D_up)
    hPassFromFailDown.Multiply(rpf_2D_down)

    output = r.TFile.Open(outputFile,"RECREATE")
    output.cd()
    hFail.Write()
    hPass.Write()
    hRatio1D.Write()
    rpf_2D.Write()
    rpf_2D_up.Write()
    rpf_2D_down.Write()
    hPassFromFail.Write()
    hPassFromFailUp.Write()
    hPassFromFailDown.Write()
    fitfun.Write()
    errup.Write()
    errdown.Write()    
    output.Close()

def applyFuncToTT(inputFile,fitFile,outputFile,tag_pass,tag_fail,binsX=15,xLo=60,xUp=360,binsY=22,yLo=800,yUp=3000):
    fitFile = r.TFile.Open(fitFile)
    fitfun  = fitFile.Get("QuadraticFit")
    errup   = fitFile.Get("QuadrarticFitErrorUpquadfit")
    errdown = fitFile.Get("QuadrarticFitErrorDnquadfit")
    hModel  = r.TH2F("hModel","",binsX,xLo,xUp,binsY,yLo,yUp)

    hFail = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_fail),hModel,inputFile,"QCD_{0}".format(tag_fail))
    hPass = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_pass),hModel,inputFile,"QCD_{0}".format(tag_pass))

    hFail1D = hFail.ProjectionX("QCD_mJY_mJJ_{0}_nom".format(tag_fail))
    hPass1D = hPass.ProjectionX("QCD_mJY_mJJ_{0}_nom".format(tag_pass))

    customMJYbins = np.array([60.,80.,100.,120.,140.,160.,180.,200.,220.,240.,260.,300.,360.],dtype='float64')
    customMJJbins = np.linspace(yLo,yUp,num=binsY+1,endpoint=True,dtype='float64')

    hFail1D = hFail1D.Rebin(len(customMJYbins)-1,"QCD_mJY_mJJ_{0}_nom_reb".format(tag_fail),customMJYbins)
    hPass1D = hPass1D.Rebin(len(customMJYbins)-1,"QCD_mJY_mJJ_{0}_nom_reb".format(tag_pass),customMJYbins)


    hRatio1D = hPass1D.Clone("hRatio1D_{0}".format(tag_pass))
    hRatio1D.Divide(hFail1D)

    rpf_2D = hModel.Clone("rpf_{0}_{1}".format(tag_fail,tag_pass))
    rpf_2D_up = hModel.Clone("rpf_{0}_{1}_up".format(tag_fail,tag_pass))
    rpf_2D_down = hModel.Clone("rpf_{0}_{1}_down".format(tag_fail,tag_pass))
    for i in range(1,rpf_2D.GetNbinsX()+1):
        for j in range(1,rpf_2D.GetNbinsY()+1):
            xVal    = rpf_2D.GetXaxis().GetBinCenter(i)
            rpf_val = fitfun.Eval(xVal)
            rpf_up = errup.Eval(xVal)
            rpf_down = errdown.Eval(xVal)
            if(rpf_val<0.0001):
                rpf_val=0.0001
            if(rpf_up<0.0001):
                rpf_up=0.0001
            if(rpf_down<0.0001):
                delta = (rpf_val-0.)/3.
                rpf_down=rpf_val-delta
            rpf_2D.SetBinContent(i,j,rpf_val)
            rpf_2D_up.SetBinContent(i,j,rpf_up)
            rpf_2D_down.SetBinContent(i,j,rpf_down)

    hFail = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_fail),hModel,inputFile,"QCD_{0}".format(tag_fail))
    hPass = rebinHisto("QCD_mJY_mJJ_{0}_nom".format(tag_pass),hModel,inputFile,"QCD_{0}".format(tag_pass))


    hPassFromFail = hFail.Clone("QCD_PassFromFail_{0}".format(tag_pass))
    hPassFromFailUp = hFail.Clone("QCD_PassFromFail_{0}_up".format(tag_pass))
    hPassFromFailDown = hFail.Clone("QCD_PassFromFail_{0}_down".format(tag_pass))
    hPassFromFail.Multiply(rpf_2D)
    hPassFromFailUp.Multiply(rpf_2D_up)
    hPassFromFailDown.Multiply(rpf_2D_down)

    output = r.TFile.Open(outputFile,"RECREATE")
    output.cd()
    hFail.Write()
    hPass.Write()
    hRatio1D.Write()
    rpf_2D.Write()
    rpf_2D_up.Write()
    rpf_2D_down.Write()
    hPassFromFail.Write()
    hPassFromFailUp.Write()
    hPassFromFailDown.Write()
    fitfun.Write()
    errup.Write()
    errdown.Write()    
    output.Close()


# get1DRpf("templates/WP_0.94_0.98/2016/QCD.root","templates/WP_0.94_0.98/2016/QCD1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2016/QCD.root","templates/WP_0.94_0.98/2016/QCD1DRpf_AL_T.root","AL_T","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2016/QCD.root","templates/WP_0.94_0.98/2016/QCD1DRpf_NAL_L.root","NAL_L","NAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2016/QCD.root","templates/WP_0.94_0.98/2016/QCD1DRpf_NAL_T.root","NAL_T","NAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2016/QCD.root","templates/WP_0.94_0.98/2016/QCD1DRpf_WAL_L.root","WAL_L","WAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2016/QCD.root","templates/WP_0.94_0.98/2016/QCD1DRpf_WAL_T.root","WAL_T","WAL_AL")

# get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_AL_T.root","AL_T","AL_AL")
get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_NAL_L.root","NAL_L","NAL_AL")
get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_NAL_T.root","NAL_T","NAL_AL")
get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_WAL_L.root","WAL_L","WAL_AL")
get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_WAL_T.root","WAL_T","WAL_AL")
get1DRpf("templates/WP_0.94_0.98/2016/dataMinusTTbar.root","templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_WAL_LplusT.root","WAL_L","WAL_AL")


# get1DRpf("templates/WP_0.94_0.98/2017/QCD.root","templates/WP_0.94_0.98/2017/QCD1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2017/QCD.root","templates/WP_0.94_0.98/2017/QCD1DRpf_AL_T.root","AL_T","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2017/QCD.root","templates/WP_0.94_0.98/2017/QCD1DRpf_NAL_L.root","NAL_L","NAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2017/QCD.root","templates/WP_0.94_0.98/2017/QCD1DRpf_NAL_T.root","NAL_T","NAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2017/QCD.root","templates/WP_0.94_0.98/2017/QCD1DRpf_WAL_L.root","WAL_L","WAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2017/QCD.root","templates/WP_0.94_0.98/2017/QCD1DRpf_WAL_T.root","WAL_T","WAL_AL")

# get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_AL_T.root","AL_T","AL_AL")
get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_NAL_L.root","NAL_L","NAL_AL")
get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_NAL_T.root","NAL_T","NAL_AL")
get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_WAL_L.root","WAL_L","WAL_AL")
get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_WAL_T.root","WAL_T","WAL_AL")
get1DRpf("templates/WP_0.94_0.98/2017/dataMinusTTbar.root","templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_WAL_LplusT.root","WAL_L","WAL_AL")


# get1DRpf("templates/WP_0.94_0.98/2018/QCD.root","templates/WP_0.94_0.98/2018/QCD1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2018/QCD.root","templates/WP_0.94_0.98/2018/QCD1DRpf_AL_T.root","AL_T","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2018/QCD.root","templates/WP_0.94_0.98/2018/QCD1DRpf_NAL_L.root","NAL_L","NAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2018/QCD.root","templates/WP_0.94_0.98/2018/QCD1DRpf_NAL_T.root","NAL_T","NAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2018/QCD.root","templates/WP_0.94_0.98/2018/QCD1DRpf_WAL_L.root","WAL_L","WAL_AL")
# get1DRpf("templates/WP_0.94_0.98/2018/QCD.root","templates/WP_0.94_0.98/2018/QCD1DRpf_WAL_T.root","WAL_T","WAL_AL")

# get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_AL_T.root","AL_T","AL_AL")
get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_NAL_L.root","NAL_L","NAL_AL")
get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_NAL_T.root","NAL_T","NAL_AL")
get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_WAL_L.root","WAL_L","WAL_AL")
get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_WAL_T.root","WAL_T","WAL_AL")
get1DRpf("templates/WP_0.94_0.98/2018/dataMinusTTbar.root","templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_WAL_LplusT.root","WAL_L","WAL_AL")


# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_AL_T.root","AL_T","AL_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_NAL_L.root","NAL_L","NAL_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_NAL_T.root","NAL_T","NAL_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_WAL_L.root","WAL_L","WAL_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_WAL_T.root","WAL_T","WAL_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_LL.root","LL","L_AL")
# get1DRpf("templates/RunII/QCD.root","templates/RunII/QCD1DRpf_TT.root","TT","T_AL")

# get1DRpf("templates/RunII/dataMinusTTbar.root","templates/RunII/DataMinusTT1DRpf_AL_L.root","AL_L","AL_AL")
# get1DRpf("templates/RunII/dataMinusTTbar.root","templates/RunII/DataMinusTT1DRpf_AL_T.root","AL_T","AL_AL")
# get1DRpf("templates/RunII/dataMinusTTbar.root","templates/RunII/DataMinusTT1DRpf_NAL_L.root","NAL_L","NAL_AL")
# get1DRpf("templates/RunII/dataMinusTTbar.root","templates/RunII/DataMinusTT1DRpf_NAL_T.root","NAL_T","NAL_AL")
# get1DRpf("templates/RunII/dataMinusTTbar.root","templates/RunII/DataMinusTT1DRpf_WAL_L.root","WAL_L","WAL_AL")
# get1DRpf("templates/RunII/dataMinusTTbar.root","templates/RunII/DataMinusTT1DRpf_WAL_T.root","WAL_T","WAL_AL")
