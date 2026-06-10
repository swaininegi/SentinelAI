from urllib.parse import urlparse
import re, math
from difflib import SequenceMatcher
from .risk import level
BRANDS=['google','facebook','instagram','whatsapp','amazon','netflix','paypal','sbi','hdfc','icici','axis','yono','microsoft','apple','flipkart']
SUSP=['login','verify','account','secure','update','bank','kyc','password','otp','free','gift','claim','urgent','suspended','alert','limited','winner']
SHORT=['bit.ly','tinyurl.com','t.co','goo.gl','cutt.ly','is.gd','ow.ly']
BAD_TLDS=['.xyz','.top','.tk','.ml','.ga','.cf','.gq','.ru','.cn','.work','.click','.rest','.zip']

def scan_url(url):
    raw=url.strip(); u=raw if raw.startswith(('http://','https://')) else 'http://'+raw
    p=urlparse(u); host=p.netloc.lower(); path=(p.path+'?'+p.query).lower(); text=(host+path).lower()
    score=0; reasons=[]
    if not raw.startswith('https://'):
        score+=18; reasons.append('Connection is not HTTPS encrypted')
    if len(raw)>75:
        score+=12; reasons.append('URL is unusually long')
    if any(k in text for k in SUSP):
        hits=[k for k in SUSP if k in text][:6]; score+=min(30,6*len(hits)); reasons.append('Suspicious intent keywords: '+', '.join(hits))
    if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', host):
        score+=25; reasons.append('Uses IP address instead of trusted domain')
    if any(s in host for s in SHORT): score+=20; reasons.append('Uses a shortened URL service')
    if any(host.endswith(t) for t in BAD_TLDS): score+=15; reasons.append('Uses a high-risk or uncommon top-level domain')
    if '@' in raw: score+=20; reasons.append('Contains @ symbol which can hide real destination')
    if raw.count('-')>=3 or raw.count('.')>=5: score+=10; reasons.append('Excessive separators/subdomains detected')
    for b in BRANDS:
        if b in host: continue
        for token in re.split('[.-]', host):
            if SequenceMatcher(None, token, b).ratio()>0.78 and token!=b:
                score+=22; reasons.append(f'Possible typosquatting of {b}: {token}'); break
    score=min(100,score)
    if not reasons: reasons=['No major URL red flags detected']
    return {'score':score,'level':level(score),'reasons':reasons,'host':host}
