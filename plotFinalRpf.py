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

def plotRpfs(MCfitFile,dataFitFile,TTbarFile,dataFile,outputFile,tagPass,tagFail,zMax=0.1):
    rrpf_f = r.TFile.Open(dataFitFile)
    rrpf   = rrpf_f.Get("rpf_final")#RRpf actually!
    rrpf.SetName("RRpf")
    rrpf.SetTitle("RRatio")
    print(MCfitFile,"QCD_{0}".format(tagFail))


    smooth_f = r.TFile.Open(MCfitFile)
    print(MCfitFile)
    print("QCD_PassFromFail_{0}".format(tagPass.replace("NA","WA")))
    print("QCD_{0}".format(tagFail.replace("NA","WA")))
    smooth_pass = smooth_f.Get("QCD_PassFromFail_{0}".format(tagPass.replace("NA","WA")))
    smooth_fail = smooth_f.Get("QCD_{0}".format(tagFail.replace("NA","WA")))

    smooth_pass = rebin2DHisto(smooth_pass,rrpf,"QCD_DD_Pass")
    smooth_fail = rebin2DHisto(smooth_fail,rrpf,"QCD_DD_Fail")

    rpf_mc = smooth_pass.Clone("Rpf_mc")
    rpf_mc.SetTitle("1D DD Rpf")
    rpf_mc.Divide(smooth_fail)

    finalRpf = rrpf.Clone("Rpf_final")
    finalRpf.Multiply(rpf_mc)
    finalRpf.SetZTitle("R_{P/F}^{data}")

    finalRpf.SetTitle("1D Rpf x RRatio")

    ttbar_f = r.TFile.Open(TTbarFile)
    data_f  = r.TFile.Open(dataFile)
    dataTag = "data_obs"

    dataPass = data_f.Get("{0}_mJY_mJJ_{1}_nom".format(dataTag,tagPass))
    dataFail = data_f.Get("{0}_mJY_mJJ_{1}_nom".format(dataTag,tagFail))
    ttbarPass = ttbar_f.Get("TTbar_mJY_mJJ_{0}_nom".format(tagPass))
    ttbarFail = ttbar_f.Get("TTbar_mJY_mJJ_{0}_nom".format(tagFail))

    dataPass.Add(ttbarPass,-1)
    dataFail.Add(ttbarFail,-1)
    dataPass = rebin2DHisto(dataPass,rrpf,"Data-TTbar_Pass")
    dataFail = rebin2DHisto(dataFail,rrpf,"Data-TTbar_Fail")

    dataRpf = dataPass.Clone("Rpf_data")
    dataRpf.SetTitle("Data-TTbar pass/fail")
    dataRpf.Divide(dataFail)
    dataRpf.SetXTitle("M_{JY} [GeV]")
    dataRpf.SetYTitle("M_{JJ} [GeV]")
    dataRpf.SetZTitle("Data-t#bar{t}")
    dataRpf.SetMinimum(0)
    dataRpf.SetMaximum(0.2)

    #drawOpt="colz"
    drawOpt="lego"

    c = r.TCanvas("","",3000,2000)
    c.SetMargin(0.15,0.15,0.15,0.15)
    c.cd(0)
    rpf_mc.SetTitle("1D R_{P/F}")
    rpf_mc.SetTitleOffset(1.7,"X")
    rpf_mc.SetTitleOffset(1.7,"Y")
    rpf_mc.SetTitleOffset(1.7,"Z")
    rpf_mc.GetZaxis().SetTitle("R_{P/F}")
    rpf_mc.Draw(drawOpt)
    c.SaveAs(outputFile.replace(".png","_1DRpf.png"))
    c.Clear()
    rrpf.SetTitle("")
    rrpf.SetTitleOffset(1.7,"X")
    rrpf.SetTitleOffset(1.7,"Y")
    rrpf.SetTitleOffset(1.7,"Z")
    rrpf.Draw(drawOpt)
    c.SaveAs(outputFile.replace(".png","_rratio.png"))
    c.Clear()
    finalRpf.SetTitle("RRatio x 1D Rpf")
    finalRpf.SetTitleOffset(1.7,"X")
    finalRpf.SetTitleOffset(1.7,"Y")
    finalRpf.SetTitleOffset(1.7,"Z")
    finalRpf.GetZaxis().SetRangeUser(0.,zMax)
    finalRpf.Draw(drawOpt)
    c.SaveAs(outputFile.replace(".png","_finalRpf.png"))
    c.Clear()
    dataRpf.SetTitle("Data-TTbar pass/fail")
    dataRpf.SetTitleOffset(1.7,"X")
    dataRpf.SetTitleOffset(1.7,"Y")
    dataRpf.SetTitleOffset(1.7,"Z")
    dataRpf.GetZaxis().SetRangeUser(0.,zMax)
    dataRpf.Draw(drawOpt)
    c.SaveAs(outputFile.replace(".png","_dataRpf.png"))

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


