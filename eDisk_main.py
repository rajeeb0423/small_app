import streamlit as st
from st_pages import Page, show_pages
import pandas as pd
import numpy as np
from streamlit_extras.switch_page_button import switch_page
import plotly.express as px

def display_footer():
    st.divider()
    footer = st.container()
    with footer:
        st.markdown("<h1 style='text-align: Right; color: #808080;'>Made By:</h1>", unsafe_allow_html=True)
        st.markdown("""<p style='text-align: Right; color: #808080;'>Rajeeb Sharma, PhD fellow<br>
                    Niels Bohr Institute, University of Copenhagen<br>
                    <a href='mailto:rajeeb.sharma@nbi.ku.dk'>rajeeb.sharma@nbi.ku.dk</a>
                    </p>""", unsafe_allow_html=True)

def displaypage():

    st.set_page_config(page_title= 'eDisk Overview', page_icon='eDisk_logo_ver.4.jpg', initial_sidebar_state="collapsed", layout='wide')

    show_pages([Page("eDisk_main.py","Main"),
                Page("plot_spectral_lines.py","Plot")])

    st.markdown(
        """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        [data-testid="stMainMenu"] {
            display: none
        }
    </style>
    """,unsafe_allow_html=True)

    eDisk_df = pd.read_csv('eDisk_sources_overview.csv', sep=',')

    col1, col2 = st.columns([0.7, 0.3])
    col1.markdown('# The eDisk program')
    col2.image('eDisk_logo_ver.4.jpg')

    st.markdown(':red[***When do substructures start to develop in disks?***]') 
    st.markdown('''In order to investigate the possibility of early planet formation, 
                it is obviously necessary for us to investigate disks around Class
                0/I protostars. To this end, an ALMA Large Program was conducted
                titled “Early Planet Formation in Embedded Disks (eDisk),” in which 
                19 Class 0/I embedded protostars in nearby star-forming regions
                were systematically surveyed at resolutions of ∼5 au (0.04") for
                the first time. 
                The main scientific objective of the eDisk
                program is to investigate whether or not substructures exist in
                disks around embedded, Class 0/I protostars that might be
                indicative of early planet formation.''')

    col1, col2 = st.columns(2)

    col1.dataframe(eDisk_df, use_container_width=True, 
                hide_index=True, height=380,
                column_config={'RA': 'R.A. (hh:mm:ss)', 'Dec': 'Dec. (dd:mm:ss)',                  
                                'Distance': 'Distance (pc)', 'T_bol': 'T_bol (K)', 
                                'L_bol': 'L_bol (L_sun)', 'v_sys': None, 'cont_rms': None, 'Description': None})
    
    fig = px.scatter(eDisk_df, x='T_bol', y='L_bol', labels={
                     "T_bol": 'T<sub>bol</sub> (K)',
                     "L_bol": 'L<sub>bol</sub> (L<sub>&#x2299;</sub>)'},
                     title='L<sub>bol</sub> vs T<sub>bol</sub> diagram of the eDisk sources',
                     log_x=True, log_y=True, range_x=[10,1000], range_y=[0.1,100],
                     hover_data={'Source': True,
                                 'T_bol': True,
                                 'L_bol': True},
                     width=900, height=450)
    
    fig.add_annotation(dict(x=np.log10(30),y=np.log10(70),text="<b>Class 0</b>",showarrow=False,font_size=20))
    fig.add_annotation(dict(x=np.log10(200),y=np.log10(70),text="<b>Class I</b>",showarrow=False,font_size=20))
    fig.update_xaxes(dtick=1, showgrid=True, minor_griddash="dot", ticks='outside', showline=True, mirror=True, tickcolor='black')
    fig.update_yaxes(dtick=1, showgrid=True, minor_griddash="dot", ticks='outside', showline=True, mirror=True, tickcolor='black')
    fig.update_layout(title_x=0.4)
    fig.add_vline(x=70, line_dash='dash')
    fig.add_vline(x=650, line_dash='dash')
    col2.plotly_chart(fig, use_container_width=True)

    st.markdown('### Select a source to view:')
    col1,col2 = st.columns([0.3,0.7])
    with col1:
        with st.form("source"):
            selected_src = st.selectbox('select_source', eDisk_df, label_visibility='hidden')
            btnSubmit = st.form_submit_button(label='Submit')

    st.session_state['selected_source'] = eDisk_df.loc[eDisk_df['Source'] == selected_src]
    st.session_state['zoom_only'] = False

    display_footer()

    if btnSubmit:
        switch_page('Plot')

if __name__ == '__main__':
    displaypage()