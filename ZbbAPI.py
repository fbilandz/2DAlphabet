from time import time
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball, cd, execute_cmd
from TwoDAlphabet.ftest import FstatCalc
import os

'''--------------------------Helper functions---------------------------'''
def _get_other_region_names(pass_reg_name):
    return pass_reg_name, pass_reg_name.replace('pass','loose'),pass_reg_name.replace('pass','fail')

def _select_bkg(row, args):
    '''Used by the Ledger.select() method to create a subset of a Ledger.
    This function provides the logic to determine which entries/rows of the Ledger
    to keep for the subset. The first argument should always be the row to process.
    The arguments that follow will be the other arguments of Ledger.select().
    This function should ALWAYS return a bool that signals whether to keep (True)
    or drop (False) the row.

    To check if entries in the Ledger pass, we can access a given row's
    column value via attributes which are named after the columns (ex. row.process
    gets the "process" column). One can also access them as keys (ex. row["process"]).

    In this example, we want to select for signals that have a specific string
    in their name ("process"). Thus, the first element of `args` contains the string
    we want to find.

    We also want to pick a TF to use so the second element of `args` contains a
    string to specify the Background_args[1] process we want to use.

    Args:
        row (pandas.Series): The row to evaluate.
        args (list): Arguments to pass in for the evaluation.

    Returns:
        Bool: True if keeping the row, False if dropping.
    '''
    poly_order = args[0]
    if row.process_type == 'SIGNAL':
        return True
    elif 'qcd_' in row.process:
        if row.process == 'qcd_'+poly_order:
            return True
        else:
            return False
    else:
        return True

def _load_CR_rpf(poly_order):
    twoD_CRonly = TwoDAlphabet('XHYfits_CR','XHYbbWW.json', loadPrevious=True)
    params_to_set = twoD_CRonly.GetParamsOnMatch('rpf.*'+poly_order, 'MX_2000_MY_800_area', 'b')
    return {k:v['val'] for k,v in params_to_set.items()}

def _load_CR_rpf_as_SR(poly_order):
    params_to_set = {}
    for k,v in _load_CR_rpf(poly_order).items():
        params_to_set[k.replace('CR','SR')] = v
    return params_to_set

def _generate_constraints(nparams):
    out = {}
    for i in range(nparams):
        if i == 0:
            out[i] = {"MIN":0,"MAX":10,"NOM":1}
        else:
            out[i] = {"MIN":-20,"MAX":20,"NOM":0}
    return out


def _gof_for_FTest(twoD, subtag, card_or_w='card.txt'):

    run_dir = twoD.tag+'/'+subtag
    
    with cd(run_dir):
        gof_data_cmd = [
            'combine -M GoodnessOfFit',
            '-d '+card_or_w,
            '--algo=saturated',
            '-n _gof_data'
        ]

        gof_data_cmd = ' '.join(gof_data_cmd)
        execute_cmd(gof_data_cmd)

# we are working in a 2D space, so linear in X, linear in Y just change the shape of the transfer function
_rpf_options = {
    '0x0': {
        'form': '0.002*(@0)',
        'constraints': _generate_constraints(1)
    },
    '1x0': {
        'form': '0.002*(@0+@1*x)',
        'constraints': _generate_constraints(2)
    },
    '0x1': {
        'form': '0.002*(@0+@1*y)',
        'constraints': _generate_constraints(2)
    },
    '1x1': {
        'form': '0.002*(@0+@1*x)*(1+@2*y)',
        'constraints': _generate_constraints(3)
    },
    '1x2': {
        'form': '0.002*(@0+@1*x)*(1+@2*y+@3*y*y)',
        'constraints': _generate_constraints(4)
    },
    '2x1': {
        'form': '0.002*(@0+@1*x+@2*x*x)*(1+@3*y)',
        'constraints': _generate_constraints(4)
    },
    '2x2': {
        'form': '0.002*(@0+@1*x+@2*x*x)*(1+@3*y+@4*y*y)',
        'constraints': _generate_constraints(5)
    },
    '2x3': {
        'form': '0.002*(@0+@1*x+@2*x*x)*(1+@3*y+@4*y*y+@5*y*y*y)',
        'constraints': _generate_constraints(6)
    },
    '3x2': {
        'form': '0.002*(@0+@1*x+@2*x*x+@3*x*x*x)*(1+@4*y+@5*y*y)',
        'constraints': _generate_constraints(6)
    }
}

