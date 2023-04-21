#!/usr/bin/env

"""

make line datacubes and integrated maps
and compare applying continuum selfcal
  
NOTE: this is intended to be an interactive, iterative process
      so this is more a log that should be run by cutting and
      pasting into casa rather than as an executable script

      search "CHANGEME" for variables to be changed
      
10/9/15 MCA
               
"""



# ================================== Setup =====================================


# LupusIV_150  +16:00:44.52 -41:55:31.1
# Class II, K0


field = 8                                                   # CHANGEME 

fitspw    = '2,3,4'                                         # line-free channels for fitting continuum
linespw   = '0,1,3'                                         # line spectral windows (C18O, 13CO, CN)

robust     = 0.5                                            # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '1.0km/s'
start      = '-3km/s'
nchan      = 16

xc         = 330                               # CHANGEME
yc         = 317                               # CHANGEME
in_a       = 80
out_a      = 120
aper       = 1.25

boxwidth = 300.
box = rg.box([xc-boxwidth,yc-boxwidth],[xc+boxwidth,yc+boxwidth])




# ================ Create continuum subtracted line datasets ===================


uvcontsub(vis       = 'f'+str(field)+'.vis',                # full vis file for this field
          spw       = linespw,                              # line spw (for cont subtraction)
          fitspw    = fitspw,                               # cont spw
          combine   = 'spw',
          solint    = 'int',
          fitorder  = 1,
          want_cont = False)                                # should not be changed.

           
# ============================== 13CO line =====================================


# first try on 13CO line as thats going to be the brightest
# os.system('rm -rf f'+str(field)+'_13co32*')
clean(vis           = 'f'+str(field)+'.vis.contsub',
      imagename     = 'f'+str(field)+'_13co32',
      mode          = 'velocity',
      start         = start,
      width         = width,
      nchan         = nchan,
      outframe      = outframe,
      veltype       = veltype,
      restfreq      = '330.58797GHz',
      niter         = 500,
      mask          = 'f8_cont_mask.crtf',
      threshold     = 0,
      interactive   = False,
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line, so just cleaned in automated mode
  
# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_13co32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])

# export cube to fits file    
fbase = 'f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')

# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'f'+str(field)+'_13co32_b4sc.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_13co32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[0km/s,8km/s]'))
# can't really tell what flux is real, gave high snr

# export to fits file    
fbase = 'f'+str(field)+'_13co32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,fitsimage=fbase+'.fits')

# measure flux
im_rms = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 1345.09 mJy, rms = 76.79 mJy, S/N = 17.5

# continuum and gas
imview(raster=[{'file':'f'+str(field)+'_13co32.mom0'}],
       contour = [{'file':'f'+str(field)+'_cont.fits'}])



# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_13co32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_13co32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_13co32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_13co32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_13co32.mom0_cropped.fits')
'''
Measuring COG for G/f8_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.24 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 72.79 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     49.7     17.0      2.9
   1      0.2    164.6     58.4      2.8
   2      0.3    330.1     74.1      4.5
   3      0.4    494.3     96.5      5.1
   4      0.5    663.7    125.4      5.3
   5      0.6    787.7    119.7      6.6
   6      0.7    860.3    150.7      5.7
   7      0.8    874.2    154.2      5.7 <-- using this (where flux levels off)
   8      0.9    895.2    199.6      4.5
   9      1.0   1004.6    202.8      5.0
  10      1.1   1140.8    178.9      6.4
  11      1.2   1272.9    216.4      5.9

F = 1272.9 mJy
E = 216.4 mJy
S = 5.9
D = 2.4 arcsec
     
'''

# USING 1.6" SINCE WHERE TOTAL FLUX LEVELS OFF FIRST
# AND APERTURE LOOKS BEST IN CASA

#    8    0.800    2233   870.19  176.791     4.9   412.72   73.481     5.6   1.000



# ======================== C18O line  ==========================================

