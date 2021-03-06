#*******************************************************************************
 #
 #  Filename    : bprimeKit_MC_76X.py
 #  Description : Default settings for 76X
 #  Author      : Yi-Mu 'Enoch' Chen [ ensc@hep1.phys.ntu.edu.tw ]
 #
 #  Ditching original cfg framework 2016-03
 #
#*******************************************************************************
import FWCore.ParameterSet.Config        as cms
import bpkFrameWork.bprimeKit.Ntuplizer18_cfi as ntpl

#-------------------------------------------------------------------------------
#   Additional tag settings
#-------------------------------------------------------------------------------
Year                 = '2018'
isData               = True
GlobalTag            = '106X_dataRun2_v32'

#-------------------------------------------------------------------------------
#   BprimeKit input tags
#-------------------------------------------------------------------------------
bprimeKit = cms.EDAnalyzer(
    'bprimeKit',

    lherunsrc=cms.InputTag('externalLHEProducer'),

    evtgensetting  = ntpl.evtgenbase,
    vtxsetting     = ntpl.vertexbase,
    triggersetting = ntpl.triggerbase,

    #----- Photon information -----------------------------------------------
    photonsettings = cms.VPSet(
        ntpl.photonbase
    ),

    #----- Lepton related information ---------------------------------------
    leptonsettings=cms.VPSet(
        ntpl.leptonbase
    ),

    #----- Jet Information --------------------------------------------------
    jetsettings=cms.VPSet(
        ntpl.ak4jetbase,
        ntpl.ak4jetpuppi,
        ntpl.ak8jetpuppi,
        ntpl.ca8jetpuppi
    )
)
