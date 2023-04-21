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


# LupusIII_50  +16:08:30.69 -38:28:26.8
# Class II, K1

field = 9                                                   # CHANGEME 

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
start      = '-2km/s'
nchan      = 12

xc         = 326                                            # CHANGEME
yc         = 306                                            # CHANGEME
in_a       = 80
out_a      = 120
aper       = 1.25

boxwidth = 300.
box = rg.box([xc-boxwidth,yc-boxwidth],[xc+boxwidth,yc+boxwidth])


split(vis = visfile,
      outputvis = fieldvis,
      field = field,
      datacolumn = 'data')



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
      niter         = 5000,
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
          chans      = ('range=[1km/s,9km/s]'))

# export to fits file    
fbase = 'test_f'+str(field)+'_13co32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,
           fitsimage=fbase+'.fits')



#### FIRST MOMENT MAP
sigma = 35e-3  # Jy/beam in peak velocity channel
os.system('rm -rf test_f9_13co32_mom1.image')
immoments(imagename  = 'test_f9_13co32.cube.fits',
          outfile    = 'test_f9_13co32_mom1.image',
          moments    = [1],
          includepix = [3.0*sigma,100.0],
          chans      = ('range=[1km/s,9km/s]'))
os.system('rm -rf test_f9_13co32_mom1.fits')
exportfits(imagename='test_f9_13co32_mom1.image',fitsimage='test_f9_13co32_mom1.fits')
os.system('rm -rf test_f9_13co32_res0.3_mom1.image')


#### FIRST MOMENT MAP
sigma = 35e-3  # Jy/beam in peak velocity channel
os.system('rm -rf test_f9_13co32_mom2.image')
immoments(imagename  = 'test_f9_13co32.cube.fits',
          outfile    = 'test_f9_13co32_mom2.image',
          moments    = [2],
          includepix = [3.0*sigma,100.0],
          chans      = ('range=[1km/s,9km/s]'))
os.system('rm -rf test_f9_13co32_mom1.fits')
exportfits(imagename='test_f9_13co32_mom1.image',fitsimage='test_f9_13co32_mom1.fits')
os.system('rm -rf test_f9_13co32_res0.3_mom1.image')





# measure flux
# imview(raster=[{'file':'f'+str(field)+'_13co32.mom0'}])
im_rms = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 6518.87 mJy, rms = 70.36 mJy, S/N = 92.7

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
Measuring COG for G/f9_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.52 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 75.29 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10   198.79    15.40     12.9
   1     0.20   723.28    46.47     15.6
   2     0.30  1597.21    76.39     20.9
   3     0.40  2578.79   115.67     22.3
   4     0.50  3574.32   119.84     29.8
   5     0.60  4375.40   166.53     26.3
   6     0.70  5058.44   172.47     29.3
   7     0.80  5630.33   174.36     32.3
   8     0.90  6079.59   207.74     29.3
   9     1.00  6449.81   223.62     28.8
  10     1.10  6657.41   250.96     26.5
  11     1.20  6681.97   261.98     25.5
  12     1.30  6626.41   284.84     23.3

F = 6681.97 mJy
E = 261.98 mJy
S = 25.51
D = 2.40 arcsec
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
          chans      = ('range=[1km/s,8km/s]'))

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
# Flux = 1573.52 mJy, rms = 74.05 mJy, S/N = 21.2


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
Measuring COG for G/f9_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.14 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 76.44 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10    52.58    20.56      2.6
   1     0.20   182.08    56.67      3.2
   2     0.30   389.22    99.57      3.9
   3     0.40   644.39   112.78      5.7
   4     0.50   953.76   142.79      6.7
   5     0.60  1208.38   160.18      7.5
   6     0.70  1391.54   160.94      8.6
   7     0.80  1528.53   188.68      8.1
   8     0.90  1635.66   207.19      7.9
   9     1.00  1696.71   238.48      7.1 <--- using this where flux levels off
  10     1.10  1685.69   254.04      6.6
  11     1.20  1689.91   250.73      6.7
  12     1.30  1724.29   258.45      6.7

F = 1724.29 mJy
E = 258.45 mJy
S = 6.67
D = 2.60 arcsec

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
          chans      = ('range=[0km/s,10km/s]'))                        # CHANGEME (based on above analysis!!)

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
# Flux = 7164.63 mJy, rms = 54.67 mJy, S/N = 131.1


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
Measuring COG for G/f9_cn32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.16 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 55.88 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1    207.2     13.7     15.2
   1      0.2    744.1     34.4     21.7
   2      0.3   1626.5     57.1     28.5
   3      0.4   2597.2     87.9     29.5
   4      0.5   3602.8    115.7     31.1
   5      0.6   4458.7    168.4     26.5
   6      0.7   5205.0    167.7     31.0
   7      0.8   5826.4    246.6     23.6
   8      0.9   6364.0    172.3     36.9
   9      1.0   6794.1    254.5     26.7
  10      1.1   7006.7    294.6     23.8
  11      1.2   7111.1    271.7     26.2
  12      1.3   7217.5    367.4     19.6
  13      1.4   7291.1    371.8     19.6
  14      1.5   7267.3    418.3     17.4
  15      1.6   7209.4    501.9     14.4
  16      1.7   7192.2    474.0     15.2
  17      1.8   7220.3    478.0     15.1

F = 7291.1 mJy
E = 371.8 mJy
S = 19.6
D = 2.8 arcsec

'''
