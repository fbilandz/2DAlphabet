import ROOT as r
import numpy as np
import sys
r.gROOT.SetBatch(True)
r.gStyle.SetOptFit(111)


def rebinHisto(hToRebin,name):
    bins_x = [60,80,100,140,160,180,200,360]
    bins_y = [900,1100,1200,1300,1400,1500,3000]
    #bins_x = [60,80,100,120,160,200,360]
    #bins_y = [900,1200,1500,3000]
    bins_x = np.array(bins_x,dtype='float64')
    bins_y = np.array(bins_y,dtype='float64')
    n_x    = len(bins_x) - 1 
    n_y    = len(bins_y) - 1 
    hModel = r.TH2F("model_histo","",n_x,bins_x,n_y,bins_y)

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
            tempVal = hRes.GetBinContent(i_re,j_re)
            err = hToRebin.GetBinError(i,j)
            err_re = np.sqrt(hRes.GetBinError(i_re,j_re)*hRes.GetBinError(i_re,j_re)+err*err)
            hRes.SetBinContent(i_re,j_re,tempVal+value)
            hRes.SetBinError(i_re,j_re,err_re)
    hRes.SetDirectory(0)
    hRes.SetBinErrorOption(1)
    return hRes

def get_binning_x(hLow,hSig,hHigh):
    bins = []
    for i in range(1,hLow.GetNbinsX()+1):
        bins.append(hLow.GetXaxis().GetBinLowEdge(i))
    for i in range(1,hSig.GetNbinsX()+1):
        bins.append(hSig.GetXaxis().GetBinLowEdge(i))
    for i in range(1,hHigh.GetNbinsX()+2):#low edge of overflow is high edge of last bin
        bins.append(hHigh.GetXaxis().GetBinLowEdge(i))
    bins = np.array(bins,dtype='float64')
    return bins

def get_binning_y(hLow,hSig,hHigh):
    #histos should have same binning in Y
    bins = []
    for i in range(1,hLow.GetNbinsY()+2):
        bins.append(hLow.GetYaxis().GetBinLowEdge(i))
    bins = np.array(bins,dtype='float64')
    return bins

def merge_low_sig_high(hLow,hSig,hHigh,hName="temp"):
    n_x_low     = hLow.GetNbinsX()
    n_x_sig     = hSig.GetNbinsX()
    n_x_high    = hHigh.GetNbinsX()
    n_x         = n_x_low + n_x_sig + n_x_high
    n_y         = hLow.GetNbinsY()#assumes Y bins are the same
    bins_x      = get_binning_x(hLow,hSig,hHigh)
    bins_y      = get_binning_y(hLow,hSig,hHigh)
    h_res = r.TH2F(hName,"",n_x,bins_x,n_y,bins_y)
    h_res.SetBinErrorOption(1)
    for i in range(1,n_x_low+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+0,j,hLow.GetBinContent(i,j))
            h_res.SetBinError(i+0,j,hLow.GetBinError(i,j))

    for i in range(1,n_x_sig+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+n_x_low,j,hSig.GetBinContent(i,j))
            h_res.SetBinError(i+n_x_low,j,hSig.GetBinError(i,j))

    for i in range(1,n_x_high+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i+n_x_sig+n_x_low,j,hHigh.GetBinContent(i,j))
            h_res.SetBinError(i+n_x_sig+n_x_low,j,hHigh.GetBinError(i,j))

    return h_res

def remake_histo_CI_errors(h):   
    n_x     = h.GetNbinsX()
    x_min   = h.GetXaxis().GetBinLowEdge(1)
    x_max   = h.GetXaxis().GetBinLowEdge(n_x+1)
    n_y     = h.GetNbinsY()
    y_min   = h.GetYaxis().GetBinLowEdge(1)
    y_max   = h.GetYaxis().GetBinLowEdge(n_y+1)
    #print(n_x,x_min,x_max,n_y,y_min,y_max)
    h_res = r.TH2F("temp","",n_x,x_min,x_max,n_y,y_min,y_max)
    h_res.SetBinErrorOption(1)
    for i in range(1,n_x+1):
        for j in range(1,n_y+1):
            h_res.SetBinContent(i,j,h.GetBinContent(i,j))
    return h_res

