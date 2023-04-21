#!/usr/bin/env

"""

split, clean, and self-cal continuum and line data
  
NOTE: this is intended to be an interactive, iterative process
      so this is more a log that should be run by cutting and
      pasting into casa rather than as an executable script

      search "CHANGEME" for variables to be changed
      
10/9/15 MCA

"""



# ======================== Setup ===========================


# LupusIII_1015 15:59:28.366 -40:21:51.486
# Class II, K4

field = 14                                     # CHANGEME 

file_ms = '../science_calibrated.ms'
contspw   = '2,3,4'
contspw_w = [128,3840,1920] 

robust     = 0.5                               # CHANGEME
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'
refant     = 'DA52'                            # CHANGEME

xc         = 327                               # CHANGEME
yc         = 311                               # CHANGEME
in_a       = 80
out_a      = 120
aper       = 1.25

boxwidth = 300.
box = rg.box([xc-boxwidth,yc-boxwidth],[xc+boxwidth,yc+boxwidth])



# ======================= Split Off Continuum ========================


# split off field from full ms
split(vis = file_ms,
      outputvis = 'f'+str(field)+'.vis',
      field = field,
      datacolumn = 'data')

# split off continuum (take the large bw spw and average
split(vis = 'f'+str(field)+'.vis',
      outputvis = 'f'+str(field)+'_cont.vis',
      spw = contspw,
      width = contspw_w,
      datacolumn = 'data')

# plot uv-distance vs. amplitude
plotms(vis='f'+str(field)+'_cont.vis',
       xaxis='uvdist',yaxis='amp',
       coloraxis='spw')
       # plotfile='f'+str(field)+'_ampuv_orig.png'
       # showgui=False,
       # highres=True,
       # overwrite=True)
# source is resolved

# find antenna close to center of configuration
# check pipeline log that this ant is OK
plotants(vis='f'+str(field)+'_cont.vis') #, figfile='f'+str(field)+'_ants.png')



                        
# ================== Clean continuum before selfcal ==================

# os.system('rm -rf f'+str(field)+'_cont_b4sc*')

# light clean (100 iterations) to set the mask around the main peaks
clean(vis = 'f'+str(field)+'_cont.vis',
      imagename = 'f'+str(field)+'_cont_b4sc',
      mode = 'mfs',
      psfmode = 'clark',
      niter = 100,
      threshold = '0.0mJy',
      interactive = True,
      mask = '',
      cell = cell,
      imsize = imsize,
      weighting = 'briggs',
      robust = robust,
      imagermode = imagermode)

im_max = imstat(imagename = 'f'+str(field)+'_cont_b4sc.image')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_cont_b4sc.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
print 'Peak = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_max, 1000*im_rms, im_max/im_rms)
# Peak = 47.65 mJy, rms = 0.51 mJy, S/N = 93.3


        
# ======================== Self-Calibrate 1 ==================

# first combine all the data by time (solint = inf)
# i.e., phase self-cal over entire integration time
gaincal(vis = 'f'+str(field)+'_cont.vis',
        caltable = 'f'+str(field)+'_cont_pcal1',
        refant = refant,
        solint = 'inf',
        combine = 'spw',
        gaintype = 'T',
        spw = '',
        calmode = 'p',
        minblperant = 4,
        minsnr = 3)

# plot phase for each antenna
plotcal(caltable = 'f'+str(field)+'_cont_pcal1',
        xaxis = 'time',
        yaxis = 'phase',
        spw = '',
        iteration = 'antenna',
        subplot = 421,
        plotrange = [0,0,-200,200]) # narrow yrange phases close to zero
# no variation between integration times (expected since solin=inf)
# note DV02 has no data (100% flagged in pipeline calibration)


# apply calibration to data
applycal(vis = 'f'+str(field)+'_cont.vis',
        spw = '',
        gaintable = ['f'+str(field)+'_cont_pcal1'],
        spwmap = [0,0,0],
        calwt = T,
        flagbackup = F)

# clean self-calibrated data
clean(vis = 'f'+str(field)+'_cont.vis',
      imagename = 'f'+str(field)+'_cont_pcal1_clean',
      mode = 'mfs',
      psfmode = 'clark',
      niter = 100,
      threshold   = '0.0mJy',
      interactive = False,
      mask = 'f'+str(field)+'_cont_b4sc.mask',
      cell        = cell,
      imsize      = imsize,
      weighting   = 'briggs',
      robust      = robust,
      imagermode  = imagermode)

im_max = imstat(imagename = 'f'+str(field)+'_cont_pcal1_clean.image')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_cont_pcal1_clean.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
print 'Peak = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_max, 1000*im_rms, im_max/im_rms)
# Peak = 47.96 mJy, rms = 0.48 mJy, S/N = 100.9

