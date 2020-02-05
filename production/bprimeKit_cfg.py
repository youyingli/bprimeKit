import importlib  # Python2.7 libaries
import FWCore.ParameterSet.Config            as cms
import FWCore.ParameterSet.VarParsing        as opts

#-------------------------------------------------------------------------------
#   Options settings + Parsing, see python/optionsInit and python/OptionParser
#-------------------------------------------------------------------------------
options = opts.VarParsing ('analysis')

options.register('sample',
    '',
    opts.VarParsing.multiplicity.list,
    opts.VarParsing.varType.string,
    'Sample to analyze')

options.register('outputLabel',
    'bpk_ntuple.root',
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.string,
    'Output label')

options.register('DataProcessing',
    '',
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.string,
    'Data processing types. Options are file found in python/bprimeKit_*.py')

options.register('Debug',
    0,
    opts.VarParsing.multiplicity.singleton,
    opts.VarParsing.varType.int,
    'Debugging output level' )

options.setDefault('maxEvents', 10000 )

options.parseArguments()

mysetting = importlib.import_module('bpkFrameWork.bprimeKit.bprimeKit_' + options.DataProcessing )

print '\nRunning with DataProcessing option [', options.DataProcessing, '] and with global tag [', mysetting.GlobalTag, ']\n'

#-------------------------------------------------------------------------------
#   Process Setup
#-------------------------------------------------------------------------------
process = cms.Process('bprimeKit')

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(options.sample)
    )
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.categories.append('HLTrigReport')
process.MessageLogger.cerr.FwkReport.reportEvery = 100
if( options.Debug ):
    process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag.globaltag = mysetting.GlobalTag

print '\nFinished basic setups...\n'

#-------------------------------------------------------------------------------
#   Reprocessing Jets
#     For settings, see the bprimeKit/python/jettoolbox_settings.py
#-------------------------------------------------------------------------------
print '\nBeginning jet toolbox setup.....\n'
from bpkFrameWork.bprimeKit.jettoolbox_settings import *
jettoolbox_settings( process, not mysetting.isData )
print '\nFinished jet toolbox setup.....\n'

#-------------------------------------------------------------------------------
#   Settings for Egamma Identification and Energy Correction bug fixing
#-------------------------------------------------------------------------------
# ref : https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2#2017_MiniAOD_V2
### tmp 2018 only
from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
setupEgammaPostRecoSeq(
    process,
    runEnergyCorrections = False,
    era = '2018-Prompt'
    )

process.externalCorrectionSequence = cms.Sequence()
#-------------------------------------------------------------------------------
#   Settings for MET bug fixing
#-------------------------------------------------------------------------------
# ref : https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETUncertaintyPrescription#Instructions_for_9_4_X_X_9_or_10
from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

if mysetting.Year == '2017':
    runMetCorAndUncFromMiniAOD (
        process,
        isData = mysetting.isData,
        fixEE2017 = True,
        fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold': 3.139},
        postfix = "ModifiedMET"
        )
    process.externalCorrectionSequence *= process.fullPatMetSequenceModifiedMET

#-------------------------------------------------------------------------------
#   Level 1 ECAL prefiring
#-------------------------------------------------------------------------------
# ref : https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1ECALPrefiringWeightRecipe
from PhysicsTools.PatUtils.l1ECALPrefiringWeightProducer_cfi import l1ECALPrefiringWeightProducer

if mysetting.Year != '2018' and not mysetting.isData:
    process.prefiringweight = l1ECALPrefiringWeightProducer.clone(
        DataEra = cms.string('2017BtoF' if mysetting.Year == '2017' else '2016BtoH'),
        UseJetEMPt = cms.bool(False),
        PrefiringRateSystematicUncty = cms.double(0.2),
        SkipWarnings = False
        )
    process.externalCorrectionSequence *= process.prefiringweight

#-------------------------------------------------------------------------------
#   bprimeKit configuration importing
#-------------------------------------------------------------------------------
process.TFileService = cms.Service('TFileService',
    fileName = cms.string( options.outputLabel )
    )

# See the file python/bprimeKit_* default settings for the various DataProcessings
process.bprimeKit = mysetting.bprimeKit

#-------------------------------------------------------------------------------
#   Final output settings
#-------------------------------------------------------------------------------
# process.SimpleMemoryCheck = cms.Service('SimpleMemoryCheck',ignoreTotal = cms.untracked.int32(1) )

process.Path = cms.Path(
    process.egammaPostRecoSeq*
    process.externalCorrectionSequence*
    process.JetToolBoxSequence*
    process.bprimeKit
    )
