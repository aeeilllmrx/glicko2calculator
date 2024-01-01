"""
glicko2calculator.py

A streamlit web app used to calculate glicko2 rating between two players.

"""

__version__ = '1.2.1'
__author__ = 'fsmosca'
__script_name__ = 'glicko2calculator'
__about__ = 'A streamlit web app used to calculate glicko2 rating between two players.'


from glicko2 import Glicko2
import streamlit as st


st.set_page_config(
    page_title="Glicko v2 Rating Calculator",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={'about': f'[Glicko v2 Rating Calculator v{__version__}](https://github.com/fsmosca/glicko2calculator)'}
)


Z_SCORES = {'90%': 1.645, '95%': 1.96, '99%': 2.576}


if 'vola1' not in st.session_state:
    st.session_state.vola1 = 0.06
if 'vola2' not in st.session_state:
    st.session_state.vola2 = 0.06

if 'tau' not in st.session_state:
    st.session_state.tau = 0.5
if 'rating1' not in st.session_state:
    st.session_state.rating1 = 1500
if not 'rating2' in st.session_state:
    st.session_state.rating2 = 1500
if not 'rd1' in st.session_state:
    st.session_state.rd1 = 350
if not 'rd2' in st.session_state:
    st.session_state.rd2 = 350


def data_input(num):
    st.markdown(f'''
    ##### Player #{num}
    ''')
    st.number_input(
        label='Rating',
        min_value=500,
        max_value=5000,
        key=f'rating{num}'
    )
    st.number_input(
        label='Rating Deviation',
        min_value=0,
        max_value=350,
        key=f'rd{num}'
    )
    st.number_input(
        label='Rating Volatility',
        min_value=0.001,
        max_value=1.,
        step=0.00001,
        format="%.8f",
        key=f'vola{num}'
    )

def rating_update(p, num, confidence_level):
    lower_rating = round(p.mu - Z_SCORES[confidence_level]*p.phi)
    upper_rating = round(p.mu + Z_SCORES[confidence_level]*p.phi)
                    
    st.markdown(f'''
    ##### New Rating: :green[{round(p.mu)}]
    New RD: **{round(p.phi)}**  
    New Volatility: **{round(p.sigma, 8)}**  
    Gain: **{round(p.mu - st.session_state[f'rating{num}'], 2):+0.2f}**  
    Rating Interval: **[{lower_rating}, {upper_rating}]**
    ''')


def main():
    st.header('Glicko v2 Rating Calculator')

    calculation_tab, setting_tab, credits_tab = st.tabs(
        [':chart: CALCULATION', ':hammer_and_wrench: SETTING', ':heavy_dollar_sign: CREDITS'])

    with setting_tab:
        st.slider(
            label='Input TAU',
            min_value=0.1,
            max_value=3.0,
            key='tau',
            help='''Smaller values prevent the volatility measures
            from changing by large amounts which in turn prevents enormous
            changes in ratings based on very imporbable results'''
        )

        confidence_level = st.selectbox(
            'Confidence Level',
            options=['90%', '95%', '99%'],
            index=1,
            key='confidence_level_k'
        )

    with calculation_tab:
        col1, col2 = st.columns(2)
        with col1:
            data_input(1)
        with col2:
            data_input(2)

        result = st.selectbox(
            label=':triangular_flag_on_post: Select result',
            options=['#1 wins', '#2 wins', 'draw'],
        )                      

        env = Glicko2(tau=float(st.session_state.tau))
        r1 = env.create_rating(st.session_state.rating1, st.session_state.rd1, st.session_state.vola1)
        r2 = env.create_rating(st.session_state.rating2, st.session_state.rd2, st.session_state.vola2)

        p = [None, None]
        if result == '#1 wins':
            p[0], p[1] = env.rate_1vs1(r1, r2, drawn=False)
        elif result == '#2 wins':
            p[1], p[0] = env.rate_1vs1(r2, r1, drawn=False)
        else:
            p[0], p[1] = env.rate_1vs1(r1, r2, drawn=True)

        for i, col in enumerate(st.columns(len(p))):
            with col:
                rating_update(p[i], i+1, confidence_level)

    with credits_tab:
        st.markdown('''
        [Mark Glickman](http://www.glicko.net/glicko.html)  
        [Sublee Glicko2 Library](https://github.com/sublee/glicko2)  
        [Streamlit](https://streamlit.io/)
        ''')


if __name__ == '__main__':
    main()