# inspect images
imview(raster=[{'file':'f'+str(field)+'_cont_b4sc.image'},
               {'file':'f'+str(field)+'_cont_pcal1_clean.image'}])
# second peak has strengthened a little



# ======================== Best Continuum Map ==================


# so now run the same applycal but with flagbackup = T,
applycal(vis = 'f'+str(field)+'_cont.vis',
        spw = '',
        gaintable = ['f'+str(field)+'_cont_pcal1'],         # CHANGEME
        spwmap = [0,0,0],
        calwt = T,
        flagbackup = T)

# deep clean, trying different robust weights
clean(vis = 'f'+str(field)+'_cont.vis',
      imagename = 'f'+str(field)+'_cont_best',
      mode = 'mfs',
      psfmode = 'clark',
      niter = 2000,
      threshold   = '0.0mJy',
      interactive = True,
      mask = '',
      cell        = cell,
      imsize      = imsize,
      weighting   = 'briggs',
      robust      = -1,                                      # CHANGEME
      imagermode  = imagermode)
# placed mask around outer continuum contour
# stopped after 700 iterations once the inside became green


im_max = imstat(imagename = 'f'+str(field)+'_cont_best.image')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
bmaj = imhead(imagename = 'f'+str(field)+'_cont_best.image', mode="get", hdkey="beammajor")
bmin = imhead(imagename = 'f'+str(field)+'_cont_best.image', mode="get", hdkey="beamminor")
print 'Peak = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_max, 1000*im_rms, im_max/im_rms)
print 'Beam = {0:.2f} x {1:.2f} arcsec'.format(bmaj.get('value'),bmin.get('value'))

# robust = -1 
# Peak = 45.30 mJy, rms = 0.46 mJy, S/N = 99.2
# Beam = 0.32 x 0.28 arcsec

# robust = -1 back to the same sort of S/N but the slightly smaller beam size provides a slightly
# clearer view of the inner cavity so is worth the payoff

# save this to a fits file
exportfits(imagename='f'+str(field)+'_cont_best.image', fitsimage='f'+str(field)+'_cont.fits')

# compare to before self-cal
imview(raster=[{'file':'f'+str(field)+'_cont_b4sc.image'},
               {'file':'f'+str(field)+'_cont_best.image'}])

# measure flux
# imview(raster=[{'file':'f'+str(field)+'_cont_best.image'}])
im_rms = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 274.66 mJy, rms = 0.46 mJy, S/N = 601.3


# re-center image on source and use measure.py to get COG flux
ia.fromimage(outfile = 'f'+str(field)+'_cont_cropped.image',
             infile  = 'f'+str(field)+'_cont.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_cont_cropped.image',
           fitsimage = 'f'+str(field)+'_cont_cropped.fits')
'''
Measuring COG for G/f14_cont_cropped.fits
Assuming object center (300.0,300.0)
Background: 0.00 mJy/beam km/s
RMS in annulus 4.0-9.0 arcsec = 0.50 mJy/beam km/s

   i   radius    flux      err       snr
       (asec)    (mJy)     (mJy)
   0     0.10     9.70     0.15     62.8
   1     0.20    37.48     0.32    117.2
   2     0.30    85.82     0.48    179.5
   3     0.40   138.12     0.59    233.3
   4     0.50   188.26     0.63    299.9
   5     0.60   224.14     0.89    250.9
   6     0.70   248.43     0.82    301.5
   7     0.80   263.17     0.95    276.3
   8     0.90   271.40     1.12    242.3
   9     1.00   275.14     1.30    212.2
  10     1.10   275.50     1.44    191.2
  11     1.20   274.82     1.68    163.6
  12     1.30   274.62     1.80    152.5

F = 275.50 mJy
E = 1.44 mJy
S = 191.21
D = 2.20 arcsec

'''


# A_ap = np.pi*(1.1**2)/0.03
# A_beam = 113.0
# 0.46*A_ap/A_beam = 0.515814





# ======================== Measure flux with UVMODELFIT ==================

# calculate offset from phase center in arcsec
pixscale = 0.03             # must match 'cell'                 
dx = pixscale*(320.0-xc)    # offset to east (left)
dy = pixscale*(yc-320.0)    # offset to north (up)

  
# measure flux as gaussian
uvmodelfit(vis       = 'f'+str(field)+'_cont.vis',
           comptype  = 'G',
           sourcepar = [im_flux,dx,dy,0.5,0.5,-70.0],
           varypar   = [T,T,T,T,T,T],
           niter     = 10)

'''
           
reduced chi2=1.5909
I = 0.305037 +/- 0.00122294
x = -0.203522 +/- 0.0018746 arcsec
y = -0.276375 +/- 0.000967499 arcsec
a = 1.14991 +/- 0.0048408 arcsec
r = 0.369156 +/- 0.00243405
p = -71.3731 +/- 0.162642 deg

consistent with aperture method
much larger errors?

'''
