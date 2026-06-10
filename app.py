import streamlit as st, pandas as pd, numpy as np, time, random, base64
import plotly.graph_objects as go, plotly.express as px
from core.database import init_db, log_scan, get_scans, stats
from core.url_scanner import scan_url
from core.message_scanner import scan_message
from core.deepfake import image_scan, video_scan, audio_scan
from core.report import make_pdf
from core.risk import recommendations

st.set_page_config(page_title='SentinelAI Ultra Pro', page_icon='🛡️', layout='wide', initial_sidebar_state='expanded')
init_db()

CSS='''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap');
:root{--primary:#00E5FF;--secondary:#00FF9D;--danger:#FF3D71;--bg:#050816;--card:#0B1221;}
html,body,[class*="css"]{font-family:Inter,sans-serif;background:#050816;color:#EAF8FF;}
.stApp{background: radial-gradient(circle at 15% 10%, rgba(0,229,255,.18), transparent 25%), radial-gradient(circle at 85% 20%, rgba(0,255,157,.14), transparent 23%), linear-gradient(135deg,#050816,#070b18 50%,#03040b);}
.stApp:before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(0,229,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.07) 1px,transparent 1px);background-size:42px 42px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.7),transparent);pointer-events:none;animation:grid 12s linear infinite;}@keyframes grid{from{background-position:0 0}to{background-position:42px 42px}}
.hero{padding:44px;border:1px solid rgba(0,229,255,.35);border-radius:28px;background:linear-gradient(145deg,rgba(11,18,33,.88),rgba(0,229,255,.08));box-shadow:0 0 55px rgba(0,229,255,.16);position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-80px;top:-80px;width:280px;height:280px;border-radius:50%;background:conic-gradient(#00E5FF,#00FF9D,#FF3D71,#00E5FF);filter:blur(18px);opacity:.22;animation:spin 7s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.title{font-size:60px;font-weight:900;line-height:1.02;background:linear-gradient(90deg,#fff,#00E5FF,#00FF9D);-webkit-background-clip:text;color:transparent}.subtitle{font-size:20px;color:#B6C7D9;max-width:900px}.badge{display:inline-block;border:1px solid rgba(0,229,255,.45);background:rgba(0,229,255,.09);border-radius:999px;padding:8px 14px;color:#91F4FF;font-weight:700;margin:4px}.card{background:rgba(11,18,33,.78);border:1px solid rgba(0,229,255,.23);border-radius:22px;padding:24px;box-shadow:0 12px 40px rgba(0,0,0,.28);backdrop-filter:blur(18px);transition:.25s}.card:hover{transform:translateY(-4px);box-shadow:0 0 35px rgba(0,229,255,.25)}
.metric{font-size:36px;font-weight:900;color:#00E5FF}.label{color:#9FB3C8;font-size:13px;text-transform:uppercase;letter-spacing:1px}.danger{color:#FF3D71}.safe{color:#00FF9D}.warn{color:#FFCE54}.small{color:#9FB3C8;font-size:14px}.stButton>button{background:linear-gradient(90deg,#00E5FF,#00FF9D)!important;color:#02040A!important;border:0!important;border-radius:14px!important;font-weight:900!important;padding:.75rem 1.2rem!important;box-shadow:0 0 22px rgba(0,229,255,.35)}
section[data-testid="stSidebar"]{background:rgba(5,8,22,.92);border-right:1px solid rgba(0,229,255,.22)}
.alert{border-left:4px solid #FF3D71;background:rgba(255,61,113,.08);padding:16px;border-radius:14px}.ok{border-left:4px solid #00FF9D;background:rgba(0,255,157,.08);padding:16px;border-radius:14px}
.pulse{animation:pulse 1.4s infinite}@keyframes pulse{0%{opacity:.55}50%{opacity:1}100%{opacity:.55}}
</style>'''
st.markdown(CSS, unsafe_allow_html=True)