#plotRpfs(MCfitFile,dataFitFile,TTbarFile,dataFile,outputFile,tagPass,tagFail,zMax=0.1):
#plotRpfs("templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_WAL_L.root","2016_NAL_L_CR/NAL_L_2016/plots/postfit_rpf_fitb.root","templates/WP_0.94_0.98/2016/TTbar16.root","templates/WP_0.94_0.98/2016/JetHT16.root","RpfPlots/2016_NAL_L_Rpfs.png","NAL_L","NAL_AL",0.02)
# plotRpfs("templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_WAL_L.root","2017_NAL_L_CR/NAL_L_2017/plots/postfit_rpf_fitb.root","templates/WP_0.94_0.98/2017/TTbar17.root","templates/WP_0.94_0.98/2017/JetHT17.root","RpfPlots/2017_NAL_L_Rpfs.png","NAL_L","NAL_AL",0.02)
# plotRpfs("templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_WAL_L.root","2018_NAL_L_CR/NAL_L_2018/plots/postfit_rpf_fitb.root","templates/WP_0.94_0.98/2018/TTbar18.root","templates/WP_0.94_0.98/2018/JetHT18.root","RpfPlots/2018_NAL_L_Rpfs.png","NAL_L","NAL_AL",0.02)

# plotRpfs("templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_WAL_T.root","2016_NAL_T_CR/NAL_T_2016/plots/postfit_rpf_fitb.root","templates/WP_0.94_0.98/2016/TTbar16.root","templates/WP_0.94_0.98/2016/JetHT16.root","RpfPlots/2016_NAL_T_Rpfs.png","NAL_T","NAL_AL",0.02)
# plotRpfs("templates/WP_0.94_0.98/2017/DataMinusTT1DRpf_WAL_T.root","2017_NAL_T_CR/NAL_T_2017/plots/postfit_rpf_fitb.root","templates/WP_0.94_0.98/2017/TTbar17.root","templates/WP_0.94_0.98/2017/JetHT17.root","RpfPlots/2017_NAL_T_Rpfs.png","NAL_T","NAL_AL",0.02)
# plotRpfs("templates/WP_0.94_0.98/2018/DataMinusTT1DRpf_WAL_T.root","2018_NAL_T_CR/NAL_T_2018/plots/postfit_rpf_fitb.root","templates/WP_0.94_0.98/2018/TTbar18.root","templates/WP_0.94_0.98/2018/JetHT18.root","RpfPlots/2018_NAL_T_Rpfs.png","NAL_T","NAL_AL",0.02)


plotRpfs("templates/WP_0.94_0.98/2016/DataMinusTT1DRpf_WAL_T.root","2016_NAL_CR/NAL_T_2016/plots/postfit_rpf_fits.root","templates/WP_0.94_0.98/2016/TTbar16.root","templates/WP_0.94_0.98/2016/JetHT16.root","RpfPlots/2016_NAL_T_Rpfs.png","NAL_T","NAL_AL",0.02)
