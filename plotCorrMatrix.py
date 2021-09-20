import header
import sys
from ROOT import *

gROOT.SetBatch(True)

def reducedCorrMatrixHist(fit_result,varsOfInterest=[],blacklist=[]):
    blacklist.append("Fail_")
    blacklist.append("prop_")
    gStyle.SetOptStat(0)
    # ROOT.gStyle.SetPaintTextFormat('.3f')
    CM = fit_result.correlationMatrix()
    finalPars = fit_result.floatParsFinal()

    nParams = CM.GetNcols()
    finalParamsDict = {}
    for cm_index in range(nParams):
        tempVarName = finalPars.at(cm_index).GetName()
        if varsOfInterest == []:
            if any(blTag in tempVarName for blTag in blacklist):
                continue
            else:
                finalParamsDict[tempVarName] = cm_index
        else:
            if any(wlTag in tempVarName for wlTag in varsOfInterest):            
                finalParamsDict[tempVarName] = cm_index

    nFinalParams = len(finalParamsDict.keys())
    out = TH2D('correlation_matrix','correlation_matrix',nFinalParams,0,nFinalParams,nFinalParams,0,nFinalParams)
    out_txt = open('correlation_matrix.txt','w')

    for out_x_index, paramXName in enumerate(sorted(finalParamsDict.keys())):
        cm_index_x = finalParamsDict[paramXName]
        for out_y_index, paramYName in enumerate(sorted(finalParamsDict.keys())):
            cm_index_y = finalParamsDict[paramYName]
            if cm_index_x > cm_index_y:
                out_txt.write('%s:%s = %s\n'%(paramXName,paramYName,CM[cm_index_x][cm_index_y]))
            out.Fill(out_x_index+0.5,out_y_index+0.5,CM[cm_index_x][cm_index_y])

        out.GetXaxis().SetBinLabel(out_x_index+1,finalPars.at(cm_index_x).GetName())
        out.GetYaxis().SetBinLabel(out_x_index+1,finalPars.at(cm_index_x).GetName())
    out.SetMinimum(-1)
    out.SetMaximum(+1)

    return out

thistag = sys.argv[1]
#blacklist = ["MCRpfUnc","muonI","pref","muonTrig","trigHT","pnet","purewt","pdfrewt","btagSF","rpf"]
blacklist = ["17","18","rpf"]
blacklists = [["17","18","rpf"],["16","18","rpf"],["16","17","rpf"],[]]

with header.cd(thistag):
    covMtrx_File = TFile.Open('fitDiagnostics.root')
    fit_result = covMtrx_File.Get("fit_b")
    if hasattr(fit_result,'correlationMatrix'):
        for i,subset in enumerate(["16","17","18","full"]):
            corrMtrx = reducedCorrMatrixHist(fit_result,blacklist=blacklists[i])
            #corrMtrx = reducedCorrMatrixHist(fit_result,varsOfInterest=whitelist)
            corrMtrxCan = TCanvas('c','c',1400,1000)
            corrMtrxCan.cd()
            corrMtrxCan.SetBottomMargin(0.22)
            corrMtrxCan.SetLeftMargin(0.17)
            corrMtrxCan.SetTopMargin(0.06)

            corrMtrx.Draw('colz')
            corrMtrxCan.Print('correlation_matrix_{0}.png'.format(subset),'png')