def gauge(score,title='Risk Score'):
    color='#00FF9D' if score<40 else '#FFCE54' if score<70 else '#FF3D71'
    fig=go.Figure(go.Indicator(mode='gauge+number', value=score, number={'suffix':'/100','font':{'color':'white','size':34}}, title={'text':title,'font':{'color':'white'}}, gauge={'axis':{'range':[0,100],'tickcolor':'white'},'bar':{'color':color},'bgcolor':'rgba(0,0,0,0)','bordercolor':'rgba(0,229,255,.4)','steps':[{'range':[0,40],'color':'rgba(0,255,157,.18)'},{'range':[40,70],'color':'rgba(255,206,84,.18)'},{'range':[70,100],'color':'rgba(255,61,113,.18)'}]}))
    fig.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20,r=20,t=40,b=10))
    return fig

def card(label,value,cls=''):
    st.markdown(f"<div class='card'><div class='label'>{label}</div><div class='metric {cls}'>{value}</div></div>", unsafe_allow_html=True)

def report_button(title,stype,inp,score,level,explanation):
    path=make_pdf(title,stype,inp,score,level,explanation)
    with open(path,'rb') as f: st.download_button('📄 Download Professional PDF Report', f, file_name='SentinelAI_Report.pdf', mime='application/pdf')

page=st.sidebar.radio('🛡️ SentinelAI Command Center',['Home','URL Scanner','Message Scanner','Deepfake Lab','SOC Dashboard','Education Hub','AI Security Chatbot','Future of AI Security','Admin Panel'])
st.sidebar.markdown('---')
st.sidebar.markdown('### Live System')
st.sidebar.markdown('<span class="pulse">●</span> AI Engine Online', unsafe_allow_html=True)
st.sidebar.markdown('Threat DB: Active  |  Privacy Mode: Local')

if page=='Home':
    st.markdown("""<div class='hero'><span class='badge'>AI SECURITY MVP</span><span class='badge'>PHISHING</span><span class='badge'>SCAM</span><span class='badge'>DEEPFAKE</span><div class='title'>Defending Digital Trust with Artificial Intelligence</div><p class='subtitle'>Real-time protection against phishing, scams, deepfakes, malicious websites and social engineering attacks. Built as a professional startup-grade SOC platform for hackathon demonstration.</p></div>""", unsafe_allow_html=True)
    a,b,c,d=st.columns(4); s=stats()
    with a: card('Live Threat Signals', f"{random.randint(42000,98000):,}")
    with b: card('Total Scans', s['total'])
    with c: card('Threats Found', s['threats'],'danger')
    with d: card('AI Modules', '5+')
    st.markdown('### 🚀 Platform Capabilities')
    cols=st.columns(3)
    features=[('🔗 Phishing URL Intelligence','Detect fake domains, typosquatting, insecure links and brand impersonation.'),('💬 Scam Message AI','Find OTP fraud, KYC scams, urgency, fear tactics and social engineering.'),('🎭 Deepfake Lab','Analyze images, videos and audio using offline forensic heuristics.'),('📊 SOC Dashboard','Investor-style cyber command center with analytics and threat trends.'),('📄 PDF Reports','Export professional scan reports with explanation and recommendations.'),('🤖 Security Chatbot','Cyber awareness assistant for phishing and privacy guidance.')]
    for i,(t,x) in enumerate(features):
        with cols[i%3]: st.markdown(f"<div class='card'><h3>{t}</h3><p class='small'>{x}</p></div>", unsafe_allow_html=True)

elif page=='URL Scanner':
    st.markdown('## 🔗 Phishing URL Detector')
    url=st.text_input('Paste a URL for AI threat analysis', 'http://paypal-login-verification-security.xyz')
    if st.button('Start URL Analysis'):
        with st.spinner('SentinelAI is inspecting SSL, domain patterns, typosquatting and phishing intent...'):
            time.sleep(1); r=scan_url(url); log_scan('URL',url,r['score'],r['level'],'; '.join(r['reasons']))
        c1,c2=st.columns([1,1])
        with c1: st.plotly_chart(gauge(r['score']), use_container_width=True)
        with c2:
            st.markdown(f"<div class='card'><h2>Threat Level: <span class='{'danger' if r['score']>=60 else 'safe'}'>{r['level']}</span></h2><p>Host: <b>{r['host']}</b></p></div>", unsafe_allow_html=True)
            for reason in r['reasons']: st.markdown(f"<div class='alert'>⚠️ {reason}</div>", unsafe_allow_html=True)
        st.plotly_chart(px.pie(values=[r['score'],100-r['score']], names=['Risk','Trust'], hole=.62, title='URL Risk Composition'), use_container_width=True)
        report_button('URL Threat Scan','URL',url,r['score'],r['level'],'; '.join(r['reasons']))

