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



# III_67 M4.0 II
# 16:08:51.58 -39:03:17.6

field = 33                                     # CHANGEME 

fitspw    = '2,3,4,7,8,9'                      # line-free channels for fitting continuum
linespw   = '0,1,3,5,6,8'                      # line spectral windows (C18O, 13CO, CN)

robust     = 0.5                               # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '1.0km/s'
start      = '-3km/s'
nchan      = 16

xc         = 324                               # CHANGEME
yc         = 309                               # CHANGEME
in_a       = 80
out_a      = 120
aper       = 0.5

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
# os.system('rm -rf f'+str(field)+'_13co32_b4sc*')
clean(vis           = 'f'+str(field)+'.vis.contsub',
      imagename     = 'f'+str(field)+'_13co32_b4sc',
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
      mask          = 'f33_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# used continuum region in automated mode
# can't see emission

# export cube to fits file    
fbase = 'f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')

# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_13co32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])
# cannot see emission

# export cube to fits file    
fbase = 'f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')

# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'f'+str(field)+'_13co32.image',              # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_13co32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[2km/s,6km/s]'))                      # CHANGEME (based on above analysis!!)

# export to fits file    
fbase = 'f'+str(field)+'_13co32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,fitsimage=fbase+'.fits')

# measure flux
im_max = imstat(imagename = 'f'+str(field)+'_13co32.mom0')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 41.06 mJy, rms = 30.07 mJy, S/N = 1.4


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
Measuring COG for M/f33_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.28 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 29.83 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10     9.24     9.42      1.0
   1     0.20    22.18    21.32      1.0
   2     0.30    32.46    28.18      1.2 <-- ND
   3     0.40    42.74    42.56      1.0
   4     0.50    41.06    62.07      0.7
   5     0.60    39.00    73.63      0.5
   6     0.70    55.83    91.85      0.6
   7     0.80    84.27    74.95      1.1

F = 84.27 mJy
E = 74.95 mJy
S = 1.12
D = 1.60 arcsec

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
      mask          = 'f33_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# couldn't see line, just cleaned in automated mode
# in continuum region for all channels

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
# Flux = 48.22 mJy, rms = 36.04 mJy, S/N = 1.3

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
Measuring COG for M/f33_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.50 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 35.38 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10     4.22     8.75      0.5
   1     0.20    13.92    21.98      0.6
   2     0.30    33.68    39.05      0.9 <-- ND
   3     0.40    50.25    53.05      0.9
   4     0.50    48.22    68.84      0.7
   5     0.60    36.99    73.77      0.5
   6     0.70    13.00   100.72      0.1
   7     0.80   -66.02   122.02     -0.5

F = 50.25 mJy
E = 53.05 mJy
S = 0.95
D = 0.80 arcsec
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
      mask          = 'f33_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# couldn't see line, just cleaned in automated mode
# in continuum region for all channels

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
          chans      = ('range=[1km/s,7km/s]'))                      # CHANGEME (based on above analysis!!)
# can't see emission

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
# Flux = -11.59 mJy, rms = 29.30 mJy, S/N = -0.4


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


# COULD NOT SEE GAS, SO USED 1" APER TO MEASURE FLUX
#    5    0.500     877   -13.35   72.422    -0.2    73.85   29.823     2.5   0.999
