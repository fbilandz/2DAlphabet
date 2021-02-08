from TwoDAlphabetClass import TwoDAlphabet, runMLFit
from RunIIMaker import RunIIMaker
import sys, traceback
from optparse import OptionParser
import subprocess
import header
import ROOT
from ROOT import *

parser = OptionParser()

parser.add_option('-q', '--tag', metavar='<tag>', type='string', action='store',
                default =   '',
                dest    =   'quicktag',
                help    =   'Assigns a tag for this run')
parser.add_option('-s', '--setParameter', metavar='<param1=1.0,param2=1.0...>', type='string', action='store',
                default =   '',
                dest    =   'setParameter',
                help    =   'String of parameters to set pre-fit. Uses same comma separated format as Combine (V1=1.0,V2=1.0...)')
parser.add_option('--rMin', metavar='<rMin>', type='string', action='store',
                default =   '0',
                dest    =   'rMin',
                help    =   'Minimum bound on r (signal strength)')
parser.add_option('--rMax', metavar='<rMax>', type='string', action='store',
                default =   '5',
                dest    =   'rMax',
                help    =   'Minimum bound on r (signal strength)')
parser.add_option("--recycleAll", action="store_true", 
                default =   False,
                dest    =   "recycleAll",
                help    =   "Recycle everything from the previous run with this tag")
parser.add_option("--recycle", action="store", type='string', 
                default =   '',
                dest    =   "recycle",
                help    =   "Recycle comma separated list of items")
parser.add_option("--skipFit", action="store_true", 
                default =   False,
                dest    =   "skipFit",
                help    =   "Skip fit and go directly to plotting (WARNING: Will use previous fit result if it exists and crash otherwise)")
parser.add_option("--skipPlots", action="store_true", 
                default =   False,
                dest    =   "skipPlots",
                help    =   "Skip plotting")
parser.add_option("--fullRun2", action="store_true", 
                default =   False,
                dest    =   "fullRun2",
                help    =   "Plot sum of years 16, 17, 18. Requires a naming scheme that denotes these years clearly. Still fits years individually.")
parser.add_option("--CL", action="store", type='string',
                default =   '',
                dest    =   "CL",
                help    =   "Command-line options to set for all configs")

(options, args) = parser.parse_args()
inputConfigsAndArgs = args

# Assign and summarize input
stringSwaps = {}
inputConfigs = []
for i,c in enumerate(inputConfigsAndArgs):
    if ':' in c: # specify string swap
        stringSwaps[c.split(':')[0]] = c.split(':')[1]
        print c.split(':')[0] +' = '+c.split(':')[1]
    elif '.json' in c:
        inputConfigs.append(c)

print 'Setting on-fly parameters:'
print '\ttag\t\t = '+options.quicktag
print '\trecycleAll\t = '+str(options.recycleAll)
print '\trecycle\t\t = '+str(options.recycle)
print '\tskipFit\t\t = '+str(options.skipFit)
print 'Remaining arguments:'
for i in inputConfigs:
    print '\t'+i

twoDinstances = []

# If simultaneous fit
# if len(inputConfigs) > 1:
##############
# Instantiate all class instances
recycle = [r for r in options.recycle.split(',') if r !='']
for i in inputConfigs:
    instance = TwoDAlphabet(i,options.quicktag,options.recycleAll,recycle,CLoptions=options.CL.split(','),stringSwaps=stringSwaps)
    twoDinstances.append(instance)

# For each instance, check tags match and if they don't, ask the user for one
for t in twoDinstances:
    if t.tag != twoDinstances[0].tag:
        print 'ERROR: tags in configuration files do not match. '+t.tag+' does not match '+twoDinstances[0].tag+'. Please make sure they match and try again. Quitting...'
        quit()
thistag = twoDinstances[0].tag

# Combine the cards
print 'cd ' + thistag
with header.cd(thistag):
    card_combination_command = 'combineCards.py --X-no-jmax'
    for i in twoDinstances:
        card_combination_command += ' '+i.name+'/card_'+i.name+'.txt'
    card_combination_command += ' > card_'+thistag+'.txt'

    print 'Executing ' + card_combination_command
    subprocess.call([card_combination_command],shell=True)
    for num in range(1,len(twoDinstances)+1):
        subprocess.call(["sed -i 's/ch"+str(num)+"_//g' card_"+thistag+".txt"],shell=True)

if not options.skipFit:
    runMLFit(twoDinstances,options.rMin,options.rMax,systsToSet=options.setParameter,skipPlots=options.skipPlots)

# Plot
if not options.skipPlots:
    with header.cd(thistag):
        covMtrx_File = TFile.Open('fitDiagnostics.root')
        fit_result = covMtrx_File.Get("fit_b")
        if hasattr(fit_result,'correlationMatrix'):
            corrMtrx = header.reducedCorrMatrixHist(fit_result)
            corrMtrxCan = TCanvas('c','c',1400,1000)
            corrMtrxCan.cd()
            corrMtrxCan.SetBottomMargin(0.22)
            corrMtrxCan.SetLeftMargin(0.17)
            corrMtrxCan.SetTopMargin(0.06)

            corrMtrx.Draw('colz')
            corrMtrxCan.Print('correlation_matrix.png','png')

    for t in twoDinstances:
        try:
            t.plotFitResults('b')
        except Exception as exc:
            print traceback.format_exc()
            print exc
            print 'Failed to run b plots for '+t.name
        try:
            t.plotFitResults('s')
        except Exception as exc:
            print traceback.format_exc()
            print exc
            print 'Failed to run s plots for '+t.name

    if options.fullRun2:
        tags = RunIIMaker(thistag)

        runIIs = {}
        for cat in tags:
            for t in twoDinstances:
                if cat in t.name and '17' in t.name:
                    runIIs[cat] = t
                    break

        for cat in runIIs.keys():
            runII = runIIs[cat]
            runII.name = cat+'RunII'
            runII.year = 1
            runII.projPath = runII._projPath()
            runII.plotFitResults('RunII_b')
            runII.plotFitResults('RunII_s')

        # Will steal existing twoDinstances with a slight attribute
        # modification to get it to work for RunII


# for t in twoDinstances:
#     del t
#########
# If single fit
# else:
#     instance = TwoDAlphabet(inputConfigs[0],options.quicktag,options.recycleAll,stringSwaps=stringSwaps)
    
#     if not options.skipFit:
#         runMLFit([instance],options.rMin,options.rMax,systsToSet=options.setParameter,skipPlots=options.skipPlots)
#     thistag = instance.projPath

#     # Plot
#     if not options.skipPlots:
#         try:
#             instance.plotFitResults('b')
#         except Exception as exc:
#             print traceback.format_exc()
#             print exc
#             print 'Failed to run b plots for '+instance.name
#         try:
#             instance.plotFitResults('s')
#         except Exception as exc:
#             print traceback.format_exc()
#             print exc
#             print 'Failed to run s plots for '+instance.name

#     del instance
    