elif page=='Message Scanner':
    st.markdown('## 💬 Scam Message Scanner')
    msg=st.text_area('Paste SMS / WhatsApp / Email content', 'URGENT: Your bank account will be blocked within 24 hours. Verify immediately and share OTP at http://secure-bank-login.xyz', height=160)
    if st.button('Analyze Message'):
        with st.spinner('Detecting urgency, fear tactics, credential theft and social engineering...'):
            time.sleep(1); r=scan_message(msg); log_scan('Message',msg,r['score'],r['level'],str(r['found']))
        st.plotly_chart(gauge(r['score'],'Scam Probability'), use_container_width=True)
        st.markdown(f"<div class='card'><h2>Classification: <span class='{'danger' if r['score']>=60 else 'safe'}'>{r['level']}</span></h2><p>{r['explanation']}</p></div>", unsafe_allow_html=True)
        if r['found']:
            for cat,hits in r['found'].items(): st.markdown(f"<div class='alert'><b>{cat}</b>: {', '.join(hits)}</div>", unsafe_allow_html=True)
        else: st.markdown("<div class='ok'>No major scam indicators detected.</div>", unsafe_allow_html=True)
        report_button('Scam Message Scan','Message',msg,r['score'],r['level'],str(r['found']))

elif page=='Deepfake Lab':
    st.markdown('## 🎭 Deepfake Detection Lab')
    tab1,tab2,tab3=st.tabs(['Image Deepfake','Video Deepfake','Voice Deepfake'])
    with tab1:
        f=st.file_uploader('Upload face/image file', type=['png','jpg','jpeg'])
        if f:
            c1,c2=st.columns(2); c1.image(f, caption='Uploaded media', use_container_width=True)
            r=image_scan(f); log_scan('Deepfake Image',f.name,r['score'],'High' if r['score']>65 else 'Medium' if r['score']>40 else 'Low',r['explanation'])
            c2.plotly_chart(gauge(r['score'],'Deepfake Probability'), use_container_width=True)
            st.image(r['heatmap'], caption='Forensic edge heatmap visualization')
            st.write(r['explanation']); report_button('Deepfake Image Analysis','Image',f.name,r['score'],'Deepfake Risk',r['explanation'])
    with tab2:
        f=st.file_uploader('Upload video file', type=['mp4','mov','avi'])
        if f:
            r=video_scan(f); log_scan('Deepfake Video',f.name,r['score'],'High' if r['score']>65 else 'Medium',r['explanation'])
            st.plotly_chart(gauge(r['score'],'Video Fake Probability'), use_container_width=True)
            st.line_chart(pd.DataFrame({'Frame Risk':r['timeline']})); st.write(r['explanation'])
            report_button('Deepfake Video Analysis','Video',f.name,r['score'],'Video Risk',r['explanation'])
    with tab3:
        f=st.file_uploader('Upload voice/audio file', type=['wav','mp3','m4a','ogg'])
        if f:
            r=audio_scan(f); log_scan('Deepfake Voice',f.name,r['score'],'High' if r['score']>65 else 'Medium',r['explanation'])
            st.plotly_chart(gauge(r['score'],'AI Voice Probability'), use_container_width=True)
            st.progress(r['human']/100, text=f"Human voice likelihood: {r['human']}%"); st.write(r['explanation'])
            report_button('Deepfake Voice Analysis','Audio',f.name,r['score'],'Voice Risk',r['explanation'])

