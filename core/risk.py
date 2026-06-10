def level(score):
    if score < 20: return 'Safe'
    if score < 40: return 'Low'
    if score < 60: return 'Medium'
    if score < 85: return 'High'
    return 'Critical'

def recommendations(score):
    if score >= 85: return ['Do not click or reply','Block sender/domain','Report to cyber cell or IT team','Change passwords if already interacted']
    if score >= 60: return ['Verify through official website/app','Do not share OTP/password','Ask sender through another channel']
    if score >= 40: return ['Proceed carefully','Check URL spelling and sender identity']
    return ['No major red flags found','Still avoid sharing sensitive information unnecessarily']