'''---------------Primary functions---------------------------'''
def test_make():
    '''Constructs the workspace for either the CR or SR (a different function
    could build them simultanesouly but in this example, we don't care to fit
    the two simultanesouly so separate treatment is fine).
    '''

    # Create the twoD object which starts by reading the JSON config and input arguments to
    # grab input simulation and data histograms, rebin them if needed, and save them all
    # in one place (organized_hists.root). The modified JSON config (with find-replaces applied, etc)
    # is also saved as runConfig.json. This means, if you want to share your analysis with
    # someone, they can grab everything they need from this one spot - no need to have access to
    # the original files! (Note though that you'd have to change the config to point to organized_hists.root).
    twoD = TwoDAlphabet(working_area, '/afs/cern.ch/work/m/mrogulji/UL_X_YH/Zbb_SF/CMSSW_10_6_14/src/2DAlphabet/configs/2016/ZbbConfig.json', loadPrevious=False)
    qcd_hists = twoD.InitQCDHists() # Create the data - BKGs histograms


    binning_f, _ = twoD.GetBinningFor("F")

    # Next we construct the Alphabet objects which all inherit from the Generic2D class.
    # This class constructs and stores RooAbsArg objects (RooRealVar, RooFormulaVar, etc)
    # which represent each bin in the space.

    # First we make a BinnedDistribution which is a collection of RooRealVars built from a starting
    # histogram (`qcd_hists[f]`). These can be set to be constants but, if not, they become free floating
    # parameters in the fit.
    fail_name = 'qcd_fail'
    qcd_f = BinnedDistribution(
                fail_name, qcd_hists["F"],
                binning_f, constant=False
            )

    # We'll then book a flat TF which will be used to transfer between loose and pass
    # We keep it out of the loop below though because this will keep the same form
    # while the fail-to-loose TF changes with the different possible options.

    # We add it to `twoD` so its included when making the RooWorkspace and ledger.
    # We specify the name of the process, the region it lives in, and the object itself.
    # The process is assumed to be a background and colored yellow but this can be changed
    # with optional arguments.
    twoD.AddAlphaObj('qcd',"F",qcd_f)

    # As a global variables, we've defined some different transfer function (TF) options.
    # We only want to include one of these at the time of fitting but we want to construct
    # them all right now so we can pick and choose later.
    for opt_name, opt in _rpf_options.items():
        # We have two regions determined by a TF, "pass" and "loose" with the "pass"
        # being a simple flat scaling of the loose. The functional form and the
        # dictionary of constraints is defined in _rpf_options so we just plug
        # these in, being careful to name the objects uniquely (this affects
        # the naming of the RooFormulaVars created, which need to be unique).

        # The ParametricFunction class is the same as the BinnedDistribution except
        # the bins are RooFormulaVars constructed from the input formula with the
        # "x" and "y" taken as the centers of each bin.
        # The constraints option takes as input a dictionary with keys that control
        # the minimum, maximum, and error (initial step) of each parameter. It can
        # also be used to specify if the parameter should be unconstrainted (flatParam)
        # or Gaussian constrained (param <mu> <sigma>).
        qcd_rpfL = ParametricFunction(
                    fail_name.replace('fail','rpfL')+'_'+opt_name,
                    binning_f, opt['form'],
                    constraints=opt['constraints']
                )

        qcd_rpfT = ParametricFunction(
                    fail_name.replace('fail','rpfT')+'_'+opt_name,
                    binning_f, opt['form'],
                    constraints=opt['constraints']
            )

        # Of course, what we actually need is these TFs multiplied by something else:
        #     qcd_l = qcd_f*rpfL
        #     qcd_p = qcd_l*rpfT
        # The Multiply method will make a new set of RooFormulaVars defined by multiplying the RooAbsArgs
        # of each object together. Other methods exist for adding and dividing (where Add() can take a optional factor
        # so that subtraction is possible).
        qcd_l = qcd_f.Multiply(fail_name.replace('fail','loose')+'_'+opt_name, qcd_rpfL)
        qcd_t = qcd_f.Multiply(fail_name.replace('fail','tight')+'_'+opt_name, qcd_rpfT)

        # Now add the final models to the `twoD` object for tracking
        # Note that we have unique process names so they are identifiable
        # but we give them different titles so that they look pretty in
        # the final plot legends.
        twoD.AddAlphaObj('qcd_'+opt_name,"L",qcd_l,title='qcd')
        twoD.AddAlphaObj('qcd_'+opt_name,"T",qcd_t,title='qcd')

    # Save() will save the RooWorkspace and the ledgers and other associated pieces
    # so the twoD object can be reconstructed later. If this line doesn't run or
    # if something in the above needs to change, everything will need to be re-run to this point.
    twoD.Save()

