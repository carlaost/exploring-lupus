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




# IV_145 K7.0 II
# 16:00:02.38 -42:22:15.6

field = 27                                     # CHANGEME 

fitspw    = '2,3,4,7,8,9'                      # line-free channels for fitting continuum
linespw   = '0,1,3,5,6,8'                      # line spectral windows (C18O, 13CO, CN)

robust     = 0.5                               # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '1.0km/s'
start      = '-1km/s'
nchan      = 11

xc         = 331                               # CHANGEME
yc         = 337                               # CHANGEME
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


# export cube to fits file    
fbase = 'test_f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')


# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'test_f'+str(field)+'_13co32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])


# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf test_f'+str(field)+'_13co32_mom0*')
immoments(imagename  = 'test_f'+str(field)+'_13co32.image',              # CHANGEME (based on above analysis!!)
          outfile    = 'test_f'+str(field)+'_13co32_mom0.image',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[2km/s,6km/s]'))                      # CHANGEME (based on above analysis!!)
fbase = 'test_f'+str(field)+'_13co32_mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.fits')

#### FIRST MOMENT MAP
sigma = 14e-3  # Jy/beam in peak velocity channel
os.system('rm -rf test_f27_13co32_mom1.image')
immoments(imagename  = 'test_f27_13co32.cube.fits',
          outfile    = 'test_f27_13co32_mom1.image',
          moments    = [1],
          includepix = [3.0*sigma,100.0],
          chans      = ('range=[2km/s,6km/s]'))
os.system('rm -rf test_f27_13co32_mom1.fits')
exportfits(imagename='test_f27_13co32_mom1.image',fitsimage='test_f27_13co32_mom1.fits')
os.system('rm -rf f27_13co32_mom1.image')



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
# Flux = 1838.36 mJy, rms = 32.14 mJy, S/N = 57.2

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
Measuring COG for M/f27_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.92 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 32.79 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10    68.66     8.47      8.1
   1     0.20   229.58    24.34      9.4
   2     0.30   462.08    35.94     12.9
   3     0.40   698.59    47.70     14.6
   4     0.50   943.94    56.09     16.8
   5     0.60  1166.67    78.93     14.8
   6     0.70  1393.08    62.69     22.2
   7     0.80  1584.87    76.78     20.6
   8     0.90  1735.30    90.11     19.3
   9     1.00  1849.28   123.08     15.0
  10     1.10  1889.94   124.45     15.2
  11     1.20  1857.02   119.94     15.5
  12     1.30  1828.11   166.51     11.0

F = 1889.94 mJy
E = 124.45 mJy
S = 15.2
D = 2.20 arcsec

     
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
      mask          = 'f27_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# couldn't see line, just cleaned in automated mode
# in continuum region for all channels


# export cube to fits file    
fbase = 'f'+str(field)+'_c18o32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')


# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_c18o32.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])


# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_c18o32.mom0*')
immoments(imagename  = 'f'+str(field)+'_c18o32_b4sc.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_c18o32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[2km/s,6km/s]'))
# can't see emission, using same velocity range as 13CO

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
# Flux = 405.97 mJy, rms = 37.55 mJy, S/N = 10.8

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
Measuring COG for M/f27_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 1.79 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 36.67 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10    -3.65    10.85     -0.3
   1     0.20    -5.85    27.97     -0.2
   2     0.30    -2.30    40.52     -0.1 <-- ND
   3     0.40     2.28    57.08      0.0
   4     0.50    33.14    64.92      0.5
   5     0.60   110.60    74.79      1.5
   6     0.70   193.91    80.76      2.4
   7     0.80   261.53   108.99      2.4
   8     0.90   302.25    85.78      3.5
   9     1.00   318.97    81.88      3.9
  10     1.10   343.00   110.37      3.1
  11     1.20   386.08    97.11      4.0
  12     1.30   425.37   113.94      3.7

F = 425.37 mJy
E = 113.94 mJy
S = 3.73
D = 2.60 arcsec

Doesn't look real, just looks like noise spike to the side
Doesn't have 13CO in the same location
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
          chans      = ('range=[2km/s,6km/s]'))                      # CHANGEME (based on above analysis!!)
# can see clear emission

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
# Flux = 2387.74 mJy, rms = 25.21 mJy, S/N = 94.7


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
diameter     total     rms       snr
     3.8    2701.22  106.096       25.5
diameter     total     rms       snr
     2.6    2438.20   82.613       29.5
diameter      peak     rms       snr
     1.4     198.39   25.511        7.8

'''
# used diameter of 3.0" instead since where flux first levels off
#   15    1.500    7845  2562.48  172.642    14.8   198.39   25.511     7.8   1.000