def calculatePull(data_cont,bkg_cont,data_err_lo,data_err_up,bkg_err):
    diff        = data_cont-bkg_cont
    if(bkg_cont>=data_cont):
        sigma2  = data_err_up*data_err_up+bkg_err*bkg_err
    else:
        sigma2  = data_err_lo*data_err_lo+bkg_err*bkg_err
    sigma     = np.sqrt(sigma2)
    pull      = diff/sigma
    # if(abs(pull)>3.0):
    #     print(data_cont,bkg_cont,data_err_lo,data_err_up,bkg_err)
    #     print(diff,sigma,pull)
    return pull


def calculatePull_quantile(data_cont,bkg_cont):
    pull = r.Math.normal_quantile(r.Math.poisson_cdf(int(data_cont),bkg_cont),1)#black magic
    return pull


def get_2D_pull(h2_bkg,h2_data,region,h2Fail=""):
    h_pull      = r.TH1F("pulls_{0}".format(region),"Pulls in {0};Pull;Bins/0.05".format(region),16,-4,4)
    h_pull.SetDirectory(0)
    h2_data.SetBinErrorOption(1)
    for i in range(1,h2_bkg.GetNbinsX()+1):
        for j in range(1,h2_bkg.GetNbinsY()+1):
            if(h2_data.GetBinContent(i,j)<1 and h2_bkg.GetBinContent(i,j)<1):
                continue
            if(h2Fail and h2Fail.GetBinContent(i,j)==0):
                print("Skipping ", i,j)
                continue
            data_err_up     = h2_data.GetBinErrorUp(i,j)
            data_err_lo     = h2_data.GetBinErrorLow(i,j)
            bkg_err         = h2_bkg.GetBinError(i,j)
            data_cont       = h2_data.GetBinContent(i,j)
            bkg_cont        = h2_bkg.GetBinContent(i,j)
            pull            = calculatePull(data_cont,bkg_cont,data_err_lo,data_err_up,bkg_err)
            #pull            = calculatePull_quantile(data_cont,bkg_cont)
            if(abs(pull)>3):
                print("{0} {1} {2:.2f} {3:.4f} {4:.4f}".format(i,j,data_cont,bkg_cont,bkg_err,pull))
            h_pull.Fill(pull)
    return h_pull


def get_1D_pull(h2_bkg,h2_data,region,year,ProjectionY=False):
    h_pull          = r.TH1F("pulls_{0}".format(region),"{0} {1} 1D pulls;Pull;Bins/0.05".format(region),16,-4,4)
    h_pull.SetDirectory(0)

    if(ProjectionY):
        h_bkg       = h2_bkg.ProjectionY()
        h_data      = h2_data.ProjectionY()
    else:
        h_bkg       = h2_bkg.ProjectionX()
        h_data      = h2_data.ProjectionX()

    h_data.SetBinErrorOption(1)

    for i in range(1,h_bkg.GetNbinsX()+1):
        data_err_up     = h_data.GetBinErrorUp(i)
        data_err_lo     = h_data.GetBinErrorLow(i)
        bkg_err         = h_bkg.GetBinError(i)
        data_cont       = h_data.GetBinContent(i)
        bkg_cont        = h_bkg.GetBinContent(i)
        pull            = calculatePull(data_cont,bkg_cont,data_err_lo,data_err_up,bkg_err)
        #pull            = calculatePull_quantile(data_cont,bkg_cont)
        #print("{0:.2f} {1:.2f} {2:.2f}".format(data_cont,bkg_cont,pull))
        h_pull.Fill(pull)
    return h_pull