def test_fit():
    '''Loads a TwoDAlphabet object from an existing project area, selects
    a subset of objects to run over (a specific signal and TF), makes a sub-directory
    to store the information, and runs the fit in that sub-directory. To make clear
    when a directory/area is being specified vs when a signal is being selected,
    I've redundantly prepended the "subtag" argument with "_area".
    '''
    # So that the find-replace in the config doesn't need to be done again if I want
    # the SR (since it would have been performed already by test_make()), I grab
    # the runConfig.json that's already been saved in the created directory.
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json'%working_area, loadPrevious=True)
    # Access the Ledger and perform a selection on it to create a subset
    # from which to build the card. One can modify the Ledger DataFrames
    # manually to do more sophisticated manipulations but the select()
    # method will not modify the Ledger in-place. It always generates a new Ledger
    # which, by itself, is only stored in memory.

    # Create a subset of the primary ledger using the select() method.
    # The select() method takes as a function as its first argument
    # and any args to pass to that function as the remiaining arguments
    # to select(). See _select_signal for how to construct the function.
    subset = twoD.ledger.select(_select_bkg, polyOrder)

    # Make card reads the ledger and creates a Combine card from it.
    # The second argument specifices the sub-directory to save the card in.
    # MakeCard() will also save the corresponding Ledger DataFrames as csvs
    # in the sub-directory for later reference/debugging. By default, MakeCard()
    # will reference the base.root workspace in the first level of the project directory
    # (../ relative to the card). However, one can specify another path if a different
    # workspace is desired. Additionally, a different dataset can be supplied via
    # toyData but this requires supplying almost the full Combine card line and
    # is reserved for quick hacks by those who are familiar with Combine cards.
    twoD.MakeCard(subset, '{0}_area'.format(polyOrder))

    # Run the fit! Will run in the area specified by the `subtag` (ie. sub-directory) argument
    # and use the card in that area. Via the cardOrW argument, a different card or workspace can be
    # supplied (passed to the -d option of Combine).
    twoD.MLfit('{0}_area'.format(polyOrder),verbosity=0)

def test_plot():
    '''Load the twoD object again and run standard plots for a specific subtag.
    Assumes loading the Ledger in this sub-directory but a different one can
    be provided if desired.
    '''
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json'%working_area, loadPrevious=True)
    subset = twoD.ledger.select(_select_bkg, polyOrder)
    twoD.StdPlots('{0}_area'.format(polyOrder), subset)

def test_GoF():
    '''Perform a Goodness of Fit test using an existing working area.
    Requires using data so SRorCR is enforced to be 'CR' to avoid accidental unblinding.
    '''

    twoD = TwoDAlphabet(working_area, '%s/runConfig.json'%working_area, loadPrevious=True)
    # Run the Goodness of fit test with 500 toys, r floating, TF parameters set to prefit.
    # This method always runs the evaluation on data interactively but the toy generation and evaluation
    # can be sent to condor with condor=True and split over several jobs with njobs=<int>.
    # Note that running a GoF test without data is relatively meaningless so by using this method,
    # you must unblind data. If you wish to use a toy dataset instead, you should set that
    # up when making the card.
    twoD.GoodnessOfFit(
        '{0}_area'.format(polyOrder), ntoys=500, freezeSignal=False,
        condor=True, njobs=10
    )

    # Note that no plotting is done here since one needs to wait for the condor jobs to finish first.
    # See test_GoF_plot() for plotting (which will also collect the outputs from the jobs).

