
import warnings
import pandas as pd
import talib as ta
from typing import Any


from pandas import Series, DataFrame



import pyodbc
import os.path
import math
from kiteconnect import KiteConnect
OiMaxCVal=1000
LTP=0
switch=0
ShowAll=False
warnings.simplefilter(action='ignore', category=FutureWarning)

NseSymbol=['NSE:HDFCBANK',
               'NSE:ICICIBANK',
               'NSE:AXISBANK',
               'NSE:KOTAKBANK',
               'NSE:INDUSINDBK',
               'NSE:SBIN',
               'NSE:BAJFINANCE',
               'NSE:BAJAJFINSV',
               'NSE:RELIANCE',
               'NSE:TCS',
               'NSE:INFY',
               ]

NfoSymbols = ['NFO:HDFCBANK',
               'NFO:ICICIBANK',
               'NFO:AXISBANK',
               'NFO:KOTAKBANK',
               'NFO:INDUSINDBK',
               'NFO:SBIN',
               'NFO:BAJFINANCE',
               'NFO:BAJAJFINSV',
               'NFO:RELIANCE',
               'NFO:TCS',
               'NFO:INFY'
               ]

from datetime import datetime, timedelta
date_now = datetime.now().strftime('%Y-%m-%d')


print(datetime.today())
Symbol='NFO:HDFCBANK'
SpotSymbol=Symbol.replace("NFO", "NSE")

def  GetSpotName(Symbol):
    GetSpotName = Symbol.replace("NFO", "NSE")
    return GetSpotName

def LoadFromStream(Symbol):
    from expressoptionchain.option_chain import OptionChainFetcher
    option_chain_fetcher = OptionChainFetcher()
    option_chain = option_chain_fetcher.get_option_chain(Symbol)
    #option_chain = option_chain_fetcher.get_option_chain('NFO:NIFTY')
    # print("Expiry Dates :",option_chain['expiry'])
    # df = pd.DataFrame.from_dict(option_chain['expiry']['22-11-2023'])
    # print(df.head(2))
    return option_chain




# convert to k, million, billion
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', ' K', ' M', ' CR', ' T', ' P'][magnitude])

import threading

def GetSymbol():
    #threading.Timer(10, GetSymbol).start()
    global switch , Symbol

    if switch >= len(NseSymbol):
        switch=0
    Symbol=NfoSymbols[switch-1]
    switch = switch + 1
    print('Length of Nsesymbol',len(NseSymbol),switch)
    print("Symbol Changed :",Symbol)
    return Symbol




def roundup(x):
    return int(math.ceil(x / 100.0)) * 100


def GetQoute():
    threading.Timer(120, GetQoute).start()
    print('Getting Quote....................')

    with open('access_token.txt') as f:
        access_token = f.readline()

    with open('api_key.txt') as f:
        api_key = f.readline()

    # print(access_token)
    # print(api_key)
    access_token = str(access_token)
    api_key = str(api_key)

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    quote = kite.ltp(NseSymbol)
    df2 = pd.DataFrame.from_dict(quote, orient="index")
    df2.to_csv("LTP.csv",mode='w')
    return df2



x=GetQoute()
print(x)
Symbol=GetSymbol()
print("Symbol---- start",Symbol)

def GetLtpFromCsv(Symbol):
    df = pd.read_csv('LTP.csv')
    #print(df)
    if Symbol== 'NSE:BANKNIFTY' :
        Symbol='NSE:NIFTY BANK'

    if Symbol== 'NSE:NIFTY' :
        Symbol='NSE:NIFTY 50'

    df1=df[df['Unnamed: 0']==Symbol]
    GetLtpFromCsv=df1.iloc[0]['last_price']
    #print(GetLtpFromCsv)
    return GetLtpFromCsv

