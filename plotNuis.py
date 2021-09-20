import os
from ROOT import *
import header
import sys



def plotNuisances():
    diffnuis_cmd = 'python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnostics.root --abs -g nuisance_pulls.root'
    header.executeCmd(diffnuis_cmd)

    # systematic_analyzer_cmd = 'python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py '+card_name+' --all -f html > systematics_table.html'
    # header.executeCmd(systematic_analyzer_cmd)

    #Make a PDF of the nuisance_pulls.root
    if os.path.exists('nuisance_pulls.root'):
        nuis_file = TFile.Open('nuisance_pulls.root')
        # nuis_can = nuis_file.Get('nuisances')
        # nuis_can.Print('nuisance_pulls.pdf','pdf')
        # nuis_file.Close()
        c = nuis_file.Get("nuisances")
        h = c.GetPrimitive("prefit_nuisancs")
        for i in range(0,4):
            h.GetXaxis().SetRangeUser(i*20,(i+1)*20)
            gStyle.SetOptStat(000000)
            c.Update()
            c.SaveAs("nuis_{0}.pdf".format(i))


def printFlatParams():
    fit_file   = TFile.Open("fitDiagnostics.root")
    fit_result = fit_file.Get("fit_b")
    rateParams = ["bqL_16","bqqL_16","bqT_16","bqqT_16","bqL_17","bqqL_17","bqT_17","bqqT_17","bqL_18","bqqL_18","bqT_18","bqqT_18"]
    for param in rateParams:
        rrv    = fit_result.floatParsFinal().find(param)
        if(rrv):
            row = ["%-10s"%param, "%10.3f"%rrv.getVal(), "+/-%2.3f"%rrv.getError()]
            print("{:<10} {:5} {:>5}").format(*row)

def printAllParams():
    fit_file   = TFile.Open("fitDiagnostics.root")
    fit_result = fit_file.Get("fit_b")
    fitRes     = fit_result.floatParsFinal()
    for i in range(len(fitRes)):
        rrv = fitRes[i]
        if("Fail_bin" in rrv.GetName() or "prop_" in rrv.GetName()):
            continue
        row = ["|| %-10s"%rrv.GetName(), "%10.3f"%rrv.getVal(), "+/-%2.3f"%rrv.getError()]
        print("{:<10} {:5} {:>5}").format(*row)



fitDir = sys.argv[1]
print(fitDir)
os.chdir(fitDir)
plotNuisances()
#printFlatParams()
printAllParams()
