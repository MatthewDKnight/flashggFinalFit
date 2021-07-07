print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG BACKGROUND FITTER ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
import ROOT
import pandas as pd
import pickle
import math
import os, sys
import json
from optparse import OptionParser
import glob
import re
from collections import OrderedDict as od

from commonTools import *
from commonObjects import *
from backgroundFunctions import *
from modelBuilder_v2 import *
from plottingTools import *

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG BACKGROUND FITTER (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  exit()

def get_options():
  parser = OptionParser()
  parser.add_option("--xvar", dest='xvar', default='CMS_hgg_mass', help="Observable to fit")
  parser.add_option("--inputWSFile", dest='inputWSFile', default='', help="Input flashgg WS file: usually path to allData.root")
  parser.add_option("--ext", dest='ext', default='', help="Extension")
  parser.add_option("--cat", dest='cat', default='', help="RECO category")
  parser.add_option("--year", dest='year', default='2016', help="Year. Use 'merged' for year-merged cat")
  parser.add_option("--blindingRegion", dest='blindingRegion', default='115,135', help="Only fit function outside this region (unless running with --fitFullRange)")
  parser.add_option("--fitFullRange", dest='fitFullRange', default=False, action="store_true", help="Fit background pdfs over full range, including the blinding region")
  parser.add_option("--maxOrder", dest='maxOrder', default=6, type='int', help="Max order of functions")
  parser.add_option("--pvalFTest", dest='pvalFTest', default=0.05, type='float', help="p-value threshold to include higher order function in envelope")
  parser.add_option("--gofCriteria", dest='gofCriteria', default=0.01, type='float', help="goodness-of-fit threshold to include function in envelope")
  parser.add_option('--doPlots', dest='doPlots', default=False, action="store_true", help="Produce bkg fitting plots")
  parser.add_option('--nBins', dest='nBins', default=80, type='int', help="Number of bins for fit")
  # Minimizer options
  parser.add_option('--minimizerMethod', dest='minimizerMethod', default='TNC', help="(Scipy) Minimizer method")
  parser.add_option('--minimizerTolerance', dest='minimizerTolerance', default=1e-8, type='float', help="(Scipy) Minimizer tolerance")
  return parser.parse_args()
(opt,args) = get_options()

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETUP: background fTest
print " --> Running bkg fTest for %s"%opt.cat
f = ROOT.TFile(opt.inputWSFile,"read")
inputWS = f.Get(inputWSName__)
xvar = inputWS.var(opt.xvar)
xvarFit = xvar.Clone()

data = inputWS.data("Data_%s_%s"%(sqrts__,opt.cat))

if( data.numEntries == 0 )|( data.sumEntries() <= 0. ):
  print " --> [ERROR] Attempting to running bkg modelling for category (%s) with zero/negative events"%opt.cat
  sys.exit(1)

# Extract blinding region in list
blindingRegion = [float(opt.blindingRegion.split(",")[0]),float(opt.blindingRegion.split(",")[1])]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTRUCT MODEL
model = modelBuilder("model_%s_%s"%(opt.cat,opt.year),opt.cat,xvarFit,data,functionFamilies,opt.nBins,blindingRegion,opt.minimizerMethod)
if opt.fitFullRange: model.setBlind(False)

model.fTest()
model.goodnessOfFit()

plotPdfMap(model,model.pdfs,_outdir="/eos/home-j/jlangfor/www/CMS/postdoc/finalfits/Jul21/Background",_cat=opt.cat)

#pdf3_chi2 = model.buildPdf("Exponential",3,ext="_chi2")
#model.runFit(pdf3_chi2,_verbose=True,_mode="chi2")
#pdf5 = model.buildPdf("Exponential",5)
#model.runFit_v2(pdf5,_verbose=True)


#pdf3_nll = model.buildPdf("Exponential",3,ext="_nll")
#model.runFit(pdf3_nll,_verbose=True,_mode='NLL')

#pdfMap = od()
#pdfMap["exp3_chi2"] = od()
#pdfMap["exp3_chi2"]['pdf'] = pdf3_chi2
#pdfMap["exp3_chi2"]['norm'] = model.getNorm(pdf3_chi2)
#pdfMap["exp3_nll"] = od()
#pdfMap["exp3_nll"]['pdf'] = pdf3_nll
#pdfMap["exp3_nll"]['norm'] = model.getNorm(pdf3_nll)

#plotPdfMap(model,pdfMap,_outdir="/eos/home-j/jlangfor/www/CMS/postdoc/finalfits/Jul21/Background",_cat=opt.cat)



sys.exit(1)

# Do fTest
model.fTest( _maxOrder = opt.maxOrder, _pvalFTest = opt.pvalFTest )

# Apply goodness of fit critera: functions passing enter envelope
model.goodnessOfFit( _gofCriteria = opt.gofCriteria )

# Build envelope, find best-fit function and calculate normalisation
if opt.year == "merged": model.buildEnvelope(_extension="_%s"%sqrts__)
else: model.buildEnvelope(_extension="_%s_%s"%(opt.year,sqrts__))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TODO: SAVE RESULTS TO FILE: see resFile in fTest.cpp

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE: to output workspace
foutDir = "%s/outdir_%s/fTest/output"%(bwd__,opt.ext)
foutName = "%s/outdir_%s/fTest/output/CMS-HGG_multipdf_%s.root"%(bwd__,opt.ext,opt.cat)
print "\n --> Saving output multipdf to file: %s"%foutName
if not os.path.isdir(foutDir): os.system("mkdir %s"%foutDir)
fout = ROOT.TFile(foutName,"RECREATE")
outWS = ROOT.RooWorkspace(bkgWSName__,bkgWSName__)
#fm.save(outWS)
#outWS.Write()
#fout.Close()


