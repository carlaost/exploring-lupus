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



# LupusIII_34    16:08:01.75   -39:12:31.6 

field = 16                                     # CHANGEME 

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

xc         = 320                               # CHANGEME
yc         = 320                               # CHANGEME
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
      niter         = 100,
      threshold     = 0,
      interactive   = False,
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# can't see gas or continuum emission
# cleaned in automated mode without mask


# export cube to fits file    
fbase = 'f'+str(field)+'_13co32'
os.system('rm -rf '+fbase+'.cube.fits')
exportfits(imagename=fbase+'.image',fitsimage=fbase+'.cube.fits')

# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_13co32.mom0*')
immoments(imagename  = 'f'+str(field)+'_13co32.image',          # CHANGEME (based on above analysis!!)
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
# Flux = -69.68 mJy, rms = 48.96 mJy, S/N = -1.4

# view gas (continuum not detected)
imview(raster=[{'file':'f'+str(field)+'_13co32.mom0'}])

# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_13co32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_13co32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_13co32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_13co32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_13co32.mom0_cropped.fits')

'''
Measuring COG for G/f16_13co32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: 1.86 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 45.06 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10    13.11    11.25      1.2
   1     0.20    18.43    37.83      0.5
   2     0.30   -10.84    47.39     -0.2 <-- ND
   3     0.40   -49.52    63.15     -0.8
   4     0.50   -69.68    83.01     -0.8
   5     0.60   -56.85    99.80     -0.6
   6     0.70   -33.49    93.39     -0.4
   7     0.80   -27.45   123.66     -0.2

F = 18.43 mJy
E = 37.83 mJy
S = 0.49
D = 0.40 arcsec

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
      niter         = 100,
      threshold     = 0,
      interactive   = False,
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# can't see gas or continuum emission
# cleaned in automated mode without mask

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
# Flux = 199.92 mJy, rms = 54.70 mJy, S/N = 3.7

# view gas (continuum not detected)
imview(raster=[{'file':'f'+str(field)+'_c18o32.mom0'}])

# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_c18o32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_c18o32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_c18o32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_c18o32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_c18o32.mom0_cropped.fits')


'''
Measuring COG for G/f16_c18o32.mom0_cropped.fits
Assuming object center (300.0,300.0)
Background: -0.68 mJy/beam km/s
RMS in annulus 4.0-6.0 arcsec = 55.51 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10    10.83    10.78      1.0
   1     0.20    40.32    33.23      1.2
   2     0.30    96.68    60.73      1.6 <-- ND
   3     0.40   157.97    87.31      1.8
   4     0.50   199.92   104.30      1.9
   5     0.60   212.64    93.61      2.3
   6     0.70   201.55   123.70      1.6
   7     0.80   154.58   144.81      1.1

F = 212.64 mJy
E = 93.61 mJy
S = 2.27
D = 1.20 arcsec

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
      niter         = 100,
      threshold     = 0,
      interactive   = False,
      imsize        = imsize,
      cell          = cell,
      weighting     ='briggs',
      robust        = robust,
      imagermode    = imagermode)
# can't see gas or continuum emission
# cleaned in automated mode without mask
  
# redo moment0 maps (now excluding noisy first channel!!)
# os.system('rm -rf f'+str(field)+'_cn32.mom0*')
immoments(imagename  = 'f'+str(field)+'_cn32_b4sc.image',            # CHANGEME (based on above analysis!!)
          outfile    = 'f'+str(field)+'_cn32.mom0',
          moments    = [0],
          includepix = [-10.0,100.0],
          chans      = ('range=[1km/s,7km/s]'))                      # CHANGEME (based on above analysis!!)

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
# Flux = 47.36 mJy, rms = 40.52 mJy, S/N = 1.2

# view gas (continuum not detected)
imview(raster=[{'file':'f'+str(field)+'_cn32.mom0'}])

# re-center image on source and use measure.py to get COG flux
# os.system('rm -rf f'+str(field)+'_cn32.mom0_cropped*')
ia.fromimage(outfile = 'f'+str(field)+'_cn32.mom0_cropped.image',
             infile  = 'f'+str(field)+'_cn32.mom0.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_cn32.mom0_cropped.image',
           fitsimage = 'f'+str(field)+'_cn32.mom0_cropped.fits')


# CAN'T SEE GAS SO JUST USING 1" APER
#     5    0.500     877    46.38   84.827     0.5    98.37   40.021     2.5   0.998