def do_2D_pulls(postfitFile,regions):
    postfitFile = r.TFile.Open(postfitFile)
    total_pull  = r.TH1F("pulls_all","",16,-4,4)
    for region in regions:
        c   = r.TCanvas("tempCanvas","",1500,1500)
        c.cd()
        #Pass
        h2_low_data   = postfitFile.Get("pass_LOW_{0}_postfit/data_obs".format(region))
        h2_sig_data   = postfitFile.Get("pass_SIG_{0}_postfit/data_obs".format(region))
        h2_high_data  = postfitFile.Get("pass_HIGH_{0}_postfit/data_obs".format(region))
        hName         = "data_{0}".format(region)
        h2_Data       = merge_low_sig_high(h2_low_data,h2_sig_data,h2_high_data,hName=hName)
        h2_Data.SetDirectory(0)
        h2_low_bkg   = postfitFile.Get("pass_LOW_{0}_postfit/TotalBkg".format(region))
        h2_sig_bkg   = postfitFile.Get("pass_SIG_{0}_postfit/TotalBkg".format(region))
        h2_high_bkg  = postfitFile.Get("pass_HIGH_{0}_postfit/TotalBkg".format(region))
        hName        = "bkg_{0}".format(region)
        h2_Bkg       = merge_low_sig_high(h2_low_bkg,h2_sig_bkg,h2_high_bkg,hName=hName)
        h2_Bkg.SetDirectory(0)

        #Fail
        h2_low_data   = postfitFile.Get("fail_LOW_{0}_postfit/data_obs".format(region))
        h2_sig_data   = postfitFile.Get("fail_SIG_{0}_postfit/data_obs".format(region))
        h2_high_data  = postfitFile.Get("fail_HIGH_{0}_postfit/data_obs".format(region))
        hName         = "dataFail_{0}".format(region)
        h2_DataFail   = merge_low_sig_high(h2_low_data,h2_sig_data,h2_high_data,hName=hName)
        h2_DataFail.SetDirectory(0)
        h2_low_bkg   = postfitFile.Get("fail_LOW_{0}_postfit/TotalBkg".format(region))
        h2_sig_bkg   = postfitFile.Get("fail_SIG_{0}_postfit/TotalBkg".format(region))
        h2_high_bkg  = postfitFile.Get("fail_HIGH_{0}_postfit/TotalBkg".format(region))
        hName        = "bkgFail_{0}".format(region)
        h2_BkgFail   = merge_low_sig_high(h2_low_bkg,h2_sig_bkg,h2_high_bkg,hName=hName)
        h2_DataFail.SetDirectory(0)


        #tempF = r.TFile.Open("test.root","RECREATE")
        #tempF.cd()
        #h2_Bkg.

        #h_pull       = get_2D_pull(h2_Bkg,h2_Data,region,h2Fail=h2_DataFail)
        h_pull       = get_2D_pull(h2_Bkg,h2_Data,region,h2Fail="")
        h_pull_temp       = get_2D_pull(h2_BkgFail,h2_DataFail,region,h2Fail=h2_DataFail)
        #h_pull.Add(h_pull_temp)
        total_pull.Add(h_pull,1)

        h_pull.SetLineWidth(3)
        h_pull.Fit("gaus","S")
        h_pull.Draw("hist")
        h_pull.GetFunction("gaus").Draw("same")
        c.SaveAs("pulls/pulls_2D_{0}.png".format(region))
        c.Close()

    c = r.TCanvas("tempCanvas","",1500,1500)
    total_pull.SetLineWidth(3)
    total_pull.Fit("gaus","S")
    total_pull.Draw("hist")
    total_pull.GetFunction("gaus").Draw("same")
    c.SaveAs("pulls/pulls_2D_all.png")
    c.Close()
    postfitFile.Close()


def do_2D_pulls_rebinned(postfitFile,years,regions):
    #rebin 2D histos to remove entries with data=0
    postfitFile = r.TFile.Open(postfitFile)
    total_pull  = r.TH1F("pulls_all","",16,-4,4)
    for year in years:
        for region in regions:
            print(year,region)
            c   = r.TCanvas("tempCanvas","",1500,1500)
            c.cd()
            h2_low_data   = postfitFile.Get("pass_LOW_{0}_postfit/data_obs".format(region))
            h2_sig_data   = postfitFile.Get("pass_SIG_{0}_postfit/data_obs".format(region))
            h2_high_data  = postfitFile.Get("pass_HIGH_{0}_postfit/data_obs".format(region))
            hName         = "data_{0}".format(region)
            h2_Data       = merge_low_sig_high(h2_low_data,h2_sig_data,h2_high_data,hName=hName)
            h2_Data       = rebinHisto(h2_Data,"h2_data_rebinned")
            h2_Data.SetDirectory(0)
            h2_low_bkg   = postfitFile.Get("pass_LOW_{0}_postfit/TotalBkg".format(region))
            h2_sig_bkg   = postfitFile.Get("pass_SIG_{0}_postfit/TotalBkg".format(region))
            h2_high_bkg  = postfitFile.Get("pass_HIGH_{0}_postfit/TotalBkg".format(region))
            hName        = "bkg_{0}".format(region)
            h2_Bkg       = merge_low_sig_high(h2_low_bkg,h2_sig_bkg,h2_high_bkg,hName=hName)
            h2_Bkg       = rebinHisto(h2_Bkg,"h2_bkg_rebinned")
            h2_Bkg.SetDirectory(0)
            h_pull       = get_2D_pull(h2_Bkg,h2_Data,region,year)
            total_pull.Add(h_pull,1)

            h_pull.SetLineWidth(3)
            h_pull.Fit("gaus","S")
            h_pull.Draw("hist")
            h_pull.GetFunction("gaus").Draw("same")
            c.SaveAs("pulls/pulls_2D_rebinned_{0}.png".format(region))
            c.Close()

    c = r.TCanvas("tempCanvas","",1500,1500)
    total_pull.SetLineWidth(3)
    total_pull.Fit("gaus","S")
    total_pull.Draw("hist")
    total_pull.GetFunction("gaus").Draw("same")
    c.SaveAs("pulls/pulls_2D_rebinned_all.png")
    c.Close()
    postfitFile.Close()


