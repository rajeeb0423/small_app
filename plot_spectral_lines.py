import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import hide_pages

import numpy as np
import aplpy
import glob

from astropy import wcs
from astropy.io import fits
from astropy.nddata.utils import Cutout2D

#from regions import Regions

import matplotlib.pyplot as plt

def min_max_vals(img_val):
    min_flux = np.nanmin(img_val.data)
    max_flux = np.nanmax(img_val.data)
    return min_flux, max_flux

def drawContours(contstart=None,contend=None,contnoise=None):
    poscontours = np.geomspace(contstart,contend, num=7)
    negcontours=poscontours[::-1]*(-1.0)
    contours=np.concatenate((negcontours,poscontours))*contnoise
    
    return contours

def standardStuff(f, length, dist_val, color):
    f.add_scalebar(length/3600.0,color=color)
    f.scalebar.set_corner('bottom right')
    f.scalebar.set_label(str(length*dist_val)+' AU')
    f.scalebar.set_linewidth(5)
    f.scalebar.set_font_size(20)

    f.add_beam()
    f.beam.set_corner('bottom left')
    f.beam.set_color('black')
    f.beam.set_frame(True)

def plot_continuum(fig, cont, rms_region, distance):

    hdul = fits.open(cont)
    cont_img = hdul[0]
    cont_header = cont_img.header
    w = wcs.WCS(cont_header, hdul)
    ra_pix, dec_pix = cont_header['naxis1']//2, cont_header['naxis2']//2
    ra, dec = w.all_pix2world(ra_pix, dec_pix, 0)

    region_for_rms = rms_region.to_pixel(w)
    position = (region_for_rms.center.x, region_for_rms.center.y)
    size = (region_for_rms.height, region_for_rms.width)

    region_for_rms = Cutout2D(cont_img.data, position, size)
    rms_val = np.sqrt(np.nanmean((region_for_rms.data)**2))

    minval, maxval = min_max_vals(cont_img)
    gc = aplpy.FITSFigure(cont_img, figure=fig)
    gc.show_colorscale(vmin= minval, vmax=maxval, cmap='inferno', stretch='arcsinh')
    gc.add_colorbar()
    standardStuff(gc, 1, distance, 'w')
    return ra, dec, gc, cont_header, rms_val

def plot_mom_map(fig, mom_map, distance, cmap_val, v_sys=None):

    hdul = fits.open(mom_map)
    mom_img = hdul[0]
    mom_header = mom_img.header
    w = wcs.WCS(mom_header, hdul)
    ra_pix, dec_pix = mom_header['naxis1']//2, mom_header['naxis2']//2
    ra, dec = w.all_pix2world(ra_pix, dec_pix, 0)

    if v_sys == None:
        minval, maxval = np.nanpercentile(mom_img.data, (0.25, 99.75))
    else:
        minval, maxval = v_sys-3, v_sys+3

    gc = aplpy.FITSFigure(mom_map, figure=fig)
    st.markdown(minval)
    st.markdown(maxval)
    gc.show_colorscale(vmin=minval, vmax=maxval, cmap = cmap_val, stretch ='linear')
    gc.add_colorbar()
    #contours=drawContours(5, 405, rms_val)
    #gc.show_contour(cont_fig, levels=contours, colors='k', linewidths=1.0)
    standardStuff(gc, 1, distance, 'k')
    return ra, dec, gc, mom_header

def display_footer():
    st.divider()
    footer = st.container()
    with footer:
        st.markdown("<h1 style='text-align: Right; color: #808080;'>Made By:</h1>", unsafe_allow_html=True)
        st.markdown("""<p style='text-align: Right; color: #808080;'>Rajeeb Sharma, PhD fellow<br>
                    Niels Bohr Institute, University of Copenhagen<br>
                    <a href='mailto:rajeeb.sharma@nbi.ku.dk'>rajeeb.sharma@nbi.ku.dk</a>
                    </p>""", unsafe_allow_html=True)


