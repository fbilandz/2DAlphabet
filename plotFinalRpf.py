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
    finalRpf.SetTitle("MC Rpf x RRatio")

    ttbar_f = r.TFile.Open(TTbarFile)
    data_f  = r.TFile.Open(dataFile)
    if("pseudo" in dataFile):
        dataTag = "data_obs"
    else:
        dataTag = "JetHT"
    dataPass = data_f.Get("{0}_mJY_mJJ_{1}_nom".format(dataTag,tagPass))
    dataFail = data_f.Get("{0}_mJY_mJJ_{1}_nom".format(dataTag,tagFail))
    ttbarPass = ttbar_f.Get("TTbar_mJY_mJJ_{0}_nom".format(tagPass))
    ttbarFail = ttbar_f.Get("TTbar_mJY_mJJ_{0}_nom".format(tagFail))

    dataPass.Add(ttbarPass,-1)
    dataFail.Add(ttbarFail,-1)

    dataRpf = dataPass.Clone("Rpf_data")
    dataRpf.SetTitle("Data-TTbar pass/fail")
    dataRpf.Divide(dataFail)
    dataRpf.SetMinimum(0)
    dataRpf.SetMaximum(0.2)

    c = r.TCanvas("","",3000,2000)
    c.Divide(2,2)
    c.cd(1)
    rpf_mc.Draw("lego")
    #r.gPad.SetPhi(210)
    c.cd(2)
    rrpf.Draw("lego")
    #r.gPad.SetPhi(210)
    c.cd(3)
    finalRpf.Draw("lego")
    #r.gPad.SetPhi(210)
    c.cd(4)
    dataRpf.Draw("lego")
    #r.gPad.SetPhi(210)
    r.gPad.Update()
    c.SaveAs(outputFile)

#SR
# plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_VRL.root","2016_VRL/2016_VRL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","2016_VRL_Rpfs.png","VRL","VRF")
# plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_VRT.root","2016_VRT/2016_VRT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","2016_VRT_Rpfs.png","VRT","VRF")
# plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_TT.root","2016_TT/2016_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/pseudo.root","2016_TT_Rpfs.png","TT","ATT")
# plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_LL.root","2016_LL/2016_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/pseudo.root","2016_LL_Rpfs.png","LL","AT")

# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_VRL.root","2017_VRL/2017_VRL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_VRL_Rpfs.png","VRL","VRF")
# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_VRT.root","2017_VRT/2017_VRT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_VRT_Rpfs.png","VRT","VRF")
# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_TT.root","2017_TT/2017_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/pseudo.root","2017_TT_Rpfs.png","TT","ATT")
# plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_LL.root","2017_LL/2017_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/pseudo.root","2017_LL_Rpfs.png","LL","AT")

# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_VRL.root","2018_VRL/2018_VRL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_VRL_Rpfs.png","VRL","VRF")
# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_VRT.root","2018_VRT/2018_VRT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_VRT_Rpfs.png","VRT","VRF")
# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_TT.root","2018_TT/2018_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/pseudo.root","2018_TT_Rpfs.png","TT","ATT")
# plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_LL.root","2018_LL/2018_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/pseudo.root","2018_LL_Rpfs.png","LL","AT")


#ESB
#plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_ESB_VRL.root","2016_ESB_VRL/2016_VRL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","2016_ESB_VRL_Rpfs.png","VRL","VRF")
#plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_ESB_VRT.root","2016_ESB_VRT/2016_VRT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/JetHT.root","2016_ESB_VRT_Rpfs.png","VRT","VRF")
plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_ESB_TT.root","2016_ESB_TT/2016_ESB_TT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/pseudo.root","2016_ESB_TT_Rpfs.png","ESB_TT","ESB_ATT")
plotRpfs("templates/WP_0.8_0.95/2016/QCD1DRpf_ESB_LL.root","2016_ESB_LL/2016_ESB_LL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2016/TTbar.root","templates/WP_0.8_0.95/2016/pseudo.root","2016_ESB_LL_Rpfs.png","ESB_LL","ESB_AT")

#plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_ESB_VRL.root","2017_ESB_VRL/2016_VRL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_ESB_VRL_Rpfs.png","VRL","VRF")
#plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_ESB_VRT.root","2017_ESB_VRT/2016_VRT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/JetHT.root","2017_ESB_VRT_Rpfs.png","VRT","VRF")
plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_ESB_TT.root","2017_ESB_TT/TT_22_1DRpfSmooth//plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/pseudo.root","2017_ESB_TT_Rpfs.png","ESB_TT","ESB_ATT")
plotRpfs("templates/WP_0.8_0.95/2017/QCD1DRpf_ESB_LL.root","2017_ESB_LL/LL_22_1DRpfSmooth//plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2017/TTbar.root","templates/WP_0.8_0.95/2017/pseudo.root","2017_ESB_LL_Rpfs.png","ESB_LL","ESB_AT")

#plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_ESB_VRL.root","2018_ESB_VRL/2016_VRL_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_ESB_VRL_Rpfs.png","VRL","VRF")
#plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_ESB_VRT.root","2018_ESB_VRT/2016_VRT_22/plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/JetHT.root","2018_ESB_VRT_Rpfs.png","VRT","VRF")
plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_ESB_TT.root","2018_ESB_TT/TT_22_1DRpfSmooth//plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/pseudo.root","2018_ESB_TT_Rpfs.png","ESB_TT","ESB_ATT")
plotRpfs("templates/WP_0.8_0.95/2018/QCD1DRpf_ESB_LL.root","2018_ESB_LL/LL_22_1DRpfSmooth//plots/postfit_rpf_fitb.root","templates/WP_0.8_0.95/2018/TTbar.root","templates/WP_0.8_0.95/2018/pseudo.root","2018_ESB_LL_Rpfs.png","ESB_LL","ESB_AT")