def do_1D_pulls(postfitFile,years,regions,ProjectionY=False):
    postfitFile = r.TFile.Open(postfitFile)
    total_pull  = r.TH1F("pulls_all","",16,-4,4)
    for year in years:
        for region in regions:
            print(year,region)
            c   = r.TCanvas("tempCanvas","",1500,1500)
            c.cd()
            h2_low_data   = postfitFile.Get("pass_LOW_{0}_postfit/data_obs".format(region))
            h2_sig_data   = postfitFile.Get("pass_SIG_{0}_postfit/data_obs".format(region))
            h2_high_data  = postfitFile.Get("pass_HIGH_{0}_postfit/data_obs".format(region))
            hName         = "data_{0}".format(region)
            h2_Data       = merge_low_sig_high(h2_low_data,h2_sig_data,h2_high_data,hName=hName)
            h2_Data.SetDirectory(0)
            h2_low_bkg   = postfitFile.Get("pass_LOW_{0}_postfit/TotalBkg".format(region))
            h2_sig_bkg   = postfitFile.Get("pass_SIG_{0}_postfit/TotalBkg".format(region))
            h2_high_bkg  = postfitFile.Get("pass_HIGH_{0}_postfit/TotalBkg".format(region))
            hName        = "bkg_{0}".format(region)
            h2_Bkg       = merge_low_sig_high(h2_low_bkg,h2_sig_bkg,h2_high_bkg,hName=hName)
            h2_Bkg.SetDirectory(0)
            h_pull       = get_1D_pull(h2_Bkg,h2_Data,region,year,ProjectionY=ProjectionY)
            total_pull.Add(h_pull,1)

            h_pull.SetLineWidth(3)
            h_pull.Fit("gaus","S")
            h_pull.Draw("hist")
            h_pull.GetFunction("gaus").Draw("same")
            if(ProjectionY):
                c.SaveAs("pulls/pulls_1D_MJJ_{0}.png".format(region))
            else:
                c.SaveAs("pulls/pulls_1D_MJY_{0}.png".format(region))
            c.Close()

    c = r.TCanvas("tempCanvas","",1500,1500)
    total_pull.SetLineWidth(3)
    total_pull.Fit("gaus","S")
    total_pull.Draw("hist")
    total_pull.GetFunction("gaus").Draw("same")
    if(ProjectionY):
        c.SaveAs("pulls/pulls_1D_MJJ_all.png")
    else:
        c.SaveAs("pulls/pulls_1D_MJY_all.png")        
    c.Close()
    postfitFile.Close()

oneDimPulls  = False
MJJ = True
regions = ["LL","TT"]
fitDir = sys.argv[1]
if("RunII" in fitDir):
    years   = ["2016","2017","2018"]
else:
    years   = [fitDir.split("_")[0]]
postfitFile = fitDir+"/postfitshapes_b.root"

#Plot data
# postfitFile = r.TFile.Open(postfitFile)
# histos = []
# for region in regions:
#     for year in years:
#         print(region,year)
#         h2_low_data   = postfitFile.Get("pass_LOW_{0}_postfit/data_obs".format(region))
#         h2_sig_data   = postfitFile.Get("pass_SIG_{0}_postfit/data_obs".format(region))
#         h2_high_data  = postfitFile.Get("pass_HIGH_{0}_postfit/data_obs".format(region))
#         hName         = "data_{0}".format(region)
#         hData         = merge_low_sig_high(h2_low_data,h2_sig_data,h2_high_data,hName=hName)
#         hData.SetDirectory(0)
#         histos.append(hData)
# postfitFile.Close()
# f = r.TFile.Open("mergeHistos.root","RECREATE")
# f.cd()
# print(len(histos))
# for h in histos:
#     h.Write()
# f.Close()

do_2D_pulls(postfitFile,regions)
#do_2D_pulls_rebinned(postfitFile,years,regions)
#do_1D_pulls(postfitFile,years,regions,ProjectionY=False)
#do_1D_pulls(postfitFile,years,regions,ProjectionY=True)
