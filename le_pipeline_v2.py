#!/usr/bin/env python
##################################
#Notice: The Pipeline applies to LE data with HXMTSoftware(V1) 
#################################


import argparse
import os
import commands
import glob
import pyfits as pf
import numpy as np
import matplotlib.pyplot as plt

# find and create data dir list
parser = argparse.ArgumentParser()
parser.add_argument("-i","--input",help="data archived path")
parser.add_argument("-I","--inputlist",help="data archived path in list",type=str)
parser.add_argument("-o","--output",help="products archived path")
parser.add_argument("-O","--outputlist",help="products archived path in list",type=str)
parser.add_argument("--rangefile",action="store_true",help="rangefile path of hegtigen is $hxmtanalysis")
parser.add_argument("--detlist",action="store",help="detector list")
parser.add_argument("--bigfovdet",action="store_true",help="select big fov detectors of three boxes")
parser.add_argument("--midfovdet",action="store_true",help="select mid fov detectors of three boxes")
parser.add_argument("--smfovdet",action="store_true",help="select small fov detectors of three boxes")
parser.add_argument("--blinddet",action="store_true",help="select all blind detectors")
parser.add_argument("--hxbary",action="store_true",help="carry out hxbary and copy Evt file to local directory")
parser.add_argument("-r","--ra",help="right ascension of barycentering correction",type=float)
parser.add_argument("-d","--dec",help="declination of barycentering correction",type=float)
args = parser.parse_args()

def main():
    aux_dir = product_dir + "/AUX/" # AUX path
    acs_dir = product_dir + "/ACS/" # ACS path
    le_dir = product_dir + "/LE/"   # HE  path
    
    
    #make direction for data structure
    if not os.path.isdir(product_dir):os.system('mkdir -p '+product_dir)
    if not os.path.isdir(aux_dir):os.system('mkdir -p ' +aux_dir)
    if not os.path.isdir(acs_dir):os.system('mkdir -p ' +acs_dir)
    if not os.path.isdir(le_dir):os.system('mkdir -p '+le_dir)
    
    #read filenames
    filename = sorted(glob.glob(data_dir + '/LE/*LE-Evt_FFFFFF_V[1-9]*'))[-1]
    instatusfilename = sorted(glob.glob(data_dir + '/LE/*LE-InsStat_FFFFFF_V[1-9]*'))[-1]
    orbitname = sorted(glob.glob(data_dir + '/ACS/*_Orbit_*V[1-9]*'))[-1]
    preciseorbitname = orbitname
    attname = sorted(glob.glob(data_dir + '/ACS/*_Att_*V[1-9]*'))[-1]
    tempfilename = sorted(glob.glob(data_dir + '/LE/HXMT*TH*V[1-9]*'))[-1]
    gainfilename = commands.getstatusoutput('ls $CALDB/data/hxmt/le/bcf/*gain*')[1]
    ehkfilename = sorted(glob.glob(data_dir + '/AUX/*EHK*'))[-1]
    
    # select good time intervals utilizing HXMT software
    ## pi calculation
    lepical_text = 'lepical evtfile='+filename+' tempfile='+tempfilename+' outfile='+le_dir+'le_pi.fits gainfile='+gainfilename+\
            ' clobber=yes history=yes'
    print lepical_text
    os.system(lepical_text)
    
    ## le reconstruction
    lerecon_text = 'lerecon evtfile='+le_dir+'le_pi.fits outfile='+le_dir+'le_recon.fits instatusfile='+instatusfilename+' clobber=yes history=yes'
    print lerecon_text
    os.system(lerecon_text)
    
    ## gti selection
    legtigen_text = 'legtigen evtfile='+filename+' instatusfile='+instatusfilename+' tempfile='+tempfilename+' ehkfile='+ehkfilename+\
            ' outfile='+le_dir+'le_gti.fits defaultexpr=NONE rangefile=$HEADAS/refdata/lerangefile.fits'+\
            ' expr="ELV>10&&DYE_ELV>40&&COR>8&&T_SAA>=100&&TN_SAA>=100"'+\
            ' clobber=yes history=yes'
    print legtigen_text
    os.system(legtigen_text) 
    
    ## detector selection
    det = ''
    if args.bigfovdet:
        print 'function not available'
    if args.midfovdet:
        print 'function not available'
    if args.smfovdet:
        det = det + '0,2-4,6-10,12,14,20,22-26,28-30;'+\
                '32,34-36,38-42,44,46,52,54-58,60-62;'+\
                '64,66-68,70-74,76,78,84,86-90,92-94;'
    if args.blinddet:
        det = det + '13,45,77'
    if args.detlist:
        det = det + args.detlist;
    print 'detector_list:',det
    
    ## select good event data
    lescreen_text = 'lescreen evtfile='+le_dir+'le_recon.fits gtifile='+le_dir+'le_gti.fits outfile='+le_dir+'le_screen.fits userdetid="'+det+'"'+\
            ' baddetfile=$HEADAS/refdata/ledetectorstatus.fits eventtype=1 starttime=0 stoptime=0 minPI=0 maxPI=1536'+\
            ' clobber=yes history=yes'
    print lescreen_text
    os.system(lescreen_text)
    
    ## carry out barycentering correction
    if args.hxbary:
        # carry out hxbary
        ra = args.ra
        dec = args.dec
        hxbary_text = 'hxbary' + ' ' + le_dir + 'le_screen.fits' + ' ' + preciseorbitname + ' ' + str(ra) + ' ' + str(dec) + ' ' + '2'
        print hxbary_text
        os.system(hxbary_text)


if args.inputlist:
    inputfile = open(args.inputlist)
    outputfile= open(args.outputlist)
    for data_dir,product_dir in zip(inputfile,outputfile):
        data_dir = data_dir[0:-1]
        product_dir = product_dir[0:-1]
        try:
            main()
        except:
            continue
else:
    data_dir = args.input
    product_dir = args.output
    main()