def test_SigInj(SRorCR):
    '''Perform a signal injection test'''
    assert SRorCR in ['SR','CR']

    poly_order = '0x0'
    signame = 'MX_2000_MY_800'
    working_area = 'XHYfits_'+SRorCR
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json'%working_area, loadPrevious=True)

    # If the card doesn't exist, make it (in the case that test_fit() wasn't run first).
    if not os.path.exists(twoD.tag+'/'+signame+'_area/card.txt'):
        subset = twoD.ledger.select(_select_signal, signame, poly_order)
        twoD.MakeCard(subset, signame+'_area')

    # Perform the signal injection test with r=0 and with 500 toys split over 10 jobs on condor.
    # Because the data is blinded, we feed in the parameters from a previous fit so that we
    # have a model from which to generate toys.
    twoD.SignalInjection(
        signame+'_area', injectAmount=0,
        ntoys=500,
        blindData=True,
        setParams=_load_CR_rpf_as_SR(poly_order),
        condor=True, njobs=10)

def test_GoF_plot():
    plot.plot_gof(working_area,'{0}_area'.format(polyOrder), condor=True)

def test_SigInj_plot(SRorCR):
    '''Plot the signal injection test for r=0 injected and stored in XHYfits_<SRorCR>/MX_2000_MY_800_area
    (condor=True indicates that condor jobs need to be unpacked)'''
    plot.plot_signalInjection('XHYfits_'+SRorCR,'MX_2000_MY_800_area', injectedAmount=0,condor=True)

def test_Impacts(SRorCR):
    '''Calculate the nuisance parameter impacts. The parameters corresponding to the unconstrained bins
    of the fail region are ignored. Assumes that a fit has already been performed so that the post-fit
    uncertainties can be used for the scans. However, another card or workspace can be specified as well
    as a dictionary of parameters to set before running (setParams). With blindData=True, a pre-fit Asimov
    toy is generated for the sake of performing the scans. Since we're only using the CR here, blindData
    is set to False.
    '''
    assert SRorCR == 'SR' # Setup for either SR or CR but don't want to unblind accidentally until ready
    working_area = 'XHYfits_'+SRorCR
    twoD = TwoDAlphabet(working_area, '%s/runConfig.json'%working_area, loadPrevious=True)

    # We need to run impacts in the SR for them to make sense but we can't use the data in the SR while blinded.
    # So we need a toy to play with instead.
    subset = twoD.ledger.select(_select_signal, 'MX_2000_MY_800','0x0')
    # Make a new area to play in
    twoD.MakeCard(subset, 'MX_2000_MY_800_impactArea')

    # Use the card from the main working area to generate the toy
    toy_file_path = twoD.GenerateToys(
        '_impactToy', 'MX_2000_MY_800_impactArea',
        card='../MX_2000_MY_800_area/card.txt',
        workspace=None,
        ntoys=1, seed=123456, expectSignal=0,
        setParams=_load_CR_rpf_as_SR('0x0')
    )
    # Remake the card
    twoD.Impacts(
        'MX_2000_MY_800_impactArea',
        cardOrW='card.txt',
        extra='-t 1 --toysFile %s'%toy_file_path.split('/')[-1]
    )

