#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/lcorcodi/10XwithNano.tgz ./
export SCRAM_ARCH=slc7_amd64_gcc700
scramv1 project CMSSW CMSSW_10_6_14
tar -xzf 10XwithNano.tgz
rm 10XwithNano.tgz

mkdir tardir; cp tarball.tgz tardir/; cd tardir
tar -vxzf tarball.tgz
cp -r * ../CMSSW_10_6_14/src/2DAlphabet/
cd ../CMSSW_10_6_14/src/2DAlphabet/
ls -trlh
`eval scramv1 runtime -sh`
scramv1 b clean; scramv1 b
