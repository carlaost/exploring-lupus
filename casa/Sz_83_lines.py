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



# LupusIII_1005  +15:56:42.31 -37:49:15.6
# Class II, K7

field = 21

fitspw    = '2,3:0~2049;2151~2899;3051~3480,4'              # line-free channels for fitting continuum
fitspw    = '2,3,4'                                         # line-free channels for fitting continuum
linespw   = '0,1,3'                                         # line spectral windows (C18O, 13CO, CN)

robust     = 0.5
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'

outframe   = 'lsrk'
veltype    = 'radio'
width      = '1.0km/s'
start      = '0.0km/s'
nchan      = 10

xc         = 326                               # CHANGEME
yc         = 309                               # CHANGEME
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
      # spw           = '1',
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


# create moment0 maps (excluding noisy first channel!!)
# os.system('rm -rf tesT_f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'test_f'+str(field)+'_13co32.image',
          outfile    = 'test_f'+str(field)+'_13co32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[3km/s,6km/s]'))
# gives highest snr

# export to fits file    
fbase = 'test_f'+str(field)+'_13co32.mom0'
os.system('rm -rf '+fbase+'.fits')
exportfits(imagename=fbase,fitsimage=fbase+'.fits')



#### FIRST MOMENT MAP
sigma = 25e-3  # Jy/beam in peak velocity channel
os.system('rm -rf test_f21_13co32_mom1.image')
immoments(imagename  = 'test_f21_13co32.cube.fits',
          outfile    = 'test_f21_13co32_mom1.image',
          moments    = [1],
          includepix = [3.0*sigma,100.0],
          chans      = ('range=[3km/s,6km/s]'))
os.system('rm -rf test_f21_13co32_mom1.fits')
exportfits(imagename='test_f21_13co32_mom1.image',fitsimage='test_f21_13co32_mom1.fits')
os.system('rm -rf test_f21_13co32_res0.3_mom1.image')




# measure flux
# imview(raster=[{'file':'f'+str(field)+'_13co32.mom0'}])
im_rms = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_13co32.mom0',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 2864.29 mJy, rms = 47.19 mJy, S/N = 60.7



# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_13co32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_13co32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_13co32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_13co32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_13co32.mom0_cropped.fits')


'''
Measuring COG for G/f21_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.03 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 46.59 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1    152.0     11.9     12.7
   1      0.2    481.8     28.2     17.1
   2      0.3    908.4     52.1     17.4
   3      0.4   1344.8     57.9     23.2
   4      0.5   1832.6     83.8     21.9
   5      0.6   2277.6     98.1     23.2
   6      0.7   2655.4    120.9     22.0
   7      0.8   2922.0    144.7     20.2
   8      0.9   3062.3    154.4     19.8
   9      1.0   3078.0    155.4     19.8
  10      1.1   2982.1    161.2     18.5
  11      1.2   2870.7    198.5     14.5
  12      1.3   2890.1    165.5     17.5
  13      1.4   3003.3    172.2     17.4

F = 3078.0 mJy
E = 155.4 mJy
S = 19.8
D = 2.0 arcsec

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
      mask          = 'f21_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line, so just cleaned lightly 
# within continuum region for all channels at once


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
          chans      = ('range=[3km/s,6km/s]'))

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
# Flux = 928.82 mJy, rms = 53.24 mJy, S/N = 17.4


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
Measuring COG for G/f21_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.00 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 55.58 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     23.1     14.2      1.6
   1      0.2    118.9     30.9      3.8
   2      0.3    313.2     58.1      5.4
   3      0.4    525.7     76.0      6.9
   4      0.5    733.3     82.4      8.9
   5      0.6    884.5     99.0      8.9
   6      0.7    969.1    112.9      8.6
   7      0.8    994.3    152.1      6.5
   8      0.9    987.9    127.9      7.7
   9      1.0    957.1    137.3      7.0
  10      1.1    913.3    134.0      6.8
  11      1.2    915.9    180.6      5.1
  12      1.3    936.7    175.8      5.3
  13      1.4    943.8    190.5      5.0

F = 994.3 mJy
E = 152.1 mJy
S = 6.5
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
      niter         = 500,
      threshold     = 0,
      interactive   = False,
      mask          = 'f21_cont_mask.crtf',
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# could not see line clearly (extended), so just cleaned lightly 
# within continuum region for all channels at once


# use viewer to check channel maps and spectrum
# make sure that velocity range is adequate and continuum subtraction ok
imview(raster   = [{'file':'f'+str(field)+'_cn32_b4sc.image'}],
        contour = [{'file':'f'+str(field)+'_cont.fits'}])
# can see peaks 

# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_cn32.mom0*')
immoments(imagename  = 'f'+str(field)+'_cn32_b4sc.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_cn32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[3km/s,6km/s]'))                        # CHANGEME (based on above analysis!!)
# gives highest snr

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
# Flux = 1898.32 mJy, rms = 33.85 mJy, S/N = 56.1


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
Measuring COG for G/f21_cn32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 1.11 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 33.80 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0      0.1     29.4      7.0      4.2
   1      0.2    100.5     21.4      4.7
   2      0.3    203.7     31.7      6.4
   3      0.4    321.7     50.0      6.4
   4      0.5    482.7     70.0      6.9
   5      0.6    673.2     87.8      7.7
   6      0.7    899.5     89.5     10.1
   7      0.8   1133.9     91.2     12.4
   8      0.9   1338.1    141.5      9.5
   9      1.0   1528.0    141.8     10.8
  10      1.1   1700.9    164.2     10.4
  11      1.2   1850.5    209.4      8.8
  12      1.3   1922.2    179.8     10.7
  13      1.4   1914.3    249.0      7.7

F = 1922.2 mJy
E = 179.8 mJy
S = 10.7
D = 2.6 arcsec
'''
