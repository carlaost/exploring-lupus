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



# LupusIII_30   16:07:54.74 -39:15:44.6

field = 29                                     # CHANGEME 

fitspw    = '2,3,4'                            # line-free channels for fitting continuum
linespw   = '0,1,3'                            # line spectral windows (C18O, 13CO, CN)

robust     = 0.5                               # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '1.0km/s'
start      = '-3km/s'
nchan      = 16

xc         = 315                               # CHANGEME
yc         = 315                               # CHANGEME
in_a       = 80
out_a      = 120
aper       = 0.5                               # CHANGEME

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
      threshold     = 0,
      interactive   = False,
      mask          = 'f29_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line, so just cleaned in automated mode


# export cube to fits file    
fbase = 'f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')
  
# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_13co32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])

# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'f'+str(field)+'_13co32_b4sc.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_13co32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[2km/s,6km/s]'))
# cannot see emission but gives max snr

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
# Flux = 29.18 mJy, rms = 47.61 mJy, S/N = 0.6

# view continuum and gas
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
Measuring COG for G/f29_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.62 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 48.63 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10     7.09    11.03      0.6
   1     0.20    26.90    28.54      0.9
   2     0.30    37.34    50.54      0.7 <-- ND
   3     0.40    25.20    65.96      0.4
   4     0.50    29.18    73.16      0.4
   5     0.60    73.46    80.36      0.9
   6     0.70    98.90    93.59      1.1
   7     0.80    84.44   119.11      0.7
   8     0.90    76.15   119.61      0.6
'''


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
      mask          = 'f29_cont_mask.crtf',
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


# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_c18o32.mom0*')
immoments(imagename  = 'f'+str(field)+'_c18o32.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_c18o32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[2km/s,6km/s]'))

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
# Flux = -19.24 mJy, rms = 54.37 mJy, S/N = -0.4


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
Measuring COG for G/f29_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.02 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 57.68 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10    15.42    16.74      0.9
   1     0.20    42.45    34.64      1.2
   2     0.30    39.97    47.05      0.8 <-- ND
   3     0.40     3.22    67.98      0.0
   4     0.50   -19.24    89.80     -0.2
   5     0.60    -7.57    93.91     -0.1
   6     0.70    17.85   131.57      0.1
   7     0.80    29.19   125.71      0.2

F = 42.45 mJy
E = 34.64 mJy
S = 1.23
D = 0.40 arcsec

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
      niter         = 500,
      threshold     = 0,
      interactive   = False,
      mask          = 'f29_cont_mask.crtf',
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
          chans      = ('range=[2km/s,8km/s]'))
# cannot see emission clearly


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
# Flux = 198.73 mJy, rms = 43.30 mJy, S/N = 4.6


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
Measuring COG for G/f29_cn32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.12 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 42.67 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     29.6      8.6      3.4
   1      0.2     93.0     25.4      3.7
   2      0.3    158.8     48.6      3.3
   3      0.4    193.0     70.5      2.7
   4      0.5    198.7     83.8      2.4
   5      0.6    172.9     83.8      2.1
   6      0.7    122.0    115.8      1.1
   7      0.8     83.9    127.0      0.7
   8      0.9     64.1    140.4      0.5
   9      1.0     69.1    150.5      0.5

F = 198.7 mJy
E = 83.8 mJy
S = 2.4
D = 1.0 arcsec

'''