def main():
    st.set_page_config(page_title= 'eDisk Spectral Plots', page_icon='eDisk_logo_ver.4.jpg',layout="wide")

    st.markdown(
        """
    <style>
        [data-testid="stMainMenu"] {
            display: none
        }
    </style>
    """,unsafe_allow_html=True)

    hide_pages(['Main','Plot'])

    if st.button('Return Back'):
        switch_page('Main')
    
    molecules=['12CO', '13CO', 'C18O', 'DCN', 'CH3OH', 'SiO', 
             'SO', 'H2CO_3_03-2_02_218.22GHz', 
             'H2CO_3_21-2_20_218.76GHz',  
             'H2CO_3_22-2_21_218.47GHz',
             'C3H2_217.82',
             'C3H2_217.94',
             'C3H2_218.16']
    path = 'fits_files/'
    src_name = st.session_state['selected_source']['Source'].values[0]
    dist = st.session_state['selected_source']['Distance'].values[0]
    vsys = st.session_state['selected_source']['v_sys'].values[0]
    cont_rms = st.session_state['selected_source']['cont_rms'].values[0]

    col1, col2 = st.columns([0.7, 0.3])
    col1.markdown("<h1 style='text-align: center;'>%s</h1>" %(src_name), unsafe_allow_html=True)
    col2.image('eDisk_logo_ver.4.jpg')

    col1.markdown(st.session_state['selected_source']['Description'].values[0])

    source_path = path + '%s/' %src_name
    
    #cont_image = source_path + '%s_SBLB_continuum_robust_2.0.pbcor.tt0.fits' %(src_name)
    #sky_region = Regions.read(source_path + '%s_rms.crtf' %(src_name), format='crtf')[0]
    
    mom8_imgs = glob.glob(source_path+'*robust_2.0_mom8_15arcsec.fits')
    mom9_imgs = glob.glob(source_path+'*robust_2.0_mom9_15arcsec.fits')

    
    #col2.subheader('Continuum Plot of %s' %(src_name))
    #col2.markdown("<h1 style='text-align: center; color: black;'>Continuum plot of %s</h1>" %(src_name), unsafe_allow_html=True)
    #fig1 = plt.figure(figsize=(7,7))
    #ra, dec, gc1, cont_hdr, cont_rms = plot_continuum(fig1, cont_image, sky_region, dist)
    #gc1.colorbar.set_axis_label_text(cont_hdr['bunit'])

    mol=st.sidebar.selectbox('Select the molecule:',molecules)
    mom8_idx = [i for i, s in enumerate(mom8_imgs) if mol in s][0]
    mom9_idx = [i for i, s in enumerate(mom9_imgs) if mol in s][0]
    mom8_img = mom8_imgs[mom8_idx]
    mom9_img = mom9_imgs[mom9_idx]

    col1, col2 = st.columns([0.3, 0.7])
    zoom=col1.slider('Select Zoom Level (RA/Dec square size in arcsecs):', 2, 15, 15, 1)
    fig2 = plt.figure(figsize=(7,7))
    ra, dec, gc2, mom8_hdr = plot_mom_map(fig2, mom8_img, dist, cmap_val='Spectral_r')
    fig3 = plt.figure(figsize=(7,7))
    ra2, dec2, gc3, mom9_hdr = plot_mom_map(fig3, mom9_img, dist, cmap_val='RdBu_r', v_sys=vsys)

    col2,col3 = st.columns(2)

    #with col1:
    #    st.markdown("<h3 style='text-align: center;'>Continuum plot of %s</h3>" %(src_name), unsafe_allow_html=True)
    #    gc1.recenter(x=ra,y=dec, width=(zoom/3600.0),height=(zoom/3600.0))
    #    st.pyplot(fig1)
    with col2:
        st.markdown("<h3 style='text-align: center;'>Moment 8 map of %s</h3>" %(mol), unsafe_allow_html=True)
        gc2.recenter(x=ra,y=dec, width=(zoom/3600.0),height=(zoom/3600.0))
        gc2.colorbar.set_axis_label_text(mom8_hdr['bunit'])
        st.pyplot(fig2)
    with col3:
        st.markdown("<h3 style='text-align: center;'>Moment 9 map of %s</h3>" %(mol), unsafe_allow_html=True)
        gc3.recenter(x=ra2,y=dec2, width=(zoom/3600.0),height=(zoom/3600.0))
        gc3.colorbar.set_axis_label_text(mom9_hdr['bunit'])
        st.pyplot(fig3)
    
    display_footer()

    #except:
    #    st.markdown('# Plots for this source coming soon!!')

    #    display_footer()

if __name__=='__main__':
    main()