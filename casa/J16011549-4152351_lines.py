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

# LupusIV_153
# Class F, SpT ?

field = 43                                                  # CHANGEME 

fitspw    = '2,3,4'                                         # line-free channels for fitting continuum
linespw   = '0,1,3'                                         # line spectral windows (C18O, 13CO, CN)

robust     = 0.5                                            # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '0.5km/s'
start      = '0km/s'
nchan      = 15

xc         = 327                               # CHANGEME
yc         = 312                               # CHANGEME
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
# os.system('rm -rf test_f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'test_f'+str(field)+'_13co32.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'test_f'+str(field)+'_13co32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[2.5km/s,5.5km/s]'))
# can see emission clearly, gives highets snr

# first moment map
sigma = 30e-3  # Jy/beam in peak velocity channel
os.system('rm -rf test_f43_13co32_mom1.image')
immoments(imagename  = 'test_f43_13co32.cube.fits',
          outfile    = 'test_f43_13co32_mom1.image',
          moments    = [1],
          includepix = [3.0*sigma,100.0],
          chans      = ('range=[2.5km/s,5.5km/s]'))
os.system('rm -rf test_f43_13co32_mom1.fits')
exportfits(imagename='test_f43_13co32_mom1.image',fitsimage='test_f43_13co32_mom1.fits')
os.system('rm -rf G21_13co32_mom1.image')



# export to fits file    
fbase = 'f'+str(field)+'_13co32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,
           fitsimage=fbase+'.fits')

# measure flux
# imview(raster=[{'file':'f'+str(field)+'_13co32.mom0'}])
im_rms = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 2882.75 mJy, rms = 40.37 mJy, S/N = 71.4

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
Measuring COG for G/f43_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.22 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 41.09 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     37.3      9.6      3.9
   1      0.2    158.9     27.3      5.8
   2      0.3    378.5     53.3      7.1
   3      0.4    635.1     65.9      9.6
   4      0.5    970.5     83.8     11.6
   5      0.6   1302.3    108.2     12.0
   6      0.7   1598.3    126.1     12.7
   7      0.8   1884.7    157.5     12.0
   8      0.9   2156.0    140.6     15.3
   9      1.0   2389.3    191.9     12.4
  10      1.1   2580.1    178.6     14.4
  11      1.2   2785.8    200.8     13.9
  12      1.3   2975.5    229.5     13.0
  13      1.4   3119.1    248.4     12.6
  14      1.5   3239.2    269.1     12.0
  15      1.6   3312.6    337.7      9.8
  16      1.7   3319.6    317.3     10.5
  17      1.8   3286.8    343.8      9.6
  18      1.9   3221.3    353.9      9.1
  19      2.0   3127.6    275.7     11.3
  20      2.1   3034.0    353.4      8.6
  21      2.2   2967.0    380.9      7.8
  22      2.3   2911.8    318.7      9.1
  23      2.4   2869.6    339.5      8.5
  24      2.5   2821.3    294.8      9.6
  25      2.6   2721.6    299.3      9.1

F = 3319.6 mJy
E = 317.3 mJy
S = 10.5
D = 3.4 arcsec

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
      mask          = 'f43_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line very clearly, so just cleaned lightly 
# within continuum region for all channels at once

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
          chans      = ('range=[3km/s,5km/s]'))                        # CHANGEME (based on above analysis!!)
# can see emission, gives highest snr, same as 13CO

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
# Flux = 1578.91 mJy, rms = 49.76 mJy, S/N = 31.7


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
Measuring COG for G/f43_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.40 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 48.19 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     30.9     11.5      2.7
   1      0.2    115.9     32.3      3.6
   2      0.3    287.9     43.7      6.6
   3      0.4    516.8     68.0      7.6
   4      0.5    746.6     90.1      8.3
   5      0.6    893.6     91.2      9.8
   6      0.7   1002.8    139.3      7.2
   7      0.8   1118.3    158.3      7.1
   8      0.9   1237.5    137.6      9.0
   9      1.0   1363.9    171.4      8.0
  10      1.1   1476.6    199.5      7.4
  11      1.2   1558.2    182.5      8.5 <-- used this (flux levels off, best ap in CASA)
  12      1.3   1591.5    207.5      7.7
  13      1.4   1605.3    260.2      6.2
  14      1.5   1655.5    265.8      6.2
  15      1.6   1708.8    221.3      7.7
  16      1.7   1720.1    245.1      7.0
  17      1.8   1686.8    204.6      8.2
  18      1.9   1606.8    226.7      7.1
  19      2.0   1522.3    220.1      6.9
  20      2.1   1436.0    231.2      6.2
  21      2.2   1405.2    283.5      5.0
  22      2.3   1436.7    235.7      6.1
  23      2.4   1451.1    294.1      4.9
  24      2.5   1442.3    264.1      5.5
  25      2.6   1441.7    257.8      5.6

F = 1720.1 mJy
E = 245.1 mJy
S = 7.0
D = 3.4 arcsec

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
          chans      = ('range=[2km/s,5km/s]'))                        # CHANGEME (based on above analysis!!)
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
# Flux = 1699.44 mJy, rms = 33.90 mJy, S/N = 50.1


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
Measuring COG for G/f43_cn32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.40 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 33.74 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     41.2      8.2      5.0
   1      0.2    133.3     23.7      5.6
   2      0.3    264.2     33.8      7.8
   3      0.4    414.6     47.9      8.7
   4      0.5    605.9     68.9      8.8
   5      0.6    813.2     91.1      8.9
   6      0.7   1020.3    107.8      9.5
   7      0.8   1180.3    108.0     10.9
   8      0.9   1304.0    134.1      9.7
   9      1.0   1450.1    161.6      9.0
  10      1.1   1576.3    157.4     10.0
  11      1.2   1669.9    211.0      7.9
  12      1.3   1722.3    220.1      7.8
  13      1.4   1750.3    235.1      7.4
  14      1.5   1789.6    248.8      7.2 <-- used this (where flux levels off; looks good in CASA)
  15      1.6   1826.4    232.9      7.8
  16      1.7   1820.6    296.2      6.1
  17      1.8   1809.3    317.6      5.7
  18      1.9   1858.3    311.7      6.0
  19      2.0   1913.2    289.6      6.6
  20      2.1   1919.9    312.2      6.1
  21      2.2   1930.6    360.6      5.4
  22      2.3   1960.5    304.2      6.4
  23      2.4   2004.1    298.2      6.7
  24      2.5   2042.6    277.5      7.4
  25      2.6   2014.7    311.8      6.5

F = 2042.6 mJy
E = 277.5 mJy
S = 7.4
D = 5.0 arcsec

'''