def GetOptionChainWithOI(Symbol):    #### its hear
    global switch,OiMaxCVal,CEOptionsTotrack,PEOptionsTotrack,LTP
    option_chain = LoadFromStream(Symbol)
    # ExpDate = open("Expiry.txt", 'r').read()
    # ExpDate=f"'{ExpDate}'"
    df = pd.DataFrame.from_dict(option_chain['expiry']['28-12-2023'])
    pd.set_option('display.max_rows', None)
    ## created df to store ce and pe values

    dfCE = pd.DataFrame(columns=['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                                 'total_sell_quantity', 'volume', 'instrument_token'])
    dfPE = pd.DataFrame(columns=['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                                 'total_sell_quantity', 'volume', 'instrument_token'])

    ltp=GetLtpFromCsv(GetSpotName(Symbol))
    LTP=ltp
    #print("Last traded price",ltp)


    df.dropna(inplace=True)
    for ind in df.index:
        # loop through the df of expiry with separate (ce and pe) and store in different df and present in understandable format

        xCE = df['ce'][ind]
        xCE['Strike'] = df['strike_price'][ind]
        # print(type(xCE))
        # x=xCE.keys()
        # print(x)
        # print(xCE['premium'])
        df2 = pd.DataFrame([xCE])
        df2 = df2[['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                   'total_sell_quantity', 'volume', 'instrument_token']]
        df2.dropna()
        dfCE = pd.concat([dfCE, df2])

        xPE = df['pe'][ind]
        xPE['Strike'] = df['strike_price'][ind]
        df2 = pd.DataFrame([xPE])
        df2 = df2[['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                   'total_sell_quantity', 'volume', 'instrument_token']]
        df2.dropna()
        dfPE = pd.concat([dfPE, df2])


    dfCE = dfCE[
        ['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity', 'total_sell_quantity',
          'instrument_token']]
    dfPE = dfPE[
        ['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity', 'total_sell_quantity',
         'instrument_token']]

    # dfCE = dfCE[dfCE.oi != 0]
    # dfPE = dfPE[dfPE.oi != 0]

    dfPEITkn = dfPE[['instrument_token', 'Strike']]
    dfCEITkn = dfCE[['instrument_token', 'Strike']]

    #TopRange = roundup(ltp + (ltp * .55) / 5)
    #BottomRange = roundup(ltp - (ltp * .55) / 5)
    TopRange = ltp + ltp *.05
    BottomRange = ltp - ltp *.05

    #print(TopRange,BottomRange)
    # print('maxvals Max Io + - 700 switch=1', OiMaxVal)
    dfCE = dfCE[(dfCE["Strike"] > BottomRange) & (dfCE["Strike"] < TopRange)]
    dfPE = dfPE[(dfPE["Strike"] > BottomRange) & (dfPE["Strike"] < TopRange)]
    #print(dfCE)


    dfCE["oi_Amt"] = dfCE['premium'] * dfCE['oi']
    dfPE["oi_Amt"] = dfPE['premium'] * dfPE['oi']

    dfCE['NewOiC'] = dfCE['total_buy_quantity'] - dfCE['total_sell_quantity']
    dfPE['NewOiC'] = dfPE['total_buy_quantity'] - dfPE['total_sell_quantity']

    dfCE['NewOiC'] = pd.to_numeric(dfCE['NewOiC'], errors='coerce')
    dfPE['NewOiC'] = pd.to_numeric(dfPE['NewOiC'], errors='coerce')


    dfCE['oi_Amt'] = pd.to_numeric(dfCE['oi_Amt'], errors='coerce')
    dfPE['oi_Amt'] = pd.to_numeric(dfPE['oi_Amt'], errors='coerce')

    dfCE['TAmt'] = dfCE['oi_Amt'].sum()
    dfPE['TAmt'] = dfPE['oi_Amt'].sum()

    dfCE['Stradle']=0
    dfPE['Stradle']=0

    ##setting range based on max oi top
    #dfCE = dfCE.nlargest(16, 'oi_Amt')
    #dfPE = dfPE.nlargest(16, 'oi_Amt')

    TAmtCE = dfCE['oi_Amt'].sum()
    TAmtPE = dfPE['oi_Amt'].sum()

    TAmtCEAmt = dfCE['oi_Amt'].sum()
    TAmtPEAmt = dfPE['oi_Amt'].sum()

    dfCE["oi_Amt"] = dfCE["oi_Amt"].apply(human_format)
    dfPE["oi_Amt"] = dfPE["oi_Amt"].apply(human_format)

    dfCE['TAmtCE'] = dfCE['TAmt'].apply(human_format)
    dfPE['TAmtPE'] = dfPE['TAmt'].apply(human_format)

    # pcr=TAmtPE/TAmtCE

    # TAmtCE = human_format(TAmtCE)
    # TAmtPE = human_format(TAmtPE)

    dfCE['NewOi'] = dfCE['total_buy_quantity'] - dfCE['total_sell_quantity']
    dfPE['NewOi'] = dfPE['total_buy_quantity'] - dfPE['total_sell_quantity']

    dfCE['NewOi'] = pd.to_numeric(dfCE['NewOi'], errors='coerce')
    dfPE['NewOi'] = pd.to_numeric(dfPE['NewOi'], errors='coerce')

    NewOiSumCE = dfCE['NewOi'].sum()
    NewOiSumPE = dfPE['NewOi'].sum()

    NewOiSumCEAmt= dfCE['NewOi'].sum()
    NewOiSumPEAmt = dfPE['NewOi'].sum()

    NewOiSumCE = human_format(NewOiSumCE)
    NewOiSumPE = human_format(NewOiSumPE)

    dfCE['NewOiSumCE'] = NewOiSumCE
    dfPE['NewOiSumPE'] = NewOiSumPE

    dfCE['NewOi'] = dfCE['NewOi'].apply(human_format)
    dfPE['NewOi'] = dfPE['NewOi'].apply(human_format)

    dfCE['oi'] = dfCE['oi'].apply(human_format)
    dfPE['oi'] = dfPE['oi'].apply(human_format)


    dfCE = dfCE[['Strike', 'premium', 'change', 'oi', 'NewOi', 'NewOiSumCE', 'TAmtCE', 'instrument_token']]
    dfPE = dfPE[['Strike', 'premium', 'change',  'oi', 'NewOi', 'NewOiSumPE', 'TAmtPE', 'instrument_token']]

    # print("Call Options")
    # print(dfCE.head(1))
    # print("Put Options")

    dfCE.set_index('instrument_token', inplace=False)
    dfPE.set_index('instrument_token', inplace=False)

    # dfCEITkn.reset_index
    # dfPEITkn.reset_index
    # print(dfCEITkn)
    # print("connecting to redis db.. getting refreshed ....",datetime.now())
    # print("Printing::debug getting blank pe " ,dfPE)

    return dfCE, dfPE, TAmtCEAmt, TAmtPEAmt, NewOiSumCEAmt, NewOiSumPEAmt, dfCEITkn, dfPEITkn


##### MAIN GUI frame

import tkinter as tk
import pandas as pd
import time
import logging
import os.path

from tkinter import ttk

logging.basicConfig(level=logging.DEBUG)


# Function to update the Text widget with new data and record the last refresh time
last_refresh_time = None


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / abs(previous)) * 100.0
    except ZeroDivisionError:
        return 0

def ShowNfoStatus():
    dfnfo=GenFnoImpStatus()
    text_left.delete("1.0", "end")  # Clear the existing text
    text_left.insert("1.0", dfnfo.to_string(index=False))  # Insert new data
    text_right.delete("1.0", "end")  # Clear the existing text
    text_right.insert("1.0", dfnfo.to_string(index=False))  # Insert new dat

def update_text_widget():
    global last_refresh_time
    global dfCEITknVal, dfPEITknVal
    # get historical data to get prev day's OI to calculate change in oi
    # function checks if file already exits it exits if it does

    ### checks if the oi data is loaded and presented, if not we load the data from historical data of all the strikes of CE and PE
    print("Symbol Changed and Getting that Chain : ",Symbol)
    if (ShowAll=="All") :
        dfCE, dfPE, TAmtCE, TAmtPE, NewOiSumCE, NewOiSumPE, dfCEITknVal, dfPEITknVal = GetOptionChainWithOI(Symbol)
        # print("Printing::debug getting blank pe(Before) " ,dfPE)
        dfCE =  dfCE[['Strike', 'premium', 'change','oi', 'NewOi', 'NewOiSumCE', 'TAmtCE']]
        dfPE =  dfPE[['Strike', 'premium', 'change','oi', 'NewOi', 'NewOiSumPE', 'TAmtPE']]
        #### sorting remove these two lines
        #dfCE.sort_values(by=['Strike'], ascending=True,inplace=True)
        #dfPE.sort_values(by=['Strike'], ascending=True,inplace=True)

        # print("Printing::debug getting blank pe " ,dfPE)
        text_left.delete("1.0", "end")  # Clear the existing text
        text_left.insert("1.0", dfCE.to_string(index=False))  # Insert new data
        text_right.delete("1.0", "end")  # Clear the existing text
        text_right.insert("1.0", dfPE.to_string(index=False))  # Insert new data
        last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # update_totals(TAmtCE,TAmtPE,NewOiSumCE,NewOiSumPE)  # Update the totals

        diffPerS = get_change(TAmtCE, TAmtPE)
        if (TAmtCE > TAmtPE):
            Signal_Label.config(text="Bullish long Term % : " + str(round(diffPerS, 2)), bg="green")
        elif (TAmtCE < TAmtPE):
            Signal_Label.config(text="Bearish Long Term % :" + str(round(diffPerS, 2)), bg="red")
        else:
            Signal_Label.config(text="NO diection : " + str(round(diffPerS, 2)), bg="yellow")

        pg1.step(diffPerS)
        pg1["value"] = diffPerS


        diffPerL = get_change(NewOiSumCE, NewOiSumPE)
        if (NewOiSumCE > NewOiSumPE):
            Signal_Label1.config(text="Bullish short Term % : " + str(round(diffPerL, 2)), bg="green")
        elif (NewOiSumCE < NewOiSumPE):
            Signal_Label1.config(text="Bearish Short Term % :" + str(round(diffPerL, 2)), bg="red")
        else:
            Signal_Label1.config(text="NO direction : " + str(round(diffPerL, 2)), bg="yellow")

        pg2.step(diffPerL)
        pg2["value"] = diffPerL

        if diffPerL > diffPerS :
            pg1['maximum']=diffPerL
            pg2['maximum'] = diffPerL
        else:
            pg1['maximum'] = diffPerS
            pg2['maximum'] = diffPerS

    elif (ShowAll=="NfoSum") :
        dfnfo= GenFnoImpStatus()
        # print("Printing::debug getting blank pe(Before) " ,dfPE)
        text_left.delete("1.0", "end")  # Clear the existing text
        text_left.insert("1.0", dfnfo.to_string(index=False))  # Insert new data
        text_right.delete("1.0", "end")  # Clear the existing text
        text_right.insert("1.0", dfnfo.to_string(index=False))  # Insert new data
        last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # update_totals(TAmtCE,TAmtPE,NewOiSumCE,NewOiSumPE)  # Update the totals

        dfnfo['LongTerm']=dfnfo['LongTerm'].astype(float)
        dfnfo['ShortTerm'] = dfnfo['ShortTerm'].astype(float)
        print("dfnfo", dfnfo['LongTerm'].mean())
        TAmtCE = dfnfo['LongTerm'].mean()
        diffPerS = TAmtCE
        if (TAmtCE > 0):
            Signal_Label.config(text="Bullish long Term % : " + str(round(diffPerS, 2)), bg="green")
        elif (TAmtCE < 0):
            Signal_Label.config(text="Bearish Long Term % :" + str(round(diffPerS, 2)), bg="red")
        else:
            Signal_Label.config(text="NO diection : " + str(round(diffPerS, 2)), bg="yellow")

        pg1.step(diffPerS)
        pg1["value"] = diffPerS

        NewOiSumCE = dfnfo['ShortTerm'].mean()
        diffPerL = NewOiSumCE
        if (NewOiSumCE > 0):
            Signal_Label1.config(text="Bullish short Term % : " + str(round(diffPerL, 2)), bg="green")
        elif (NewOiSumCE < 0):
            Signal_Label1.config(text="Bearish Short Term % :" + str(round(diffPerL, 2)), bg="red")
        else:
            Signal_Label1.config(text="NO direction : " + str(round(diffPerL, 2)), bg="yellow")

        pg2.step(diffPerL)
        pg2["value"] = diffPerL

        if diffPerL > diffPerS:
            pg1['maximum'] = diffPerL
            pg2['maximum'] = diffPerL
        else:
            pg1['maximum'] = diffPerS
            pg2['maximum'] = diffPerS
    elif (ShowAll=="BankNifty"):
        dfCE, dfPE, TAmtCE, TAmtPE, NewOiSumCE, NewOiSumPE, dfCEITknVal, dfPEITknVal = GetOptionChainWithOI(Symbol)
        # print("Printing::debug getting blank pe(Before) " ,dfPE)
        dfCE = dfCE[['Strike', 'premium', 'change', 'oi', 'NewOi', 'NewOiSumCE', 'TAmtCE']]
        dfPE = dfPE[['Strike', 'premium', 'change', 'oi', 'NewOi', 'NewOiSumPE', 'TAmtPE']]
        #### sorting remove these two lines
        # dfCE.sort_values(by=['Strike'], ascending=True,inplace=True)
        # dfPE.sort_values(by=['Strike'], ascending=True,inplace=True)

        # print("Printing::debug getting blank pe " ,dfPE)
        text_left.delete("1.0", "end")  # Clear the existing text
        text_left.insert("1.0", dfCE.to_string(index=False))  # Insert new data
        text_right.delete("1.0", "end")  # Clear the existing text
        text_right.insert("1.0", dfPE.to_string(index=False))  # Insert new data
        last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # update_totals(TAmtCE,TAmtPE,NewOiSumCE,NewOiSumPE)  # Update the totals

        diffPerS = get_change(TAmtCE, TAmtPE)
        if (TAmtCE > TAmtPE):
            Signal_Label.config(text="Bullish long Term % : " + str(round(diffPerS, 2)), bg="green")
        elif (TAmtCE < TAmtPE):
            Signal_Label.config(text="Bearish Long Term % :" + str(round(diffPerS, 2)), bg="red")
        else:
            Signal_Label.config(text="NO diection : " + str(round(diffPerS, 2)), bg="yellow")

        pg1.step(diffPerS)
        pg1["value"] = diffPerS

        diffPerL = get_change(NewOiSumCE, NewOiSumPE)
        if (NewOiSumCE > NewOiSumPE):
            Signal_Label1.config(text="Bullish short Term % : " + str(round(diffPerL, 2)), bg="green")
        elif (NewOiSumCE < NewOiSumPE):
            Signal_Label1.config(text="Bearish Short Term % :" + str(round(diffPerL, 2)), bg="red")
        else:
            Signal_Label1.config(text="NO direction : " + str(round(diffPerL, 2)), bg="yellow")

        pg2.step(diffPerL)
        pg2["value"] = diffPerL

        if diffPerL > diffPerS:
            pg1['maximum'] = diffPerL
            pg2['maximum'] = diffPerL
        else:
            pg1['maximum'] = diffPerS
            pg2['maximum'] = diffPerS
    elif (ShowAll=="Nifty"):
        dfCE, dfPE, TAmtCE, TAmtPE, NewOiSumCE, NewOiSumPE, dfCEITknVal, dfPEITknVal = GetOptionChainWithOI(Symbol)
        # print("Printing::debug getting blank pe(Before) " ,dfPE)
        dfCE = dfCE[['Strike', 'premium', 'change', 'oi', 'NewOi', 'NewOiSumCE', 'TAmtCE']]
        dfPE = dfPE[['Strike', 'premium', 'change', 'oi', 'NewOi', 'NewOiSumPE', 'TAmtPE']]
        #### sorting remove these two lines
        # dfCE.sort_values(by=['Strike'], ascending=True,inplace=True)
        # dfPE.sort_values(by=['Strike'], ascending=True,inplace=True)

        # print("Printing::debug getting blank pe " ,dfPE)
        text_left.delete("1.0", "end")  # Clear the existing text
        text_left.insert("1.0", dfCE.to_string(index=False))  # Insert new data
        text_right.delete("1.0", "end")  # Clear the existing text
        text_right.insert("1.0", dfPE.to_string(index=False))  # Insert new data
        last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # update_totals(TAmtCE,TAmtPE,NewOiSumCE,NewOiSumPE)  # Update the totals

        diffPerS = get_change(TAmtCE, TAmtPE)
        if (TAmtCE > TAmtPE):
            Signal_Label.config(text="Bullish long Term % : " + str(round(diffPerS, 2)), bg="green")
        elif (TAmtCE < TAmtPE):
            Signal_Label.config(text="Bearish Long Term % :" + str(round(diffPerS, 2)), bg="red")
        else:
            Signal_Label.config(text="NO diection : " + str(round(diffPerS, 2)), bg="yellow")

        pg1.step(diffPerS)
        pg1["value"] = diffPerS

        diffPerL = get_change(NewOiSumCE, NewOiSumPE)
        if (NewOiSumCE > NewOiSumPE):
            Signal_Label1.config(text="Bullish short Term % : " + str(round(diffPerL, 2)), bg="green")
        elif (NewOiSumCE < NewOiSumPE):
            Signal_Label1.config(text="Bearish Short Term % :" + str(round(diffPerL, 2)), bg="red")
        else:
            Signal_Label1.config(text="NO direction : " + str(round(diffPerL, 2)), bg="yellow")

        pg2.step(diffPerL)
        pg2["value"] = diffPerL

        if diffPerL > diffPerS:
            pg1['maximum'] = diffPerL
            pg2['maximum'] = diffPerL
        else:
            pg1['maximum'] = diffPerS
            pg2['maximum'] = diffPerS
    if timer_running:
        root.after(6000, update_text_widget)  # Schedule a refresh every 60 seconds if timer is running
        root.title("Option Chain for : " + str(Symbol) + ": Last Price " +str(LTP) )



# getHistoricalData(dfCEITkn,dfPEITkn)
def start_timer(): ### SHOW OPTION CHAIN OF STOCKS ONE BY ONE USING GET SYMBOL
    global timer_running
    timer_running = True
    global ShowAll,Symbol
    Symbol = GetSymbol()
    ShowAll="All"
    update_text_widget()


def Start_All():
    global  ShowAll
    ShowNfoStatus()
    ShowAll="NfoSum"
    global timer_running
    timer_running = False
    update_text_widget()

def Start_Bank():
    global ShowAll,Symbol
    Symbol='NFO:BANKNIFTY'
    ShowAll="BankNifty"
    global timer_running
    timer_running = True
    update_text_widget()

def Start_Nifty():
    global ShowAll,Symbol
    Symbol = 'NFO:NIFTY'
    ShowAll="Nifty"
    global timer_running
    timer_running = True
    update_text_widget()




def GenFnoImpStatus():    #### its hear
    global switch,OiMaxCVal,LTP
    dfStatus = pd.DataFrame(columns=['Symbol', 'LongTerm', 'ShortTerm', 'StatusLong', 'StatusShort', 'DateUpdated'])
    dfStatusResult = pd.DataFrame(
        columns=['Symbol','Price', 'LongTerm', 'ShortTerm', 'StatusLong', 'StatusShort', 'DateUpdated'])

    SyList=pd.DataFrame(NfoSymbols,columns =['Symbol'])
    SyList.set_index('Symbol')
    print("Printing symbol list:",SyList)
    for Syno in SyList.index:
        oc = LoadFromStream(SyList['Symbol'][Syno])
        Symbol=SyList['Symbol'][Syno]
        #print("Getting status for :",Symbol)
        # ExpDate = open("Expiry.txt", 'r').read()
        # ExpDate=f"'{ExpDate}'"
        df = pd.DataFrame.from_dict(oc['expiry']['28-12-2023'])
        pd.set_option('display.max_rows', None)

        dfCE = pd.DataFrame(columns=['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                                     'total_sell_quantity', 'volume', 'instrument_token'])
        dfPE = pd.DataFrame(columns=['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                                     'total_sell_quantity', 'volume', 'instrument_token'])
        print(GetSpotName(Symbol))
        ltp=GetLtpFromCsv(GetSpotName(Symbol))
        LTP=ltp
       # print("Last traded price",Symbol,ltp)


        df.dropna(inplace=True)
        for ind in df.index:
            # loop through the df of expiry with separate (ce and pe) and store in different df and present in understandable format

            xCE = df['ce'][ind]
            xCE['Strike'] = df['strike_price'][ind]
            # print(type(xCE))
            # x=xCE.keys()
            # print(x)
            # print(xCE['premium'])
            df2 = pd.DataFrame([xCE])
            df2 = df2[['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                       'total_sell_quantity', 'volume', 'instrument_token']]
            df2.dropna()
            dfCE = pd.concat([dfCE, df2])

            xPE = df['pe'][ind]
            xPE['Strike'] = df['strike_price'][ind]
            df2 = pd.DataFrame([xPE])
            df2 = df2[['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity',
                       'total_sell_quantity', 'volume', 'instrument_token']]
            df2.dropna()
            dfPE = pd.concat([dfPE, df2])


        dfCE = dfCE[
            ['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity', 'total_sell_quantity',
              'instrument_token']]
        dfPE = dfPE[
            ['Strike', 'premium', 'change', 'oi', 'oi_day_high', 'oi_day_low', 'total_buy_quantity', 'total_sell_quantity',
             'instrument_token']]

        TopRange = ltp + ltp *.05
        BottomRange = ltp - ltp *.05
        #print(TopRange,BottomRange)
        # print('maxvals Max Io + - 700 switch=1', OiMaxVal)
        dfCE = dfCE[(dfCE["Strike"] > BottomRange) & (dfCE["Strike"] < TopRange)]
        dfPE = dfPE[(dfPE["Strike"] > BottomRange) & (dfPE["Strike"] < TopRange)]



        dfCE["oi_Amt"] = dfCE['premium'] * dfCE['oi']
        dfPE["oi_Amt"] = dfPE['premium'] * dfPE['oi']

        dfCE['NewOiC'] = dfCE['total_buy_quantity'] - dfCE['total_sell_quantity']
        dfPE['NewOiC'] = dfPE['total_buy_quantity'] - dfPE['total_sell_quantity']

        dfCE['NewOiC'] = pd.to_numeric(dfCE['NewOiC'], errors='coerce')
        dfPE['NewOiC'] = pd.to_numeric(dfPE['NewOiC'], errors='coerce')


        dfCE['oi_Amt'] = pd.to_numeric(dfCE['oi_Amt'], errors='coerce')
        dfPE['oi_Amt'] = pd.to_numeric(dfPE['oi_Amt'], errors='coerce')

        dfCE['TAmt'] = dfCE['oi_Amt'].sum()
        dfPE['TAmt'] = dfPE['oi_Amt'].sum()

        dfCE['Stradle']=0
        dfPE['Stradle']=0

        TAmtCE = dfCE['oi_Amt'].sum()
        TAmtPE = dfPE['oi_Amt'].sum()

        TAmtCEAmt = dfCE['oi_Amt'].sum()
        TAmtPEAmt = dfPE['oi_Amt'].sum()


        # pcr=TAmtPE/TAmtCE

        # TAmtCE = human_format(TAmtCE)
        # TAmtPE = human_format(TAmtPE)

        dfCE['NewOi'] = dfCE['total_buy_quantity'] - dfCE['total_sell_quantity']
        dfPE['NewOi'] = dfPE['total_buy_quantity'] - dfPE['total_sell_quantity']

        dfCE['NewOi'] = pd.to_numeric(dfCE['NewOi'], errors='coerce')
        dfPE['NewOi'] = pd.to_numeric(dfPE['NewOi'], errors='coerce')

        NewOiSumCE = dfCE['NewOi'].sum()
        NewOiSumPE = dfPE['NewOi'].sum()

        NewOiSumCEAmt= dfCE['NewOi'].sum()
        NewOiSumPEAmt = dfPE['NewOi'].sum()

        dfCE['TAmtCE'] = dfCE['TAmt'].apply(human_format)
        dfPE['TAmtPE'] = dfPE['TAmt'].apply(human_format)

        dfCE['NewOiSumCE'] = NewOiSumCE
        dfPE['NewOiSumPE'] = NewOiSumPE

        dfCE = dfCE[['Strike', 'premium', 'change', 'oi', 'NewOi', 'NewOiSumCE', 'TAmtCE', 'instrument_token']]
        dfPE = dfPE[['Strike', 'premium', 'change',  'oi', 'NewOi', 'NewOiSumPE', 'TAmtPE', 'instrument_token']]

        #print("Option chain in status function :", dfCE)

        # print("Call Options")
        # print(dfCE.head(1))
        # print("Put Options")

        dfCE.set_index('instrument_token', inplace=False)
        dfPE.set_index('instrument_token', inplace=False)

        #dfX=pd.DataFrame()
        print('Processing Option Chain for :', Symbol,date_now)
        dfCE['Symbol'] = str(Symbol)
        dfCE['DateUpdated'] =str(date_now)
        dfCE['Price']=LTP


        diffPerS = get_change(TAmtCE, TAmtPE)
        if (TAmtCE > TAmtPE):
            #Signal_Label.config(text="Bullish long Term % : " + str(round(diffPerS, 2)), bg="green")
            dfCE['StatusLong'] = "Bull longT:"
            dfCE['LongTerm']=str(round(diffPerS, 2))
        elif (TAmtCE < TAmtPE):
            dfCE['StatusLong'] = "Bear longT:"
            dfCE['LongTerm'] =  str(-round(diffPerS, 2))
        else:
            dfCE['StatusLong'] = "NO direction:"
            dfCE['LongTerm'] = str(round(diffPerS, 2))
            #Signal_Label.config(text="NO direction : " + str(round(diffPerS, 2)), bg="yellow")



        diffPerL = get_change(NewOiSumCE, NewOiSumPE)
        if (NewOiSumCE > NewOiSumPE):
            dfCE['StatusShort'] = "Bull ShortT:"
            dfCE['ShortTerm'] = str(round(diffPerL, 2))
            #Signal_Label1.config(text="Bullish short Term % : " + str(round(diffPerL, 2)), bg="green")
        elif (NewOiSumCE < NewOiSumPE):
            dfCE['StatusShort'] = "Bear ShortT:"
            dfCE['ShortTerm'] = str(-round(diffPerL, 2))
            #Signal_Label1.config(text="Bearish Short Term % :" + str(round(diffPerL, 2)), bg="red")
        else:
            dfCE['StatusShort'] = "NO direction:"
            dfCE['ShortTerm'] = str(round(diffPerL, 2))
           #Signal_Label1.config(text="NO direction : " + str(round(diffPerL, 2)), bg="yellow")

        dfStatus=dfCE[['Symbol','Price', 'LongTerm', 'ShortTerm', 'StatusLong', 'StatusShort', 'DateUpdated']]
        #global dfStatusResult
        dfStatusResult = pd.concat([dfStatusResult, dfStatus.tail(1)])
    #print(dfStatusResult)
    return dfStatusResult




def stop_timer():
    global timer_running
    timer_running = False
    ShowNfoStatus()





def show_last_refresh_time():
    x= GenFnoImpStatus()
    print(x)
    #print("Refresh Button Call Exits if data is present already in csv format", dfCEITknVal)
    # getHistoricalData(dfCEITknVal,dfPEITknVal)
    if last_refresh_time is not None:
        last_refresh_label.config(text=f"Last refresh time: {last_refresh_time}")
    else:
        last_refresh_label.config(text="Data has not been refreshed yet")

root = tk.Tk()
root.title(
    f"Option Chain- Golden Systems LTD. Started Development on 6-11-2023 / Add Oi Change Getting Historical Data {Symbol} ")

# Create a Canvas widget for the left grid
canvas_left = tk.Canvas(root, borderwidth=0, width=300, height=300)
canvas_left.grid(row=0, column=0)

# Create a Text widget to display data in the left grid
text_left = tk.Text(canvas_left, wrap=tk.NONE, borderwidth=1, height=18, width=80)
text_left.pack(expand=tk.YES, fill=tk.BOTH)

# Create a Canvas widget for the right grid
canvas_right = tk.Canvas(root, borderwidth=0, width=300, height=300)
canvas_right.grid(row=0, column=1)

# Create a Text widget to display data in the right grid
text_right = tk.Text(canvas_right, wrap=tk.NONE, borderwidth=1, height=18, width=80)
text_right.pack(expand=tk.YES, fill=tk.BOTH)

text_left.grid(row=0, column=0)
text_right.grid(row=0, column=1)



# Create buttons for starting, stopping the timer, and showing last refresh time
start_button = tk.Button(root, text="Start Timer", command=start_timer)
start_button.grid(row=1, column=0)
stop_button = tk.Button(root, text="Stop And Show Nfo Status", command=stop_timer)
stop_button.grid(row=1, column=1)

ShowAll_button = tk.Button(root, text="ShowALL", command=Start_All)
ShowAll_button.grid(row=1, column=2)

BANKNIFTY_button = tk.Button(root, text="BANKNIFTY", command=Start_Bank)
BANKNIFTY_button.grid(row=1, column=3)

NIFTY_button = tk.Button(root, text="NIFTY", command=Start_Nifty)
NIFTY_button.grid(row=1, column=4)


show_last_refresh_button = tk.Button(root, text="Show Last Refresh Time", command=show_last_refresh_time)
show_last_refresh_button.grid(row=2, column=0, columnspan=2)
last_refresh_label = tk.Label(root, text="")
last_refresh_label.grid(row=3, column=0, columnspan=2)

Signal_Label = tk.Label(root, text="Long term Signal")
Signal_Label.grid(row=2, column=0)
Signal_Label1 = tk.Label(root, text="Short term Signal")
Signal_Label1.grid(row=2, column=1)

pg1 = ttk.Progressbar(maximum=100)
pg1.grid(row=3, column=0)
pg2 = ttk.Progressbar(maximum=100)
pg2.grid(row=3, column=1)

# Create a Text widget to display totals
# totals_text = tk.Text(root, wrap=tk.NONE, borderwidth=1,width=35,height=5)
# totals_text.grid(row=1, column=1, columnspan=2)


timer_running = False  # Flag to control the timer

root.mainloop()
