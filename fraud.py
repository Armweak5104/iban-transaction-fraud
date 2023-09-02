import pandas as pd
import numpy as np
import time
import csv 
import re


df = pd.read_csv('competition_dataset.csv')
currencies = open('deposits-swift.csv','r')
reader = csv.reader(currencies)
iso_codes = []
for line in reader:
    if line[2]:
        if len(line[2]) == 4:
            iso_codes.append(line[2].strip())

# frauds = pd.read_fwf('train_fraud_ids_list.txt', header = None)
# df['Fraudulent'] = False

# for i in frauds[0]:
#     df.loc[i,'Fraudulent'] = True
    

# train_frauds = df.sort_values('Fraudulent', ascending = False)[:frauds.shape[0]-10]
# test_frauds = df.sort_values('Fraudulent', ascending = False)[frauds.shape[0]-9:frauds.shape[0]]

# train_frauds['detected'] = False
# test_frauds['detected'] = False



letter_dic = {"A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "I": 18, "J": 19, "K": 20,
              "L": 21, "M": 22, "N": 23, "O": 24, "P": 25, "Q": 26, "R": 27, "S": 28, "T": 29, "U": 30, "V": 31,
              "W": 32, "X": 33, "Y": 34, "Z": 35,
              "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9}

letters = {ord(k): str(v) for k, v in letter_dic.items()}

def chech_validation_chars_iban(iban):
    zeros_iban = iban[:2] + '00' + iban[4:]
    iban_inverted = zeros_iban[4:] + zeros_iban[:4]
    iban_numbered = iban_inverted.translate(letters)

    verification_chars = 98 - (int(iban_numbered) % 97)

    if verification_chars < 10:
        verification_chars = '{:02}'.format(int(verification_chars))
    return verification_chars


def validate_iban(iban):
    iban_inverted = iban[4:] + iban[:4]
    iban_numbered = iban_inverted.translate(letters)

    if int(iban_numbered) % 97 == 1:
        return False
    else:
        return True

invalid_domains = ["nx1.us",
"innoberg.com",
"pickuplanet.com",
"816qs.com",
"hansenhu.com",
"playfunplus.com",
"cggup.com",
"masjoco.com",
"bizisstance.com",
"salvatorelli.it",
"mobilebankapp.org",
"gmailwe.com",
"kwontol.com",
"apaylofinance.com"]

def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

def transfer_amt(df):
    df3 = df.loc[(df['type'] == 'TRANSFER') & ((df['amount'] < 25) | (df['amount'] >1000000))] 
    df4 = df.loc[(df['type'] == 'PAYMENT') & ((df['amount'] < 25) | (df['amount'] >1000000))]
    df5 = df.loc[(df['type'] == 'CASH-IN') & ((df['amount'] < 1) | (df['amount'] >10000))] 
    df6 = df.loc[(df['type'] == 'CASH-OUT') & ((df['amount'] < 1) | (df['amount'] >10000))]  
    return pd.concat([df3,df4,df5,df6])['Unnamed: 0'].values.tolist()

def iban_initals(df):
    df['to_initials'] = df['to_iban'].str[:2]
    df['from_initials'] = df['from_iban'].str[:2]
    df1 = df.loc[(df['from_initials'] != df['from_country']) & (df['from_country'].isna() == False)]
    df2 = df.loc[(df['to_country'].isna() == False) & (df['to_country'] != df['to_initials'])]
    return pd.concat([df1,df2])['Unnamed: 0'].values.tolist()

def check_comments_names(df):
    df3 = df.loc[df['comment'].apply(lambda x: has_numbers(x))]
    df4 = df.loc[df['name'].apply(lambda x: has_numbers(x))]
    return df4['Unnamed: 0'].values.tolist()

def hour(df):
    return df.loc[(df['hour']>744) | (df['hour']<1)]['Unnamed: 0'].values.tolist()

def type_check(df):
    return df.loc[(df['type'] != "CASH-IN")&(df['type'] != "CASH-OUT")&(df['type'] != "TRANSFER")&(df['type'] != "PAYMENT")]['Unnamed: 0'].values.tolist()

def check_list(x,iso_codes):
    return x not in iso_codes
def currency_check(df):
    return df.loc[df['currency'].apply(lambda x: check_list(x, iso_codes))]['Unnamed: 0'].values.tolist()

def check_iban(df):
    return df.loc[(df['from_iban'].apply(lambda x: validate_iban(x)))]['Unnamed: 0'].values.tolist()

def valid_domain(x):
    domain = x.split("@")[1]
    return domain in invalid_domains

def check_mail(df):
    return df.loc[(df['from_mail'].apply(lambda x: valid_domain(x)))]['Unnamed: 0'].values.tolist()


def check_conditions(df):
    fraud_ids = []
    fraud1 = transfer_amt(df)
    fraud_ids.extend(fraud1)
    fraud2 = iban_initals(df)
    fraud_ids.extend(fraud2)
    fraud3 = check_comments_names(df)
    fraud_ids.extend(fraud3)
    fraud4 = hour(df)
    fraud_ids.extend(fraud4)
    fraud5 = type_check(df)
    fraud_ids.extend(fraud5)
    # fraud6 = currency_check(df)
    # fraud_ids.extend(fraud6)
    fraud7 = check_iban(df)
    fraud_ids.extend(fraud7)
    fraud8 = check_mail(df)
    fraud_ids.extend(fraud8)
    return list(set(fraud_ids))


# def results(fraud_ids):
#     caught = 0
#     for i in fraud_ids:
#         if df.iloc[i]['Fraudulent']:
#             caught+=1
#     return caught/len(fraud_ids)


ids = check_conditions(df)
print(ids)
print(len(ids))