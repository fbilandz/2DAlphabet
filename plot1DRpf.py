import ROOT as r
import numpy as np
from time import sleep
from QuadraticFit import *

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0000)
r.gROOT.ForceStyle()

def rebin2DHisto(hToRebin,hModel,name):
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
            err = hToRebin.GetBinError(i,j)
            err_re = np.sqrt(hRes.GetBinError(i_re,j_re)*hRes.GetBinError(i_re,j_re)+err*err)
            hRes.Fill(x,y,value)
            hRes.SetBinError(i_re,j_re,err_re)
    hRes.SetDirectory(0)
    return hRes


def plotDistributions(inputFile,outputFile,tagPass,tagFail):
    rFile = r.TFile.Open(inputFile)
    c = r.TCanvas("","",2000,2000)
    c.Divide(2,2)
    c.cd(1)
    h1 = rFile.Get("QCD_{0}".format(tagFail))
    h1.SetTitleOffset(2,"X")
    h1.SetTitleOffset(2,"Y")

    h1.SetXTitle("M_{JY} [GeV]")
    h1.SetYTitle("M_{JJ} [GeV]")

    h1.SetTitle("QCD MC {0}".format(tagFail))
    r.gPad.SetPhi(210)
    h1.Draw("lego")


    c.cd(2)
    h2 = rFile.Get("QCD_{0}".format(tagPass))
    h2.SetTitleOffset(2,"X")
    h2.SetTitleOffset(2,"Y")

    h2.SetXTitle("M_{JY} [GeV]")
    h2.SetYTitle("M_{JJ} [GeV]")

    h2.SetTitle("QCD MC {0}".format(tagPass))
    r.gPad.SetPhi(210)
    h2.Draw("lego")


    c.cd(3)
    h3 = rFile.Get("hRatio1D_{0}".format(tagPass))
    fUp = rFile.Get("QuadrarticFitErrorUpquadfit")
    fNom = rFile.Get("QuadraticFit")
    fDown = rFile.Get("QuadrarticFitErrorDnquadfit")
    
    if("TT" in tagPass or "LL" in tagPass):
        h3.SetTitle("Fit to MC Rpf taken from VR")
    else:  
        fitRes = h3.Fit(fNom,"S")
        chi2 = fitRes.Chi2()/fitRes.Ndf()
        h3.SetTitle("Fit to MC Rpf: #Chi^{2}/NDOF = %.2f" %chi2)
    #h3.SetTitle("Fit to MC Rpf")
    h3.SetXTitle("M_{JY} [GeV]")
    h3.SetTitleOffset(1.5,"Y")
    h3.SetYTitle("R_{P/F}")

    h3.Draw("e")
    fUp.Draw("same")
    fNom.Draw("same")
    fDown.Draw("same")


    c.cd(4)
    h4 = rFile.Get("QCD_PassFromFail_{0}".format(tagPass))
    h4.SetTitleOffset(2,"X")
    h4.SetTitleOffset(2,"Y")

    h4.SetXTitle("M_{JY} [GeV]")
    h4.SetYTitle("M_{JJ} [GeV]")

    h4.SetTitle("Fail x 1D Rpf")
    r.gPad.SetPhi(210)
    h4.Draw("lego")

    c.SaveAs(outputFile)

    c2 = r.TCanvas("c2","",2000,2000)
    c2.cd()
    h3.Draw("e")
    fUp.Draw("same")
    fNom.Draw("same")
    fDown.Draw("same")
    c2.SaveAs(outputFile.replace(".pdf","_rpfFit.pdf"))    


def plotVariations(inputFile,outputFile,tagPass):
    rFile = r.TFile.Open(inputFile)
    c = r.TCanvas("","",2000,1000)
    c.Divide(2,1)
    hNom = rFile.Get("QCD_PassFromFail_{0}".format(tagPass))
    hUp  = rFile.Get("QCD_PassFromFail_{0}_up".format(tagPass))
    hDn  = rFile.Get("QCD_PassFromFail_{0}_down".format(tagPass))
    c.cd(1)    
    hNomMJY = hNom.ProjectionX()
    hNomMJY.SetTitle("QCD fail x 1DRpf M_{JY} [GeV]")
    hUpMJY  = hUp.ProjectionX()
    hDnMJY  = hDn.ProjectionX()
    hUpMJY.SetLineColor(r.kGreen)
    hDnMJY.SetLineColor(r.kRed)
    hNomMJY.Draw("HIST")
    hUpMJY.Draw("HIST same")
    hDnMJY.Draw("HIST same")

    legendMJY = r.TLegend(0.7, 0.7, .85, .85)
    legendMJY.AddEntry(hNomMJY,"nominal","l")
    legendMJY.AddEntry(hUpMJY,"1sigma up","l")
    legendMJY.AddEntry(hDnMJY,"1sigma down","l")
    legendMJY.Draw()
    c.cd(2)    
    hNomMJJ = hNom.ProjectionY()
    hNomMJJ.SetTitle("QCD fail x 1DRpf M_{JJ} [GeV]")

    hUpMJJ  = hUp.ProjectionY()
    hDnMJJ  = hDn.ProjectionY()
    hUpMJJ.SetLineColor(r.kGreen)
    hDnMJJ.SetLineColor(r.kRed)
    hNomMJJ.Draw("HIST")
    hUpMJJ.Draw("HIST same")
    hDnMJJ.Draw("HIST same")

    legendMJJ = r.TLegend(0.7, 0.7, .85, .85)
    legendMJJ.AddEntry(hNomMJJ,"nominal","l")
    legendMJJ.AddEntry(hUpMJJ,"1sigma up","l")
    legendMJJ.AddEntry(hDnMJJ,"1sigma down","l")
    legendMJJ.Draw()

    c.SaveAs(outputFile)
