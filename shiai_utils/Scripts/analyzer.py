# This script loads exported JSON from Judo Shiai,
# removes duplicates (I prefer to copy competitors when it comes to friendly matches)
# and counts competitors per categories and clubs, as well as number of needed medals

# currently outputs to terminal, consider outputing to file instead
# another consideration, I could extract this from shiai using sql querries (prbly better idea)

# Lot of things are written really badly. 
# I was creating it at hand per parts of what was required at the moment
# and it's sewed together in a way it works. And I cant be bothered rewriting it just now.
# So dont judge me. Or you know what, do.

import pandas as pd
import json


with open('Susice.txt', 'r', encoding="utf8") as f:
    string = f.read()
    
    # Remove 'ISODate(', ')' is it necesarry??
    string = string.replace('ISODate(', '')
    string = string.replace(')', '')

    ff = json.loads(string)
    frame = pd.DataFrame(ff)

print(frame)
print('All contestants: ' + str(len(frame.index)))  
print('') 

frame_non_duplicates = frame.drop_duplicates(subset=['id'])
print('Without duplicates: ' + str(len(frame_non_duplicates.index)))  
print('') 

# Get all clubs
clubs = frame_non_duplicates['club']
clubs.drop_duplicates(inplace = True)
clubs = clubs.reset_index(drop = True)

print('Categories:')
kats = frame_non_duplicates['category']
kats.drop_duplicates(inplace=True)
kats = kats.reset_index(drop=True)
kats.sort_values()

m16 = 0
m14 = 0
w16 = 0
w14 = 0
m12 = 0
w12 = 0
u10 = 0

gold = 0
silver = 0
bronze = 0
u14_med = [0,0,0] # this was for specific use case, should be rewritten for all cats
u16_med = [0,0,0]
for kat in kats:
    filt = (frame_non_duplicates['category'] == kat)
    df = frame_non_duplicates.loc[filt]
    if len(df.index) >= 4:
        cnt = 4
    else:
        cnt = len(df.index)
    print(kat, ':', len(df.index))
    gold += 1
    if not len(df.index) < 2:
        silver += 1
    if not len(df.index) < 3:
        bronze += 1
    if not len(df.index) < 6:
        bronze += 1
    
    if '16' in str(kat):
        u16_med[0] += 1
        if not len(df.index) < 2:
            u16_med[1] += 1
        if not len(df.index) < 3:
            u16_med[2] += 1
        if not len(df.index) < 6:
            u16_med[2] += 1 

    if '14' in str(kat):
        u14_med[0] += 1
        if not len(df.index) < 2:
            u14_med[1] += 1
        if not len(df.index) < 3:
            u14_med[2] += 1
        if not len(df.index) < 6:
            u14_med[2] += 1 

    if str(kat).startswith('MU16'):
        m16 += len(df.index)
    elif str(kat).startswith('WU16'):
        w16 += len(df.index)
    elif str(kat).startswith('MU14'):
        m14 += len(df.index)
    elif  str(kat).startswith('WU14'):
        w14 += len(df.index)
    elif str(kat).startswith('MU12'):
        m12 += len(df.index)
    elif  str(kat).startswith('WU12'):
        w12 += len(df.index)
    elif  str(kat).startswith('U10'):
        u10 += len(df.index)

    #print(str(kat) + ': ' + str(cnt))

print('')
print('U10: ' + str(u10))
print('MU12: ' + str(m12) + ' WU12: ' + str(w12))
print('MU14: ' + str(m14) + ' WU14: ' + str(w14))
print('MU16: ' + str(m16) + ' WU16: ' + str(w16))
print('')

# Print number of competitors in clubs
test_sum = 0
for club in clubs:
    filt = (frame_non_duplicates['club'] == club)
    df = frame_non_duplicates.loc[filt]
    print(str(club) + ': ' + str(len(df.index)))
    test_sum += len(df.index)
print('Controll count of competitors: ' + str(test_sum))
print('') 

# Print number of clubs:
print('Clubs:')
print(len(clubs.index))

print('Medals:')
print('Bronze: ', bronze)
print('Silver: ', silver)
print('Gold: ', gold)
print()

print('U14: G S B')
print(u14_med[0], ' ', u14_med[1], ' ', u14_med[2])

print('U16: G S B')
print(u16_med[0], ' ', u16_med[1], ' ', u16_med[2])
print()

# Print collected fees per club
print('Fees:')
fee = 300;
test_sum = 0
for club in clubs:
    filt = (frame_non_duplicates['club'] == club)
    df = frame_non_duplicates.loc[filt]
    print(str(club) + ': ' + str(len(df.index)*fee))
    test_sum += len(df.index)*fee
print('Collected controll sum: '+ str(test_sum))