elif page=='SOC Dashboard':
    st.markdown('## 📊 Threat Intelligence SOC Dashboard')
    s=stats(); a,b,c,d=st.columns(4)
    with a: card('Total Scans',s['total'])
    with b: card('Threats Found',s['threats'],'danger')
    with c: card('Safe Content',s['safe'],'safe')
    with d: card('Critical Alerts',s['critical'],'danger')
    rows=get_scans(); df=pd.DataFrame(rows, columns=['Type','Input','Score','Level','Explanation','Time'])
    if not df.empty:
        st.plotly_chart(px.histogram(df,x='Type',color='Level',title='Attack Category Distribution'), use_container_width=True)
        st.plotly_chart(px.line(df.iloc[::-1], y='Score', title='Threat Trend Over Time'), use_container_width=True)
        st.dataframe(df, use_container_width=True)
    else: st.info('Run scans to populate the SOC dashboard.')
    coords=pd.DataFrame({'lat':[28.6,22.5,19.0,12.9,51.5,40.7,35.6],'lon':[77.2,88.3,72.8,77.5,-0.1,-74,139.6],'threat':[80,45,65,35,70,55,60]})
    st.map(coords, size='threat')

elif page=='Education Hub':
    st.markdown('## 🎓 Cyber Security Education Hub')
    tips=['Never share OTP, PIN or password with anyone.','Check domain spelling before login.','Do not trust urgent money requests from new numbers.','Use official apps for banking/KYC.','Deepfake calls can imitate family or seniors; verify through another channel.','Enable 2FA on email, banking and social media.']
    for t in tips: st.markdown(f"<div class='card'>🛡️ {t}</div>", unsafe_allow_html=True)

elif page=='AI Security Chatbot':
    st.markdown('## 🤖 AI Security Chatbot')
    q=st.chat_input('Ask about phishing, scam, deepfake, privacy...')
    if 'chat' not in st.session_state: st.session_state.chat=[]
    if q:
        ans='I recommend verifying the sender, checking URLs carefully, avoiding OTP/password sharing, and using official apps. For deepfakes, inspect unnatural eye movement, over-smooth skin, audio mismatch and verify identity through another trusted channel.'
        if 'phishing' in q.lower(): ans='Phishing is a fake message or website designed to steal credentials. Check HTTPS, exact domain spelling, urgency language, and never login through unknown links.'
        if 'deepfake' in q.lower(): ans='Deepfakes often show inconsistent lighting, strange eye reflections, lip-sync mismatch, robotic audio, or overly smooth facial texture.'
        st.session_state.chat.append((q,ans))
    for u,a in st.session_state.chat:
        st.chat_message('user').write(u); st.chat_message('assistant').write(a)

elif page=='Future of AI Security':
    st.markdown('## 🌐 Future of AI Security')
    st.markdown("<div class='hero'><div class='title'>Autonomous AI Threat Hunting</div><p class='subtitle'>A simulated cyber warfare command view showing how SentinelAI can evolve into enterprise-scale AI protection.</p></div>", unsafe_allow_html=True)
    progress=st.progress(0, text='Live attack simulation')
    for i in range(0,101,20): time.sleep(.08); progress.progress(i, text=f'Analyzing global threat stream... {i}%')
    st.success('Simulation complete: phishing cluster blocked, deepfake campaign flagged, identity fraud risk reduced.')
    st.plotly_chart(go.Figure(data=[go.Scatterpolar(r=[90,75,82,68,88],theta=['Phishing','Scam','Image Fake','Voice Fake','SOC'],fill='toself')]).update_layout(paper_bgcolor='rgba(0,0,0,0)',font_color='white'), use_container_width=True)

elif page=='Admin Panel':
    st.markdown('## 🔐 Admin Panel')
    p=st.text_input('Password', type='password')
    if p=='sentinel@2026':
        s=stats(); st.success('Admin access granted')
        c1,c2,c3=st.columns(3)
        with c1: card('Total Users','Demo Mode')
        with c2: card('Total Scans',s['total'])
        with c3: card('Critical Alerts',s['critical'],'danger')
        st.dataframe(pd.DataFrame(get_scans(), columns=['Type','Input','Score','Level','Explanation','Time']), use_container_width=True)
    elif p: st.error('Wrong password')
