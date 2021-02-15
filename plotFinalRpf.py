import ROOT as r
import numpy as np

r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(0000)

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

def plotRpfs(MCfitFile,dataFitFile,TTbarFile,dataFile,outputFile,tagPass,tagFail):
    rrpf_f = r.TFile.Open(dataFitFile)
    rrpf   = rrpf_f.Get("rpf_final")#RRpf actually!
    rrpf.SetName("RRpf")
    rrpf.SetTitle("RRatio")
    print(MCfitFile,"QCD_{0}".format(tagFail))


    smooth_f = r.TFile.Open(MCfitFile)
    smooth_pass = smooth_f.Get("QCD_PassFromFail_{0}".format(tagPass))
    smooth_fail = smooth_f.Get("QCD_{0}".format(tagFail))

    smooth_pass = rebin2DHisto(smooth_pass,rrpf,"QCD_MC_Pass")
    smooth_fail = rebin2DHisto(smooth_fail,rrpf,"QCD_MC_Fail")

    rpf_mc = smooth_pass.Clone("Rpf_mc")
    rpf_mc.SetTitle("1D MC Rpf")
    rpf_mc.Divide(smooth_fail)

    finalRpf = rrpf.Clone("Rpf_final")
    finalRpf.Multiply(rpf_mc)
    finalRpf.SetZTitle("R_{P/F}^{data}")

    finalRpf.SetTitle("MC Rpf x RRatio")

    ttbar_f = r.TFile.Open(TTbarFile)
    data_f  = r.TFile.Open(dataFile)
    if("pseudo" in dataFile):
        dataTag = "data_obs"
    else:
        dataTag = "data_obs"

    dataPass = data_f.Get("{0}_mJY_mJJ_{1}_nom".format(dataTag,tagPass))
    dataFail = data_f.Get("{0}_mJY_mJJ_{1}_nom".format(dataTag,tagFail))
    ttbarPass = ttbar_f.Get("TTbar_mJY_mJJ_{0}_nom".format(tagPass))
    ttbarFail = ttbar_f.Get("TTbar_mJY_mJJ_{0}_nom".format(tagFail))

    dataPass.Add(ttbarPass,-1)
    dataFail.Add(ttbarFail,-1)

    dataRpf = dataPass.Clone("Rpf_data")
    dataRpf.SetTitle("Data-TTbar pass/fail")
    dataRpf.Divide(dataFail)
    dataRpf.SetXTitle("M_{JY} [GeV]")
    dataRpf.SetYTitle("M_{JJ} [GeV]")
    dataRpf.SetZTitle("Data-t#bar{t}")
    dataRpf.SetMinimum(0)
    dataRpf.SetMaximum(0.2)


    c = r.TCanvas("","",3000,2000)
    c.SetMargin(0.15,0.15,0.15,0.15)
    c.cd(0)
    rpf_mc.SetTitle("")
    rpf_mc.SetTitleOffset(1.7,"X")
    rpf_mc.SetTitleOffset(1.7,"Y")
    rpf_mc.SetTitleOffset(1.7,"Z")
    rpf_mc.Draw("lego")
    c.SaveAs(outputFile.replace(".png","_mcRpf.pdf"))
    c.Clear()
    rrpf.SetTitle("")
    rrpf.SetTitleOffset(1.7,"X")
    rrpf.SetTitleOffset(1.7,"Y")
    rrpf.SetTitleOffset(1.7,"Z")
    rrpf.Draw("lego")
    c.SaveAs(outputFile.replace(".png","_rratio.pdf"))
    c.Clear()
    finalRpf.SetTitle("")
    finalRpf.SetTitleOffset(1.7,"X")
    finalRpf.SetTitleOffset(1.7,"Y")
    finalRpf.SetTitleOffset(1.7,"Z")
    finalRpf.Draw("lego")
    c.SaveAs(outputFile.replace(".png","_finalRpf.pdf"))
    c.Clear()
    dataRpf.SetTitle("")
    dataRpf.SetTitleOffset(1.7,"X")
    dataRpf.SetTitleOffset(1.7,"Y")
    dataRpf.SetTitleOffset(1.7,"Z")
    dataRpf.Draw("lego")
    c.SaveAs(outputFile.replace(".png","_dataRpf.pdf"))

    # c.Divide(2,2)
    # c.cd(1)
    # rpf_mc.Draw("lego")
    # #r.gPad.SetPhi(210)
    # c.cd(2)
    # rrpf.Draw("lego")
    # #r.gPad.SetPhi(210)
    # c.cd(3)
    # finalRpf.Draw("lego")
    # #r.gPad.SetPhi(210)
    # c.cd(4)
    # dataRpf.Draw("lego")
    # #r.gPad.SetPhi(210)
    # r.gPad.Update()

#SR
plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_L.root","2016_AL/AL_L_2016/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","2016_AL_L_Rpfs.png","AL_L","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_L.root","2017_AL/AL_L_2017/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_AL_L_Rpfs.png","AL_L","AL_AL")
#plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_L.root","2018_AL/AL_L_2018/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_AL_L_Rpfs.png","AL_L","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_L.root","RunII_AL/AL_L_2016/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","RunII_16_AL_L_Rpfs.png","AL_L","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_L.root","RunII_AL/AL_L_2017/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","RunII_17_AL_L_Rpfs.png","AL_L","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_L.root","RunII_AL/AL_L_2018/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","RunII_18_AL_L_Rpfs.png","AL_L","AL_AL")

plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_T.root","2016_AL/AL_T_2016/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","2016_AL_T_Rpfs.png","AL_T","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_T.root","2017_AL/AL_T_2017/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_AL_T_Rpfs.png","AL_T","AL_AL")
#plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_T.root","2018_AL/AL_T_2018/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_AL_T_Rpfs.png","AL_T","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_AL_T.root","RunII_AL/AL_T_2016/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","RunII_16_AL_T_Rpfs.png","AL_T","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_T.root","RunII_AL/AL_T_2017/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","RunII_17_AL_T_Rpfs.png","AL_T","AL_AL")
plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_T.root","RunII_AL/AL_T_2018/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","RunII_18_AL_T_Rpfs.png","AL_T","AL_AL")





# plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_TT.root","2016_TT/2016_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/pseudo.root","2016_TT_Rpfs.png","TT","ATT")
# plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_LL.root","2016_LL/2016_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/pseudo.root","2016_LL_Rpfs.png","LL","AT")

# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_L.root","2017_AL_L/2017_AL_L_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_AL_L_Rpfs.png","AL_L","AL_AL")
# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_AL_T.root","2017_AL_T/2017_AL_T_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_AL_T_Rpfs.png","AL_T","AL_AL")
# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_TT.root","2017_TT/2017_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/pseudo.root","2017_TT_Rpfs.png","TT","ATT")
# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_LL.root","2017_LL/2017_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/pseudo.root","2017_LL_Rpfs.png","LL","AT")

# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_L.root","2018_AL_L/2018_AL_L_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_AL_L_Rpfs.png","AL_L","AL_AL")
# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_AL_T.root","2018_AL_T/2018_AL_T_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_AL_T_Rpfs.png","AL_T","AL_AL")
# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_TT.root","2018_TT/2018_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/pseudo.root","2018_TT_Rpfs.png","TT","ATT")
# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_LL.root","2018_LL/2018_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/pseudo.root","2018_LL_Rpfs.png","LL","AT")

