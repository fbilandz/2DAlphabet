import ROOT as r
import subprocess
import sys
import os


def runCommand(command,dryrun=False):
    print(command)
    if not dryrun:
        subprocess.call([command],shell=True)

fitDir  = sys.argv[1]
configs = sys.argv[2:]
configString = " ".join(configs)

if("_LL_" in configString or "_TT_" in configString):
    rateParamsCmds  = ""
    rateParamsCmds+="echo 'bqqT_16       rateParam *TT 16_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqL_16       rateParam *LL 16_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqT_16        rateParam *TT 16_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqL_16        rateParam *LL 16_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqT_17       rateParam *TT 17_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqL_17       rateParam *LL 17_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqT_17        rateParam *TT 17_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqL_17        rateParam *LL 17_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqT_18       rateParam *TT 18_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqL_18       rateParam *LL 18_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqT_18        rateParam *TT 18_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqL_18        rateParam *LL 18_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)

else:
    rateParamsCmds  = ""
    rateParamsCmds+="echo 'bqqT_16       rateParam *AL_T 16_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqL_16       rateParam *AL_L 16_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqT_16        rateParam *AL_T 16_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqL_16        rateParam *AL_L 16_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqT_17       rateParam *AL_T 17_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqL_17       rateParam *AL_L 17_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqT_17        rateParam *AL_T 17_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqL_17        rateParam *AL_L 17_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqT_18       rateParam *AL_T 18_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqqL_18       rateParam *AL_L 18_TTbar_bqq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqT_18        rateParam *AL_T 18_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)
    rateParamsCmds+="echo 'bqL_18        rateParam *AL_L 18_TTbar_bq 1.0 [0.0,5.0]' >> card_{0}.txt\n".format(fitDir)




mlfitCmd        = "python run_MLfit.py {0} -q {1} --skipFit --skipPlots MX1600_MY125:MX1500_MY125".format(configString,fitDir)
cdCmd           = "cd {0}".format(fitDir)
cpHadCard       = "cp card_{0}.txt card_{0}_backup.txt".format(fitDir)
cpCmd           = "cp ../CR_cards/CR_*.txt ."
combinedCardCmd ="combineCards.py ch1=card_{0}.txt CR_L_16=CR_L_16.txt CR_T_16=CR_T_16.txt CR_L_17=CR_L_17.txt CR_T_17=CR_T_17.txt CR_L_18=CR_L_18.txt CR_T_18=CR_T_18.txt> combinedCard.txt".format(fitDir)


sedCmd      = "sed -i -e 's/\(ch1_\|ch1=\|T_CR\|L_CR\)//g' combinedCard.txt"

combineCmd  = "combine -M FitDiagnostics -d combinedCard.txt --setParameters r=1 --saveWorkspace --saveShapes --saveWithUncertainties  --saveNormalizations   --cminDefaultMinimizerStrategy 0  --rMin 0 --rMax 10 -v 2 --robustHesse 1 |& tee combine_output.txt"

postfitSCmd = "PostFit2DShapesFromWorkspace -w higgsCombineTest.FitDiagnostics.mH120.root -o postfitshapes_s.root -f fitDiagnostics.root:fit_s --postfit --sampling --samples 100"
postfitBCmd = "PostFit2DShapesFromWorkspace -w higgsCombineTest.FitDiagnostics.mH120.root -o postfitshapes_b.root -f fitDiagnostics.root:fit_b --postfit --sampling --samples 100"

returnCmd   = "cd .."
plotCmd     = mlfitCmd.replace("--skipPlots","--recycleAll")

runCommand(mlfitCmd)
print(cdCmd)
os.chdir(fitDir)
runCommand(cpHadCard)
for rateParamsCmd in rateParamsCmds.split("\n"):
    runCommand(rateParamsCmd)
runCommand(cpCmd)
runCommand(combinedCardCmd)
runCommand(sedCmd)
runCommand(combineCmd)
plot = raw_input("Proceed with plotting?: [y/N]")
if("y" in plot):
    runCommand(postfitSCmd)
    runCommand(postfitBCmd)
    print(returnCmd)
    os.chdir("..")
    runCommand(plotCmd)