def test_generate_for_SR():
    '''NOTE: This is an expert-level manipulation that requires understanding the underlying Combine
    commands. Use and change it only if you understand what each step is doing.

    Use the CR fit result to generate and fit a toy in the SR (without looking at SR data).
    There are two ways to do this which will be broken up into toyArea1 and toyArea2.'''
    # Load in the SR TwoDAlphabet object
    twoD = TwoDAlphabet('XHYfits_SR', 'XHYfits_SR/runConfig.json', loadPrevious=True)
    subset = twoD.ledger.select(_select_signal, 'MX_2000_MY_800','0x0')
    params_to_set = _load_CR_rpf_as_SR('0x0')

    ###################################
    #-------- Version 1 --------------#
    ###################################
    # We'll make a card for each version to ensure the directory structure is made - they will be identical though to start.
    twoD.MakeCard(subset, 'MX_2000_MY_800_toyArea1')

    # Perform a fit as normal but via the `extra` arg, provide some commands
    # directly to combine to generate 1 toy, with seed 123456, and with r=0.
    # Note that --expectSignal 0 will generate with r=0 AND fit with r=0.
    twoD.MLfit(
        subtag='MX_2000_MY_800_toyArea1',
        setParams=params_to_set,
        rMin=0,rMax=5,verbosity=0,
        extra='-t 1 -s 123456 --expectSignal 0'
    )
    # Plot!
    twoD.StdPlots('MX_2000_MY_800_toyArea1',ledger=subset)

    ###################################
    #-------- Version 2 --------------#
    ###################################
    # We'll make a card for each version to ensure the directory structure is made - they will be identical though to start.
    twoD.MakeCard(subset, 'MX_2000_MY_800_toyArea2')
    # First generate a toy by itself. This means we can set r for *just* this step
    # as opposed to Version 1 where r was set for generation and for fitting.
    # Note that this method will generate frequentist toys but always skip the frequentist fit.
    # So if you'd like to generate from a post-fit workspace, you should fit first
    # and then provide a workspace snapshot
    toy_file_path = twoD.GenerateToys(
        'toys', 'MX_2000_MY_800_toyArea2',
        card='card.txt', workspace=None, # A card or workspace MUST be defined manually or one of these options should be set to True to use a default.
        ntoys=1, seed=123456, expectSignal=0,
        setParams=params_to_set
    )
    # Perform a fit as normal but via the `extra` arg, tell combine
    # to access our already-generated toy.
    # Note that r is now freely floating in this fit again.
    twoD.MLfit(
        subtag='MX_2000_MY_800_toyArea2',
        setParams=params_to_set,
        rMin=0,rMax=5,verbosity=0,
        extra='-t 1 --toysFile=%s'%toy_file_path.split('/')[-1]
    )
    # Plot!
    twoD.StdPlots('MX_2000_MY_800_toyArea2',ledger=subset)


