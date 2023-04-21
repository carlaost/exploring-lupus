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


# LupusIII_19  16:07:08.570 -39:14:07.699
# Class F, SpT ?


field = 28                                     # CHANGEME 

file_ms = '../science_calibrated.ms'
contspw   = '2,3,4'
contspw_w = [128,3840,1920] 

robust     = 0.5
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'
refant     = 'DA52'                            # CHANGEME

xc         = 333                               # CHANGEME
yc         = 315                               # CHANGEME
in_a       = 80
out_a      = 120
aper       = 1.25                               # CHANGEME

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


# light clean (100 iterations) 
# os.system('rm -rf f'+str(field)+'_cont_b4sc*')
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
# Peak = 18.07 mJy, rms = 0.35 mJy, S/N = 52.0



   
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
# 2 of 40 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/04:40:40.7
# 4 of 40 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/05:14:20.6

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
# Peak = 21.35 mJy, rms = 0.40 mJy, S/N = 53.1 (slightly better)


# inspect images
imview(raster=[{'file':'f'+str(field)+'_cont_b4sc.image'},
               {'file':'f'+str(field)+'_cont_pcal1_clean.image'}])
# pcal1 looks WORSE




# ======================== Self-Calibrate 2 ==================

# decrease phase self-cal solution interval to a few times integration time
# int = 6s (from X125.log)
gaincal(vis = 'f'+str(field)+'_cont.vis',
        caltable = 'f'+str(field)+'_cont_pcal2',
        refant = refant,
        solint = '20s',                           # CHANGEME
        combine = 'spw',
        gaintype = 'T',
        spw = '',
        calmode = 'p',
        minblperant = 4,
        minsnr = 3)

#2 of 38 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/04:40:37.4
#6 of 35 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/04:40:49.8
#2 of 36 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/05:14:20.8

## TOO MANY FLAGS, STOPPING HERE.


# ======================== Best Continuum Map ==================


# do not apply self-cal. all were horrible, due to faint source?
# RE-MAKED _CONT.VIS FILE SO NO CALIBRATION APPLIED TO IT!

# deep clean, trying different robust weights
# os.system('rm -rf f'+str(field)+'_cont_best*')
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
      robust      = -1.0,                                      # CHANGEME
      imagermode  = imagermode)
# placed mask around outer cont contour
# stopped after 600 iterations once the inside became green


im_max = imstat(imagename = 'f'+str(field)+'_cont_best.image')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
bmaj = imhead(imagename = 'f'+str(field)+'_cont_best.image', mode="get", hdkey="beammajor")
bmin = imhead(imagename = 'f'+str(field)+'_cont_best.image', mode="get", hdkey="beamminor")
print 'Peak = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_max, 1000*im_rms, im_max/im_rms)
print 'Beam = {0:.2f} x {1:.2f} arcsec'.format(bmaj.get('value'),bmin.get('value'))

# robust = -1.0
# Peak = 16.48 mJy, rms = 0.49 mJy, S/N = 33.7
# Beam = 0.33 x 0.27 arcsec

# save this to a fits file
exportfits(imagename='f'+str(field)+'_cont_best.image', fitsimage='f'+str(field)+'_cont.fits')

# compare to before (trade-off with smaller beam seems worth it)
imview(raster=[{'file':'f'+str(field)+'_cont_b4sc.image'},
               {'file':'f'+str(field)+'_cont_best.image'}])

# measure flux
# imview(raster=[{'file':'f'+str(field)+'_cont_best.image'}])
im_rms = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 91.92 mJy, rms = 0.49 mJy, S/N = 188.0


# re-center image on source and use measure.py to get COG flux
ia.fromimage(outfile = 'f'+str(field)+'_cont_cropped.image',
             infile  = 'f'+str(field)+'_cont.fits',
             region  = box )
ia.close() 
exportfits(imagename = 'f'+str(field)+'_cont_cropped.image',
           fitsimage = 'f'+str(field)+'_cont_cropped.fits')
'''
diameter     total     rms       snr
     2.4      92.07    1.485       62.0
diameter     total     rms       snr
     1.6      83.51    1.045       79.9
diameter      peak     rms       snr
     0.8      16.48    0.501       32.9
'''



# ======================== Measure flux with UVMODELFIT ==================

# calculate offset from phase center in arcsec
pixscale = 0.03             # must match 'cell'                 
dx = pixscale*(320.0-xc)    # offset to east (left)
dy = pixscale*(yc-320.0)    # offset to north (up)


  
# measure flux as gaussian
uvmodelfit(vis       = 'f'+str(field)+'_cont.vis',
           comptype  = 'G',
           sourcepar = [im_flux,dx,dy,0.5,0.5,-30.0],
           varypar   = [T,T,T,T,T,T],
           niter     = 10)

'''
           
reduced chi2=1.39237
I = 0.091748 +/- 0.00104654
x = -0.355701 +/- 0.00282983 arcsec
y = -0.184935 +/- 0.0047132 arcsec
a = 1.03522 +/- 0.0124378 arcsec
r = 0.296366 +/- 0.00696239
p = -25.1661 +/- 0.410735 deg

consistent with aperture method
16:07:08.539 -39:14:07.885

'''