# don't bother with selfcal as it doesn't help...
# os.system('rm -rf f'+str(field)+'_c18o32*')
clean(vis           = 'f'+str(field)+'.vis.contsub',
      imagename     = 'f'+str(field)+'_c18o32',
      mode          = 'velocity',
      start         = start,
      width         = width,
      nchan         = nchan,
      outframe      = outframe,
      veltype       = veltype,
      restfreq      = '329.33055GHz',
      niter         = 500,
      threshold     = 0,
      interactive   = False,
      mask          = 'f8_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line, so just cleaned lightly 
# within continuum region for all channels at once

# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_c18o32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])

# export cube to fits file    
fbase = 'f'+str(field)+'_c18o32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')

# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_c18o32.mom0*')
immoments(imagename  = 'f'+str(field)+'_c18o32.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_c18o32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[0km/s,8km/s]'))
# can't see line so will use same velocity range as 13co32

# export to fits file    
fbase = 'f'+str(field)+'_c18o32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,fitsimage=fbase+'.fits')

# measure flux
im_rms = imstat(imagename = 'f'+str(field)+'_c18o32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_c18o32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 131.01 mJy, rms = 89.97 mJy, S/N = 1.5


# view continuum and gas
imview(raster=[{'file':'f'+str(field)+'_c18o32.mom0'}],
       contour = [{'file':'f'+str(field)+'_cont.fits'}])



# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_c18o32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_c18o32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_c18o32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_c18o32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_c18o32.mom0_cropped.fits')
'''
Measuring COG for G/f8_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.86 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 89.49 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     21.8     22.0      1.0
   1      0.2     86.6     57.5      1.5
   2      0.3    221.1     83.9      2.6 <-- ND
   3      0.4    374.7    114.5      3.3
   4      0.5    485.9    141.0      3.4
   5      0.6    562.0    193.7      2.9
   6      0.7    658.5    214.1      3.1
   7      0.8    692.0    253.0      2.7
   8      0.9    606.5    267.7      2.3
   9      1.0    448.1    272.2      1.6
  10      1.1    309.5    290.6      1.1
  11      1.2    190.7    258.2      0.7

F = 692.0 mJy
E = 253.0 mJy
S = 2.7
D = 1.6 arcsec

'''





# ======================== Image CN  ==================

# don't bother with selfcal as it doesn't help...
# os.system('rm -rf f'+str(field)+'_cn32_b4sc*')
clean(vis           = 'f'+str(field)+'.vis.contsub',
      imagename     = 'f'+str(field)+'_cn32_b4sc',
      mode          = 'velocity',
      start         = start,
      width         = width,
      nchan         = nchan,
      outframe      = outframe,
      veltype       = veltype,
      restfreq      = '340.24777GHz',
      niter         = 2000,
      threshold     = 0,
      interactive   = True,
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line, so just cleaned lightly 
# within continuum region for all channels at once


# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_cn32_b4sc.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])


# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_cn32.mom0*')
immoments(imagename  = 'f'+str(field)+'_cn32_b4sc.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_cn32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[1km/s,8km/s]'))
# can see emission

# export to fits file    
fbase = 'f'+str(field)+'_cn32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,fitsimage=fbase+'.fits')

# measure flux
im_rms = imstat(imagename = 'f'+str(field)+'_cn32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_cn32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 2147.85 mJy, rms = 50.52 mJy, S/N = 42.5


# view continuum and gas
imview(raster=[{'file':'f'+str(field)+'_cn32.mom0'}],
       contour = [{'file':'f'+str(field)+'_cont.fits'}])



# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_cn32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_cn32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_cn32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_cn32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_cn32.mom0_cropped.fits')
'''
Measuring COG for G/f8_cn32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.23 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 51.77 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     40.5     12.1      3.3
   1      0.2    162.7     31.9      5.1
   2      0.3    403.9     52.3      7.7
   3      0.4    719.2     79.3      9.1
   4      0.5   1077.2    108.5      9.9
   5      0.6   1389.2    101.7     13.7
   6      0.7   1679.2    120.9     13.9
   7      0.8   1931.7    144.7     13.3
   8      0.9   2072.9    145.2     14.3  <-- using this (where flux levels off)
   9      1.0   2080.5    180.7     11.5
  10      1.1   2051.5    158.6     12.9
  11      1.2   2094.3    190.1     11.0

F = 2094.3 mJy
E = 190.1 mJy
S = 11.0
D = 2.4 arcsec

'''

