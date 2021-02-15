import ROOT as r
import numpy as np
from time import sleep
from QuadraticFit import *

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0000)
r.gROOT.ForceStyle()



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
plotDistributions("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_L.root","16_AL_L.pdf","AL_L","AL_AL")
plotDistributions("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_T.root","16_AL_T.pdf","AL_T","AL_AL")

plotDistributions("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_L.root","17_AL_L.pdf","AL_L","AL_AL")
plotDistributions("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_T.root","17_AL_T.pdf","AL_T","AL_AL")

plotDistributions("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_L.root","18_AL_L.pdf","AL_L","AL_AL")
plotDistributions("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_T.root","18_AL_T.pdf","AL_T","AL_AL")

plotDistributions("templates/WP_0.8_0.95/2016/QCD1DRpf_LL.root","16_LL.pdf","LL","L_AL")
plotDistributions("templates/WP_0.8_0.95/2016/QCD1DRpf_TT.root","16_TT.pdf","TT","T_AL")

plotDistributions("templates/WP_0.8_0.95/2017/QCD1DRpf_LL.root","17_LL.pdf","LL","L_AL")
plotDistributions("templates/WP_0.8_0.95/2017/QCD1DRpf_TT.root","17_TT.pdf","TT","T_AL")

plotDistributions("templates/WP_0.8_0.95/2018/QCD1DRpf_LL.root","18_LL.pdf","LL","L_AL")
plotDistributions("templates/WP_0.8_0.95/2018/QCD1DRpf_TT.root","18_TT.pdf","TT","T_AL")


plotVariations("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_L.root","2016_AL_L_rpfVar.pdf","AL_L")
plotVariations("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_T.root","2016_AL_T_rpfVar.pdf","AL_T")
plotVariations("templates/WP_0.8_0.95/2016/QCD1DRpf_LL.root","2016_LL_rpfVar.pdf","LL")
plotVariations("templates/WP_0.8_0.95/2016/QCD1DRpf_TT.root","2016_TT_rpfVar.pdf","TT")