def test_FTest(poly1,poly2):
    '''Perform an F-test using existing working areas.
    '''

    twoD    = TwoDAlphabet(working_area, '%s/runConfig.json'%working_area, loadPrevious=True)

    binning = twoD.binnings["default"]
    nBins   = (len(binning.xbinList)-1)*(len(binning.ybinList)-1)

    #Get number of RPF params and run GoF for poly1
    params1 = twoD.ledger.select(_select_bkg, poly1).alphaParams
    rpfSet1 = params1[params1["name"].str.contains("rpf")]
    nRpfs1  = len(rpfSet1.index)
    _gof_for_FTest(twoD, "{0}_area".format(poly1), card_or_w='card.txt')
    gofFile1= working_area+"/{0}_area/higgsCombine_gof_data.GoodnessOfFit.mH120.root".format(poly1)

    #Get number of RPF params and run GoF for poly2
    params2 = twoD.ledger.select(_select_bkg, poly2).alphaParams
    rpfSet2 = params2[params2["name"].str.contains("rpf")]
    nRpfs2  = len(rpfSet2.index)
    _gof_for_FTest(twoD, "{0}_area".format(poly2), card_or_w='card.txt')
    gofFile2= working_area+"/{0}_area/higgsCombine_gof_data.GoodnessOfFit.mH120.root".format(poly2)

    base_fstat = FstatCalc(gofFile1,gofFile2,nRpfs1,nRpfs2,nBins)
    print(base_fstat)

    def plot_FTest(base_fstat,nRpfs1,nRpfs2,nBins):
        from ROOT import TF1, TH1F, TLegend, TPaveText, TLatex, TArrow, TCanvas, kBlue, gStyle
        gStyle.SetOptStat(0000)

        if len(base_fstat) == 0: base_fstat = [0.0]

        ftest_p1    = min(nRpfs1,nRpfs2)
        ftest_p2    = max(nRpfs1,nRpfs2)
        ftest_nbins = nBins
        fdist       = TF1("fDist", "[0]*TMath::FDist(x, [1], [2])", 0,max(10,1.3*base_fstat[0]))
        fdist.SetParameter(0,1)
        fdist.SetParameter(1,ftest_p2-ftest_p1)
        fdist.SetParameter(2,ftest_nbins-ftest_p2)

        pval = fdist.Integral(0.0,base_fstat[0])
        print 'P-value: %s'%pval

        c = TCanvas('c','c',800,600)    
        c.SetLeftMargin(0.12) 
        c.SetBottomMargin(0.12)
        c.SetRightMargin(0.1)
        c.SetTopMargin(0.1)
        ftestHist_nbins = 30
        ftestHist = TH1F("Fhist","",ftestHist_nbins,0,max(10,1.3*base_fstat[0]))
        ftestHist.GetXaxis().SetTitle("F = #frac{-2log(#lambda_{1}/#lambda_{2})/(p_{2}-p_{1})}{-2log#lambda_{2}/(n-p_{2})}")
        ftestHist.GetXaxis().SetTitleSize(0.025)
        ftestHist.GetXaxis().SetTitleOffset(2)
        ftestHist.GetYaxis().SetTitleOffset(0.85)
        
        ftestHist.Draw("pez")
        ftestobs  = TArrow(base_fstat[0],0.25,base_fstat[0],0)
        ftestobs.SetLineColor(kBlue+1)
        ftestobs.SetLineWidth(2)
        fdist.Draw('same')

        ftestobs.Draw()
        tLeg = TLegend(0.6,0.73,0.89,0.89)
        tLeg.SetLineWidth(0)
        tLeg.SetFillStyle(0)
        tLeg.SetTextFont(42)
        tLeg.SetTextSize(0.03)
        tLeg.AddEntry(ftestobs,"observed = %.3f"%base_fstat[0],"l")
        tLeg.AddEntry(fdist,"F-dist, ndf = (%.0f, %.0f) "%(fdist.GetParameter(1),fdist.GetParameter(2)),"l")
        tLeg.Draw("same")

        model_info = TPaveText(0.2,0.6,0.4,0.8,"brNDC")
        model_info.AddText('p1 = '+poly1)
        model_info.AddText('p2 = '+poly2)
        model_info.AddText("p-value = %.2f"%(1-pval))
        model_info.Draw('same')
        
        latex = TLatex()
        latex.SetTextAlign(11)
        latex.SetTextSize(0.06)
        latex.SetTextFont(62)
        latex.SetNDC()
        latex.DrawLatex(0.12,0.91,"CMS")
        latex.SetTextSize(0.05)
        latex.SetTextFont(52)
        latex.DrawLatex(0.65,0.91,"Preliminary")
        latex.SetTextFont(42)
        latex.SetTextFont(52)
        latex.SetTextSize(0.045)
        c.SaveAs(working_area+'/ftest_{0}_vs_{1}_notoys.png'.format(poly1,poly2))

    plot_FTest(base_fstat,nRpfs1,nRpfs2,nBins)

if __name__ == '__main__':
    # Provided for convenience is this function which will package the current CMSSW and store it on the user's EOS (assumes FNAL).
    # This only needs to be run once unless you fundamentally change your working environment.
    #make_env_tarball()

    working_area = 'Zbbfit'
    test_make()

    for order in ["0x0","0x1","1x0","1x1","1x2","2x1","2x2"]:
    for order in ["2x3","3x2"]:
        polyOrder = order
        test_fit()
    

    test_FTest("0x0","0x1")
    test_FTest("0x0","1x0")
    test_FTest("0x1","1x1")
    test_FTest("1x0","1x1")
    test_FTest("1x1","1x2")
    test_FTest("1x1","2x1")
    test_FTest("1x2","2x2")
    test_FTest("2x1","2x2")
    test_FTest("2x2","3x2")
    test_FTest("2x2","2x3")

    polyOrder    = "2x2"
    test_plot()
    test_GoF()
    #test_GoF_plot()