
def check(input):
    ''' Return unicode checkbox for a boolean '''
    if input == 'True':
        return '&#x2611;'  # 'BALLOT BOX WITH CHECK'
    else:
        return '&#x2612;'  # 'BALLOT BOX WITH X'