#SR

# plotDistributions("templates/2017/QCD1DRpf_AL_L.root","17_AL_L.pdf","AL_L","AL_AL")
# plotDistributions("templates/2017/QCD1DRpf_AL_T.root","17_AL_T.pdf","AL_T","AL_AL")

# plotDistributions("templates/2018/QCD1DRpf_AL_L.root","18_AL_L.pdf","AL_L","AL_AL")
# plotDistributions("templates/2018/QCD1DRpf_AL_T.root","18_AL_T.pdf","AL_T","AL_AL")

# plotDistributions("templates/2017/QCD1DRpf_LL.root","17_LL.pdf","LL","L_AL")
# plotDistributions("templates/2017/QCD1DRpf_TT.root","17_TT.pdf","TT","T_AL")

# plotDistributions("templates/2018/QCD1DRpf_LL.root","18_LL.pdf","LL","L_AL")
# plotDistributions("templates/2018/QCD1DRpf_TT.root","18_TT.pdf","TT","T_AL")


def get2DRpf(regionPass,regionFail):
    #f       = r.TFile.Open("templates/2017/QCD.root")
    f       = r.TFile.Open("templates/2017/dataMinusTTbar.root")
    hPass   = f.Get("QCD_mJY_mJJ_{0}_nom".format(regionPass))
    hFail   = f.Get("QCD_mJY_mJJ_{0}_nom".format(regionFail))

    modelHistoFile = r.TFile.Open("2017_NAL_L_sanityCheck/NAL_L_2017/plots/postfit_rpf_fitb.root")
    modelHisto     = modelHistoFile.Get("rpf_final")


    hPass = rebin2DHisto(hPass,modelHisto,"QCD_MC_Pass")
    hFail = rebin2DHisto(hFail,modelHisto,"QCD_MC_Fail")

    hRpf    = hPass.Clone("Rpf_{0}".format(regionPass))
    hRpf.Divide(hFail)
    hRpf.SetDirectory(0)
    return hRpf

def plot2DRpf(hRpf,outputFile,drawOpt="lego",zMax="",zTitle=""):
    c = r.TCanvas("","",3000,2000)
    c.SetMargin(0.15,0.15,0.15,0.15)
    c.cd(0)
    hRpf.SetTitle("")
    hRpf.SetTitleOffset(1.7,"X")
    hRpf.SetTitleOffset(1.7,"Y")
    hRpf.SetTitleOffset(1.7,"Z")
    hRpf.SetZTitle(zTitle)
    if(zMax):
        hRpf.GetZaxis().SetRangeUser(0.,zMax)
    hRpf.Draw(drawOpt)
    c.SaveAs(outputFile)

regionsPass = ["AL_L","AL_T","NAL_L","NAL_T"]
regionsFail = ["AL_AL","AL_AL","NAL_AL","NAL_AL"]
rpfs = {}
zMax = [0.05,0.05,0.3,0.1]

for i in range(len(regionsPass)):
    hRpf = get2DRpf(regionsPass[i],regionsFail[i])
    rpfs[regionsPass[i]] = hRpf
    plot2DRpf(hRpf,"Rpf_{0}.png".format(regionsPass[i]),zMax=zMax[i],zTitle="R_{P/F}")


rpfs["NAL_T"].Divide(rpfs["NAL_L"])
plot2DRpf(rpfs["NAL_L"],"ratio_NALL_NALT.png",drawOpt="lego",zMax=0.1,zTitle="R_{Ratio}")

rpfs["AL_T"].Divide(rpfs["AL_L"])
plot2DRpf(rpfs["AL_L"],"ratio_ALL_ALT.png",drawOpt="lego",zMax=0.05,zTitle="R_{Ratio}")