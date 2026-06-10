import re
from .risk import level
CATS={
'Urgency':['urgent','immediately','within 24 hours','now','today','limited time','10 minutes','blocked','terminated'],
'Credential Theft':['otp','password','pin','cvv','aadhaar','pan','kyc','login','verify','bank details'],
'Reward Scam':['won','winner','lottery','prize','gift card','free money','cashback','claim'],
'Fear/Threat':['legal action','suspended','blocked','arrest','penalty','account closed','security alert'],
'Social Engineering':['do not inform','confidential','new number','transfer money','boss','ceo','mom','dad']
}

def scan_message(msg):
    m=msg.lower(); score=0; found={}; flags=[]
    for cat,words in CATS.items():
        hits=[w for w in words if w in m]
        if hits:
            found[cat]=hits; score+=min(25,8*len(hits)); flags+=hits
    if re.search(r'https?://|www\.',m): score+=18; found.setdefault('External Link',[]).append('link present')
    if re.search(r'₹|rs\.?\s?\d+|\d{4,}',m): score+=8; found.setdefault('Money/Number Pressure',[]).append('amount or code detected')
    if msg.count('!')>=2: score+=6; found.setdefault('Tone',[]).append('excessive exclamation')
    score=min(100,score)
    return {'score':score,'level':level(score),'found':found,'flags':list(dict.fromkeys(flags)),'explanation':'The model checks urgency, fear, reward bait, credential theft and social engineering patterns.'}
