import ROOT as r
import os
from TwoDAlphabet.helpers import cd, execute_cmd
import os.path
from math import sqrt

nuisances=[
"FSR","ISR","W_d2kappa_EW","W_d3kappa_EW","Z_d2kappa_EW","Z_d3kappa_EW",
"d1K_NLO","d1kappa_EW","d2K_NLO","d3K_NLO","jer","jes","jmr",
"jms","lumi","pdfUnc","prefiring16","prefiring17","puUnc","trig"
]

def getUnc(fileName,POI):
    sf_file     = r.TFile.Open(fileName)
    resTree     = sf_file.Get("limit")

    resTree.GetEntry(0)
    SF = getattr(resTree,POI)
    resTree.GetEntry(1)
    uncDn = SF - getattr(resTree,POI)
    resTree.GetEntry(2)
    uncUp = getattr(resTree,POI) - SF
    sf_file.Close()
    return SF, uncUp, uncDn

def runNuisBreakdown(POI):
    if(os.path.isfile("higgsCombine{0}_20.total.MultiDimFit.mH120.root".format(POI))):
        print("higgsCombine{0}_20.total.MultiDimFit.mH120.root".format(POI))
        print("Skipping the calculation of nuisance breakdown")
        #return


    #First fit
    firstFitCmd = "combine TnP.root -M MultiDimFit --algo=singles --saveWorkspace -n zbb.postfit --cminDefaultMinimizerStrategy=0"
    #firstFitCmd = "combine TnP.root -M MultiDimFit --algo=singles --saveWorkspace -n zbb.postfit --cminDefaultMinimizerStrategy=0 --cminDefaultMinimizerTolerance=0.5"
    print(firstFitCmd)
    os.system(firstFitCmd)
    #Scan select POI
    scanCmd     = "combine higgsCombinezbb.postfit.MultiDimFit.mH120.root -M MultiDimFit -n {0}_0.total --algo singles --snapshotName MultiDimFit --setParameterRanges {0}=0,2 -P {0} --floatOtherPOIs=1 --cminDefaultMinimizerStrategy=0".format(POI)
    print(scanCmd)
    os.system(scanCmd)
    freezeParams= ""
    for i,nuis in enumerate(nuisances):
        if not freezeParams:
            freezeParams = nuis
        else:
            freezeParams = "{0},{1}".format(freezeParams,nuis)
        scanCmd = "combine higgsCombinezbb.postfit.MultiDimFit.mH120.root -M MultiDimFit -n {0}_{1}.total --algo singles --snapshotName MultiDimFit --setParameterRanges {0}=0,2 -P {0} --floatOtherPOIs=1 --freezeParameters={2} --cminDefaultMinimizerStrategy=0".format(POI,i+1,freezeParams)
        print(scanCmd)
        os.system(scanCmd)



def getNuisBreakdown(POI,title):
    uncsUp = []
    uncsDn = []
    totFile = "higgsCombine{0}_0.total.MultiDimFit.mH120.root".format(POI)
    SF, uncUp, uncDown = getUnc(totFile,POI)
    uncsUp.append(uncUp)
    uncsDn.append(uncDown)
    for i,nuis in enumerate(nuisances):
        fileName = "higgsCombine{0}_{1}.total.MultiDimFit.mH120.root".format(POI,i+1)
        SF_temp, uncUp, uncDown = getUnc(fileName,POI)
        uncsUp.append(uncUp)
        uncsDn.append(uncDown)

    formatResult(SF,uncsUp,uncsDn,title)

def formatResult(SF,uncsUp,uncsDn,title):
    lines="SF={0:.2f}\n".format(SF)
    lines+="Nuisance,+1 sigma,-1 sigma,+1 sigma nuisance,-1 sigma nuisance\n".format(SF)
    lines+="Total,{0:.3f},{1:.3f},-,-\n".format(uncsUp[0],uncsDn[0])
    for i in range(1,len(uncsUp)):
        name        = nuisances[i-1]
        uncUp       = uncsUp[i]
        uncDn       = uncsDn[i]
        uncUpSqDiff = uncsUp[i-1]**2-uncUp**2
        uncDnSqDiff = uncsDn[i-1]**2-uncDn**2

        if(uncUpSqDiff<0):
            uncUpNuis   = 0
        else:
            uncUpNuis   = sqrt(uncUpSqDiff)
        if(uncDnSqDiff<0):
            uncDnNuis   = 0
        else:
            uncDnNuis   = sqrt(uncDnSqDiff)
            
        lines+="{0},{1:.3f},{2:.3f},{3:.3f},{4:.3f}\n".format(name,uncUp,uncDn,uncUpNuis,uncDnNuis)

    print(lines)
    with open('{0}.csv'.format(title),'w') as oFile:
        oFile.write(lines)  


#years = ["16APV","16","17","18"]
years  = ["17","18"]
#wps   = ["loose","medium","tight"]
#wps   = ["loose","medium"]
wps   = ["medium"]
POIs  = ["SF_ZJets_bc_0","SF_ZJets_bc_1","SF_ZJets_bc_2"]
bestOrders = { 
    "loose" :{"16APV_loose_split":"2" ,"16_loose_split":"2" ,"17_loose_split":"4" ,"18_loose_split":"4"},
    "medium":{"16APV_medium_split":"2","16_medium_split":"2","17_medium_split":"3","18_medium_split":"2"},
    "tight" :{"16APV_tight_split":"2" ,"16_tight_split":"2" ,"17_tight_split":"2" ,"18_tight_split":"2"}
} #Pnet

# bestOrders = { 
#     "medium":{"16APV_medium_split":"2","16_medium_split":"3","17_medium_split":"3","18_medium_split":"4"},
#     "tight" :{"16APV_tight_split":"2" ,"16_tight_split":"2" ,"17_tight_split":"2" ,"18_tight_split":"4"}
# } #DeepDoubleX

#bestOrders = { 
#    "tight" :{"16APV_tight_split":"3" ,"16_tight_split":"3" ,"17_tight_split":"3" ,"18_tight_split":"3"}
#} #Hbb


for year in years:
    for wp in wps:
        bestOrder   = bestOrders[wp]["{0}_{1}_split".format(year,wp)]
        workingArea = "ParticleNet/{0}_{1}_split/{2}_area/".format(year,wp,bestOrder)
        with cd(workingArea):
            for POI in POIs:
                title       = "{0}_{1}_{2}".format(year,wp,POI)
                runNuisBreakdown(POI)
                getNuisBreakdown(POI,title)
