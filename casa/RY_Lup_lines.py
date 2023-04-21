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


# LupusIII_1015 15:59:28.39 -40:21:51.30
# Class II, K4

field = 14                                                  # CHANGEME 

fitspw    = '2,3:0~2049;2151~2899;3051~3480,4'              # line-free channels for fitting continuum
fitspw    = '2,3,4'                                         # line-free channels for fitting continuum
linespw   = '0,1,3'                                         # line spectral windows (C18O, 13CO, CN)

robust     = 0.5                                            # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '1.0km/s'
start      = '-3.0km/s'
nchan      = 15

xc         = 327                                            # CHANGEME
yc         = 311                                            # CHANGEME
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
# os.system('rm -rf test_f'+str(field)+'_13co32*')
clean(vis           = 'f'+str(field)+'.vis.contsub',
      imagename     = 'test_f'+str(field)+'_13co32',
      mode          = 'velocity',
      start         = start,
      width         = width,
      nchan         = nchan,
      outframe      = outframe,
      veltype       = veltype,
      restfreq      = '330.58797GHz',
      niter         = 2000,
      threshold     = 0,
      interactive   = True,
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)


# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'test_f'+str(field)+'_13co32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])

# export cube to fits file    
fbase = 'test_f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')


# os.system('rm -rf f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'test_f'+str(field)+'_13co32.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'test_f'+str(field)+'_13co32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[0km/s,9km/s]'))                      # CHANGEME (based on above analysis!!)
fbase = 'test_f'+str(field)+'_13co32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,
           fitsimage=fbase+'.fits')


# first moment map
sigma = 30e-3  # Jy/beam in peak velocity channel
os.system('rm -rf test_f14_13co32.mom1.image')
immoments(imagename  = 'test_f14_13co32.cube.fits',
          outfile    = 'test_f14_13co32.mom1.image',
          moments    = [1],
          includepix = [3.0*sigma,100.0],
          chans      = ('range=[-1km/s,9km/s]'))
os.system('rm -rf test_f14_13co32.mom1.fits')
exportfits(imagename='test_f14_13co32.mom1.image',fitsimage='test_f14_13co32.mom1.fits')
os.system('rm -rf f14_13co32.mom1.image')


# crop first-moment map
ia.fromimage(outfile = 'test_0.5_f14_13co32.mom1.crop.image',
             infile  = 'test_0.5_f14_13co32.mom1.fits',
             region  = rg.box([320-50,320-50],[320+50,320+50]) )
ia.close() 
exportfits(imagename = 'test_0.5_f14_13co32.mom1.crop.image',
           fitsimage = 'test_0.5_f14_13co32.mom1.crop.fits')



# measure flux
im_max = imstat(imagename = 'f'+str(field)+'_13co32.mom0')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 4595.72 mJy, rms = 72.09 mJy, S/N = 63.7

# view continuum and gas
imview(raster=[{'file':'f'+str(field)+'_13co32.mom0'}],
       contour = [{'file':'f'+str(field)+'_cont.fits'}])


# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_13co32.mom0_cropped.image*')
ia.fromimage(outfile = 'f'+str(field)+'_13co32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_13co32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_13co32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_13co32.mom0_cropped.fits')


'''
Measuring COG for G/f14_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.92 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 73.48 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10   252.33    15.84     15.9
   1     0.20   808.95    54.34     14.9
   2     0.30  1531.45    64.75     23.7
   3     0.40  2194.40    94.71     23.2
   4     0.50  2795.33   137.81     20.3
   5     0.60  3239.24   141.22     22.9
   6     0.70  3593.30   175.71     20.4
   7     0.80  3915.20   223.61     17.5
   8     0.90  4238.46   208.20     20.4
   9     1.00  4510.30   239.20     18.9
  10     1.10  4624.38   224.93     20.6
  11     1.20  4618.95   271.20     17.0
  12     1.30  4570.59   225.59     20.3
  13     1.40  4542.64   287.87     15.8

F = 4624.38 mJy
E = 224.93 mJy
S = 20.6
D = 2.2 arcsec
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
      mask          = 'f14_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line clearly, so just cleaned lightly 
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
          chans      = ('range=[0km/s,9km/s]'))                      # CHANGEME (based on above analysis!!)
# can't see line clearly so will use same velocity range as 13co32

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
# Flux = 1653.70 mJy, rms = 80.42 mJy, S/N = 20.6

# view continuum and gas
imview(raster=[{'file':'f'+str(field)+'_c18o32.mom0'}],
       contour = [{'file':'f'+str(field)+'_cont.fits'}])


# re-center image on source and use measure.py to get COG flux
ia.fromimage(outfile = 'f'+str(field)+'_c18o32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_c18o32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_c18o32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_c18o32.mom0_cropped.fits')
'''
Measuring COG for G/f14_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.29 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 84.60 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10   119.19    23.60      5.0
   1     0.20   398.07    58.66      6.8
   2     0.30   761.19    61.50     12.4
   3     0.40  1030.14   107.08      9.6
   4     0.50  1148.87   126.38      9.1
   5     0.60  1143.10   146.67      7.8 <-- using this
   6     0.70  1111.09   196.92      5.6
   7     0.80  1121.06   236.92      4.7
   8     0.90  1177.00   265.96      4.4
   9     1.00  1268.24   240.62      5.3

F = 1268.24 mJy
E = 240.62 mJy
S = 5.27
D = 2.00 arcsec

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
      mask          = 'f14_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line clearly, so just cleaned lightly 
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
          chans      = ('range=[-1km/s,7km/s]'))                        # CHANGEME (based on above analysis!!)

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
# Flux = 1817.61 mJy, rms = 49.99 mJy, S/N = 36.4


# view continuum and gas
imview(raster=[{'file':'f'+str(field)+'_cn32.mom0'}],
       contour = [{'file':'f'+str(field)+'_cont.fits'}])


# re-center image on source and use measure.py to get COG flux
ia.fromimage(outfile = 'f'+str(field)+'_cn32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_cn32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_cn32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_cn32.mom0_cropped.fits')
'''
Measuring COG for G/f14_cn32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.61 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 51.44 mJy/beam km/s

   i   radius    flux      err
       (asec)    (mJy)     (mJy)
   0      0.1     97.9     11.8
   1      0.2    308.9     29.8
   2      0.3    590.2     56.0
   3      0.4    869.4     74.7
   4      0.5   1139.6     89.3
   5      0.6   1323.6    127.0
   6      0.7   1433.4    107.8
   7      0.8   1489.2    126.0
   8      0.9   1529.6    160.0
   9      1.0   1621.3    191.5
  10      1.1   1752.1    170.4
  11      1.2   1825.8    174.6
  12      1.3   1764.6    221.1
  13      1.4   1650.3    222.4
  14      1.5   1592.1    250.0
  15      1.6   1653.1    230.8
  16      1.7   1767.0    249.3
  17      1.8   1815.0    300.4
  18      1.9   1775.2    313.4
  19      2.0   1707.9    272.4

F = 1825.8 mJy
E = 174.6 mJy
S = 10.5 mJy
D = 2.4 arcsec
'''
