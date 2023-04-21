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


# LupusIII_141
# 16:13:44.110 -37:36:46.400

field = 24                                     # CHANGEME 

file_ms = '../science_calibrated.ms'
contspw   = '2,3,4'
contspw_w = [128,3840,1920] 

robust     = 0.5
imsize     = [640,640]
cell       = '0.03arcsec'
imagermode = 'csclean'
refant     = 'DA52'                            # CHANGEME

xc         = 334                               # CHANGEME
yc         = 313                               # CHANGEME
in_a       = 80
out_a      = 120
aper       = 0.5                               # CHANGEME

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
# source is resolved?

# find antenna close to center of configuration
# check pipeline log that this ant is OK
plotants(vis='f'+str(field)+'_cont.vis') #, figfile='f'+str(field)+'_ants.png')



                        
# ================== Clean continuum before selfcal ==================


# light clean (100 iterations) around BOTH sources
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
# Peak = 2.06 mJy, rms = 0.40 mJy, S/N = 5.1



   
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

# 33 of 40 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/04:38:27.0
# 33 of 40 solutions flagged due to SNR < 3 in spw=0 at 2015/06/14/05:12:12.0

# TOO MANY SOLUTIONS FLAGGED, SKIPPING SELF-CAL




# ======================== Best Continuum Map ==================


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
      robust      = 0.5,                                      # CHANGEME
      imagermode  = imagermode)
# placed mask around smaller continuum contour 
# stopped after 200 iterations once the inside became green

im_max = imstat(imagename = 'f'+str(field)+'_cont_best.image')['max'][0]
im_rms = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
bmaj = imhead(imagename = 'f'+str(field)+'_cont_best.image', mode="get", hdkey="beammajor")
bmin = imhead(imagename = 'f'+str(field)+'_cont_best.image', mode="get", hdkey="beamminor")
print 'Peak = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_max, 1000*im_rms, im_max/im_rms)
print 'Beam = {0:.2f} x {1:.2f} arcsec'.format(bmaj.get('value'),bmin.get('value'))

# robust = 0.5
# Peak = 2.06 mJy, rms = 0.40 mJy, S/N = 5.1
# Beam = 0.34 x 0.29 arcsec

# save this to a fits file
exportfits(imagename='f'+str(field)+'_cont_best.image', fitsimage='f'+str(field)+'_cont.fits')


# measure flux
# imview(raster=[{'file':'f'+str(field)+'_cont_best.image'}])
im_rms = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                region='annulus[['+str(xc)+'pix,'+str(yc)+'pix],['+str(in_a)+'pix,'+str(out_a)+'pix]]')['rms'][0]
im_flux = imstat(imagename = 'f'+str(field)+'_cont_best.image',
                 region='circle[['+str(xc)+'pix,'+str(yc)+'pix],'+str(aper)+'arcsec]')['flux'][0]
print 'Flux = {0:.2f} mJy, rms = {1:.2f} mJy, S/N = {2:.1f}'.format(1000*im_flux, 1000*im_rms, im_flux/im_rms)
# Flux = 1.81 mJy, rms = 0.39 mJy, S/N = 4.7



# ======================== Measure flux with UVMODELFIT ==================

# calculate offset from phase center in arcsec
pixscale = 0.03             # must match 'cell'                 
dx = pixscale*(320.0-xc)    # offset to east (left)
dy = pixscale*(yc-320.0)    # offset to north (up)


# measure flux as point source
uvmodelfit(vis       = 'f'+str(field)+'_cont.vis',
           comptype  = 'P',
           sourcepar = [im_flux,dx,dy],
           varypar   = [T,T,T],
           niter     = 10)
'''

reduced chi2=1.38275
I = 0.00213953 +/- 0.000301619
x = -0.404516 +/- 0.0223679 arcsec
y = -0.206608 +/- 0.0196803 arcsec

higher than aperture method

'''

  
# measure flux as gaussian
uvmodelfit(vis       = 'f'+str(field)+'_cont.vis',
           comptype  = 'G',
           sourcepar = [im_flux,dx,dy,0.5,1,0],
           varypar   = [T,T,T,T,T,T],
           niter     = 10)

'''
           
reduced chi2=1.38282
I = 0.00218331 +/- 0.0004478
x = -0.403609 +/- 0.0228613 arcsec
y = -0.203876 +/- 0.021878 arcsec
a = 0.100056 +/- 0.131809 arcsec
r = 1.57686e-10 +/- 9.20592e+09
p = -2.92245 +/- 110.918 deg

a/e_a < 2 so used point source method

'''
