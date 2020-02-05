#!/bin/bash

echo
echo "Welcome to the bprimekit setup script!"
echo

echo "set up fixing codes for the electron energy scale and smearing interacts with the ECAL-tracker combination"
git cms-merge-topic cms-egamma:EgammaPostRecoTools
echo

echo "Set up JetToolBox"
git clone https://github.com/cms-jet/JetToolbox.git JMEAnalysis/JetToolbox -b jetToolbox_102X_v1
echo

echo "Set up MET bug fixing code"
git cms-merge-topic cms-met:METFixEE2017_949_v2_backport_to_102X
echo

echo "Done with setup script! You still need to build!"
echo
