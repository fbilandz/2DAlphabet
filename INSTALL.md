export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_6_14
cd CMSSW_10_6_14/src
cmsenv
git clone https://github.com/lcorcodilos/2DAlphabet.git
git clone https://github.com/lcorcodilos/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit/
curl -s https://raw.githubusercontent.com/lcorcodilos/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh | bash
scram b clean; scram b -j 10
cmsenv
git remote add matejFork git@github.com:mroguljic/2DAlphabet.git
git pull matejFork Zbb_v9
git checkout Zbb_v9
cp TwoDAlphabet/ext/TagAndProbeExtended.py $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/python/
cd ..
scram b -j4