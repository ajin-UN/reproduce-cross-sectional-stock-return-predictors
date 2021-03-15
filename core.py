def calMon6m(df):
    df = df.sort_values(["permno", "time_avail_m"], ascending=[True, True])
    mon6m = df["ret2"]
    #mon6m = df_mon6m.groupby('time_avail_m').mean()
    Mom6m = ((1 + mon6m.shift(1)) * (1 + mon6m.shift(2)) * (1 + mon6m.shift(3)) * \
                (1 + mon6m.shift(4)) * (1 + mon6m.shift(5))) - 1
    return Mom6m


# 1 52-week high
# gen temp = max(l1.maxpr, l2.maxpr, l3.maxpr, l4.maxpr, l5.maxpr, l6.maxpr, ///
# 	l7.maxpr, l8.maxpr, l9.maxpr, l10.maxpr, l11.maxpr, l12.maxpr)
# gen High52 = (abs(prc)/cfacshr)/temp	
# drop temp*
# label var High52 "52-week High"
def High52(df):
    df_high52 = df[["time_avail_m", "maxpr", "prc", "cfacshr"]].groupby('time_avail_m').mean()
    for i in range(1,13):
        df_high52["maxpr_lag{}".format(i)] = df_high52["maxpr"].shift(i)
    df_high52["maxpr"] = df_high52[["maxpr_lag1","maxpr_lag2","maxpr_lag3","maxpr_lag4",\
                                   "maxpr_lag5","maxpr_lag6","maxpr_lag7","maxpr_lag8",\
                                   "maxpr_lag9","maxpr_lag10","maxpr_lag11","maxpr_lag12"]].max(axis=1)
    High52 = ((abs(df_high52["prc"]) / df_high52["cfacshr"]) / df_high52["maxpr"]).fillna(0)
    return High52


# 2 Accruals
# gen tempTXP = txp
# replace tempTXP = 0 if mi(txp)

# gen Accruals = ( (act - l12.act) - (che - l12.che) - ( (lct - l12.lct) - ///
# 	(dlc - l12.dlc) - (tempTXP - l12.tempTXP) )) / ( (at + l12.at)/2)
# label var Accruals "Accruals"
# drop temp*
def Accruals(df_copy1):
    df_copy1["temTXP"] = df_copy1["txp"].fillna(0)
    df_new = df_copy1[["time_avail_m", "act", "che", "lct", "dlc", "temTXP", "at"]].groupby('time_avail_m').mean()
    Accruals = ( (df_new["act"] - df_new["act"].shift(12)) - (df_new["che"] - df_new["che"].shift(12)) - \
                ( (df_new["lct"] - df_new["lct"].shift(12)) - (df_new["dlc"] - df_new["dlc"].shift(12)) - \
                 (df_new["temTXP"] - df_new["temTXP"].shift(12)) )) / ((df_new["at"] + df_new["at"].shift(12))/2)
    return Accruals


# 4 Illiquidity
# gen Illiquidity = (ill + l.ill + l2.ill + l3.ill + l4.ill + l5.ill + ///
# 	l6.ill + l7.ill + l8.ill + l9.ill + l10.ill + l11.ill)/12
# label var Illiquidity "Illiquidity"
def Illiquidity(df_copy1):
    df_new = df_copy1[["time_avail_m", "ill"]].groupby('time_avail_m').mean()
    for i in range(1,12):
        df_new["ill_lag{}".format(i)] = df_new["ill"].shift(i)
    Illiquidity = (df_new["ill"] + df_new["ill_lag1"] + df_new["ill_lag2"] + \
                             df_new["ill_lag3"] + df_new["ill_lag4"] + df_new["ill_lag5"] + \
                             df_new["ill_lag6"] + df_new["ill_lag7"] + df_new["ill_lag8"] + \
                             df_new["ill_lag9"] + df_new["ill_lag10"] + df_new["ill_lag11"]) /12
    return df_new["ill_lag1"]


# 6 Asset Growth
# gen AssetGrowth = (at - l12.at)/l12.at 
# label var AssetGrowth "Asset Growth"
def AssetGrowth(df_copy1):
    df_new = df_copy1[["time_avail_m", "at"]].groupby('time_avail_m').mean()
    AssetGrowth = (df_new["at"] - df_new["at"].shift(12)) / df_new["at"].shift(12)
    return AssetGrowth


# 7 Asset Turnover
# gen temp = (rect + invt + aco + ppent + intan - ap - lco - lo) 
# gen AssetTurnover = sale/((temp + l12.temp)/2)
# drop temp
# replace AssetTurnover = . if AssetTurnover < 0
# label var AssetTurnover "Asset Turnover"
def AssetTurnover(df_copy1):
    df_copy1["temp"] = df_copy1["rect"] + df_copy1["invt"] + df_copy1["aco"] + df_copy1["ppent"] + \
                        df_copy1["intan"] - df_copy1["ap"] - df_copy1["lco"] - df_copy1["lo"]
    df_new = df_copy1[["time_avail_m", "temp", "sale"]].groupby('time_avail_m').mean()
    df_new["AssetTurnover"] = df_new["sale"] / ((df_new["temp"] + df_new["temp"].shift(12)) / 2)
    df_new.loc[df_new["AssetTurnover"]<0, "AssetTurnover"] = 0
    AssetTurnover = df_new["AssetTurnover"]
    return AssetTurnover


# 13 Change in Asset Turnover
# gen ChAssetTurnover = AssetTurnover - l12.AssetTurnover
# label var ChAssetTurnover "Change in Asset Turnover"
def ChAssetTurnover(df_copy1):
    df_copy1["temp"] = df_copy1["rect"] + df_copy1["invt"] + df_copy1["aco"] + df_copy1["ppent"] + \
                        df_copy1["intan"] - df_copy1["ap"] - df_copy1["lco"] - df_copy1["lo"]
    df_new = df_copy1[["time_avail_m", "temp", "sale"]].groupby('time_avail_m').mean()
    df_new["AssetTurnover"] = df_new["sale"] / ((df_new["temp"] + df_new["temp"].shift(12)) / 2)
    df_new.loc[df_new["AssetTurnover"]<0, "AssetTurnover"] = 0
    #df_new = df_copy1[["time_avail_m", "AssetTurnover"]].groupby('time_avail_m').mean()
    ChAssetTurnover = df_new["AssetTurnover"] - df_new["AssetTurnover"].shift(12)
    return ChAssetTurnover


# 413 Change in Forecast and Accrual
# gen tempAccruals = ( (act - l12.act) - (che - l12.che) - ( (lct - l12.lct) - ///
# 	(dlc - l12.dlc) - (txp - l12.txp) )) / ( (at + l12.at)/2)
# egen tempsort = fastxtile(tempAccruals), by(time_avail_m) n(2)
# gen ChForecastAccrual = 1 if meanest > l.meanest & !mi(meanest) & !mi(l.meanest)
# replace ChForecastAccrual = 0 if meanest < l.meanest & !mi(meanest) & !mi(l.meanest)
# replace ChForecastAccrual = . if tempsort == 1
# drop temp*
# label var ChForecastAccrual "Change in Forecast and Accrual"
def ChForecastAccrual(df_copy1):
    # df_copy1["temTXP"] = df_copy1["txp"].fillna(0)
    df_new = df_copy1[["time_avail_m", "act", "che", "lct", "dlc", "txp", "at"]].groupby('time_avail_m').mean()
    ChForecastAccrual = ( (df_new["act"] - df_new["act"].shift(12)) - (df_new["che"] - df_new["che"].shift(12)) - \
                ( (df_new["lct"] - df_new["lct"].shift(12)) - (df_new["dlc"] - df_new["dlc"].shift(12)) - \
                 (df_new["txp"] - df_new["txp"].shift(12)) )) / ((df_new["at"] + df_new["at"].shift(12))/2)
    return ChForecastAccrual


# 14 Change in Profit Margin
# gen ChPM = PM - l12.PM
# label var ChPM "Change in Profit Margin"
def ChPM(df_copy1):
    df_new = df_copy1[["time_avail_m", "PM"]].groupby('time_avail_m').mean()
    ChPM = df_new["PM"] - df_new["PM"].shift(12)
    return ChPM

# 22 Dividends
# gen DivInd = ( (l11.ret > l11.retx) )
# *replace DivInd = . if abs(prc) < 5
# label var DivInd "Dividend Indicator"

def DivInd(df_copy1):
    df_new = df_copy1[["time_avail_m", "ret", "retx", "prc"]].groupby('time_avail_m').mean()
    df_new["DivInd"] = df_new["ret"].shift(11) > df_new["retx"].shift(11)
    df_new.loc[abs(df_new["prc"]) < 5, "DivInd"] = 0
    DivInd = df_new["DivInd"]
    return DivInd


# 23 Down Forecast
# gen DownForecast = (meanest < l.meanest)
# label var DownForecast "Down Forecast EPS"
def DownForecast(df_copy1):
    df_new = df_copy1[["time_avail_m", "meanest"]].groupby('time_avail_m').mean()
    df_new["DownForecast"] = df_new["meanest"] < df_new["meanest"].shift(1)
    DownForecast = df_new["DownForecast"]
    return DownForecast


# 24 Earnings-to-Price ratio
# * original paper uses Dec 31 obs for ib and mve_c, while our 
# * mve_c gets updated monthly.  Thus, I lag mve_c 6 months
# * to try to get at the spirit of the original paper.  
# * this lag helps a lot, as it seems to remove momentum effects.   
# * excluding EP < 0 and using the original sample (not MP's) helps too
# * 2018 04 AC
# gen tempib = ib
# gen tempp = l6.mve_c
# gen EP        = tempib/tempp
# replace EP  = . if EP < 0
# label var EP "Earnings-to-price ratio"
# cap drop temp*
def EP(df_copy1):
    df_new = df_copy1[["time_avail_m", "lt", "dlc", "dltt", "at"]].groupby('time_avail_m').mean()
    df_new["temp"] = df_new["lt"] - df_new["dlc"] - df_new["dltt"]
    EP = (df_new["temp"] - df_new["temp"].shift(12)) / df_new["at"].shift(12)
    return EP


# 25 Earnings consistency
# cap drop temp*
# gen EarningsConsistency = (epspx - l12.epspx)/(.5*(abs(l12.epspx) + abs(l24.epspx)))

# label var EarningsConsistency "Earnings Consistency"

def EarningsConsistency(df_copy1):
    df_new = df_copy1[["time_avail_m", "epspx"]].groupby('time_avail_m').mean()
    EarningsConsistency = (df_new["epspx"] - df_new["epspx"].shift(12)) / (0.5 * \
                        (abs(df_new["epspx"].shift(12)) + abs(df_new["epspx"].shift(24))))
    return EarningsConsistency


# 27 Enterprise component of BM
# gen temp = che - dltt - dlc - dc - dvpa+ tstkp
# gen EBM = (ceq + temp)/(mve_c + temp)
# drop temp
# label var EBM "Enterprise component of BM"


def EBM(df_copy1):
    df_copy1["temp"] = df_copy1["che"] - df_copy1["dltt"]- df_copy1["dlc"] -df_copy1["dc"] \
                        -df_copy1["dvpa"] + df_copy1["tstkp"]
    EBM = (df_copy1["ceq"] + df_copy1["temp"]) /(df_copy1["mve_c"] + df_copy1["temp"])
    return EBM



# 28 Enterprise Multiple
# gen EntMult = (mve_c + dltt + dlc + dc - che)/oibdp
# replace EntMult = . if ceq < 0  // This screen come from Loughran and Wellman's paper, MP don't mention them.
# label var EntMult "Enterprise Multiple"

def EntMult(df_copy1):
    df_copy1["EntMult"] = (df_copy1["mve_c"] - df_copy1["dltt"]- df_copy1["dlc"] -df_copy1["dc"]- df_copy1["che"]) /df_copy1["oibdp"]
    df_copy1.loc[df_copy1["ceq"]<0, "EntMult"] = 0
    EntMult = df_copy1["EntMult"]
    return EntMult


# 29 Exchange Switch
# gen ExchSwitch = ( ( exchcd == 1 & (l1.exchcd == 2 | l2.exchcd == 2 | l3.exchcd == 2 | ///
#   l4.exchcd == 2 | l5.exchcd == 2 | l6.exchcd == 2 | l7.exchcd == 2 | ///
#   l8.exchcd == 2 | l9.exchcd == 2 | l10.exchcd == 2 | l11.exchcd == 2 | l12.exchcd == 2 | ///
#   l1.exchcd == 3 | l2.exchcd == 3 | l3.exchcd == 3 | ///
#   l4.exchcd == 3 | l5.exchcd == 3 | l6.exchcd == 3 | l7.exchcd == 3 | ///
#   l8.exchcd == 3 | l9.exchcd == 3 | l10.exchcd == 3 | l11.exchcd == 3 | l12.exchcd == 3)) | ///
#   ( exchcd == 2 & (l1.exchcd == 3 | l2.exchcd == 3 | l3.exchcd == 3 | ///
#   l4.exchcd == 3 | l5.exchcd == 3 | l6.exchcd == 3 | l7.exchcd == 3 | ///
#   l8.exchcd == 3 | l9.exchcd == 3 | l10.exchcd == 3 | l11.exchcd == 3 | l12.exchcd == 3) ))
# label var ExchSwitch "Exchange Switch"

def ExchSwitch(df_copy1):
    df_new = df_copy1[["time_avail_m", "exchcd"]].groupby('time_avail_m').mean()
    df_new["chearn"] = df_new["exchcd"] - df_new["exchcd"].shift(12)
    df_new["nincr"] = 0
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) <= 0, "nincr"] = 1
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) <= 0, "nincr"] = 2
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) <= 0, "nincr"] = 3
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) <= 0, "nincr"] = 4
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) <= 0, "nincr"] = 5
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) > 0 and df_new["chearn"].shift(18) <= 0, "nincr"] = 6
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) > 0 and df_new["chearn"].shift(18) > 0 and \
               df_new["chearn"].shift(21) <= 0, "nincr"] = 7
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) > 0 and df_new["chearn"].shift(18) > 0 and \
               df_new["chearn"].shift(21) > 0 and df_new["chearn"].shift(24) <= 0, "nincr"] = 8
    ExchSwitch = df_new["nincr"]
    return ExchSwitch



# 31 Firm Age - Momentum
# gen FirmAgeMom = ( (1+l.ret2)*(1+l2.ret2)*(1+l3.ret2)*(1+l4.ret2)*(1+l5.ret2) ) - 1
# label var FirmAgeMom "Firm Age - Momentum"

def FirmAgeMom(df):
    df_FirmAgeMom = df[["time_avail_m", "ret2"]]
    FirmAgeMom = df_FirmAgeMom.groupby('time_avail_m').mean()
    FirmAgeMom = ((1 + FirmAgeMom.shift(1)) * (1 + FirmAgeMom.shift(2)) * (1 + FirmAgeMom.shift(3)) * \
                (1 + FirmAgeMom.shift(4)) * (1 + FirmAgeMom.shift(5))) - 1
    return FirmAgeMom



# 35 Growth in long term net operating assets
# gen GrLTNOA =     (rect+invt+ppent+aco+intan+ao-ap-lco-lo)/at -(l12.rect+l12.invt+ ///
#   l12.ppent+l12.aco+l12.intan+l12.ao-l12.ap-l12.lco-l12.lo)/l12.at ///
#   - ( rect-l12.rect+invt-l12.invt + aco-l12.aco-(ap-l12.ap+lco-l12.lco) -dp )/((at+l12.at)/2)
# label var GrLTNOA "Growth in long term net operating assets"

def GrLTNOA(df_copy1):
    df_new = df_copy1[["time_avail_m", "rect", "invt", "ppent", "aco", "intan", "ao", \
                      "ap", "lco", "lo", "at", "dp"]].groupby('time_avail_m').mean()
    GrLTNOA = (df_new["rect"] + df_new["invt"] + df_new["ppent"] + df_new["aco"] + df_new["intan"] + \
             df_new["ao"] - df_new["ap"] - df_new["lco"] - df_new["lo"])/df_new["at"] - (df_new["rect"].shift(12)\
             + df_new["invt"].shift(12) + df_new["ppent"].shift(12)+ df_new["aco"].shift(12) + \
             df_new["intan"].shift(12) + df_new["ao"].shift(12) - df_new["ap"].shift(12) - df_new["lco"].shift(12) \
            - df_new["lo"].shift(12))/df_new["at"].shift(12) - (df_new["rect"]-df_new["rect"].shift(12) + df_new["invt"] - \
            df_new["invt"].shift(12) + df_new["aco"] -df_new["aco"].shift(12) - df_new["ap"] +df_new["ap"].shift(12) \
            - df_new["lco"] + df_new["lco"].shift(12) - df_new["dp"])/((df_new["at"] +df_new["at"].shift(12))/2)
    return GrLTNOA




# 40 Industry momentum
# gen IndMom = ( (1+l.ret2)*(1+l2.ret2)*(1+l3.ret2)*(1+l4.ret2)*(1+l5.ret2)) - 1

def IndMom(df_copy1):
    df_new = df_copy1[["time_avail_m", "ret2"]].groupby('time_avail_m').mean()
    IndMom = ((1 + df_new["ret2"].shift(1)) * (1 + df_new["ret2"].shift(2)) * (1 + df_new["ret2"].shift(3)) * \
                (1 + df_new["ret2"].shift(4)) * (1 + df_new["ret2"].shift(5))) - 1
    return IndMom



# 45 Intermediate momentum
# gen IntMom = ( (1+l7.ret2)*(1+l8.ret2)*(1+l9.ret2)*(1+l10.ret2)*(1+l11.ret2)*(1+l12.ret2) ) - 1
# label var IntMom "Intermediate Momentum"

def IntMom(df_copy1):
    df_new = df_copy1[["time_avail_m", "ret2"]].groupby('time_avail_m').mean()
    IntMom = ((1 + df_new["ret2"].shift(7)) * (1 + df_new["ret2"].shift(8)) * (1 + df_new["ret2"].shift(9)) * \
                (1 + df_new["ret2"].shift(10)) * (1 + df_new["ret2"].shift(11))*(1 + df_new["ret2"].shift(12))) - 1
    return IntMom



# 48 Long-run reversal
# gen Mom36m = (   (1+l13.ret2)*(1+l14.ret2)*(1+l15.ret2)*(1+l16.ret2)*(1+l17.ret2)*(1+l18.ret2)   * ///
#   (1+l19.ret2)*(1+l20.ret2)*(1+l21.ret2)*(1+l22.ret2)*(1+l23.ret2)*(1+l24.ret2)* ///
#   (1+l25.ret2)*(1+l26.ret2)*(1+l27.ret2)*(1+l28.ret2)*(1+l29.ret2)*(1+l30.ret2)     * ///
#   (1+l31.ret2)*(1+l32.ret2)*(1+l33.ret2)*(1+l34.ret2)*(1+l35.ret2)*(1+l36.ret2)  ) - 1
# label var Mom36m "LT reversal"

def Mom36m(df_copy1):
    df_new = df_copy1[["time_avail_m", "ret2"]].groupby('time_avail_m').mean()
    Mom36m = ((1 + df_new["ret2"].shift(13)) * (1 + df_new["ret2"].shift(14)) * (1 + df_new["ret2"].shift(15)) * \
                (1 + df_new["ret2"].shift(16)) * (1 + df_new["ret2"].shift(17))*(1 + df_new["ret2"].shift(18)) * \
             (1 + df_new["ret2"].shift(19)) * (1 + df_new["ret2"].shift(20)) * (1 + df_new["ret2"].shift(21)) * \
                (1 + df_new["ret2"].shift(22)) * (1 + df_new["ret2"].shift(23))*(1 + df_new["ret2"].shift(24)) * \
             (1 + df_new["ret2"].shift(25)) * (1 + df_new["ret2"].shift(26)) * (1 + df_new["ret2"].shift(26)) * \
                (1 + df_new["ret2"].shift(28)) * (1 + df_new["ret2"].shift(29))*(1 + df_new["ret2"].shift(30)) * \
             (1 + df_new["ret2"].shift(31)) * (1 + df_new["ret2"].shift(32) * (1 + df_new["ret2"].shift(33)) * \
                (1 + df_new["ret2"].shift(34)) * (1 + df_new["ret2"].shift(35))*(1 + df_new["ret2"].shift(36)))) - 1
    return Mom36m



# 354 Momentum-Reversal
# gen Mom18m13m = ( (1+l13.ret2)*(1+l14.ret2)*(1+l15.ret2)*(1+l16.ret2)*(1+l17.ret2)*(1+l18.ret2) ) - 1
# replace Mom18m13m  = -1*Mom18m13m 
# label var Mom18m13m "Momentum-Reversal"


def Mom18m13m(df_copy1):
    df_new = df_copy1[["time_avail_m", "ret2"]].groupby('time_avail_m').mean()
    Mom18m13m = ((1 + df_new["ret2"].shift(13)) * (1 + df_new["ret2"].shift(14)) * (1 + df_new["ret2"].shift(15)) * \
                (1 + df_new["ret2"].shift(16)) * (1 + df_new["ret2"].shift(17))*(1 + df_new["ret2"].shift(18))) - 1
    Mom18m13m = -1 * Mom18m13m
    return Mom18m13m



# 56 Net Operating Assets
# gen OA = at - che
# gen OL = at - dltt - mib - dc - ceq
# gen NOA = (OA - OL)/l12.at
# label var NOA "Net Operating Assets"

def NOA(df_copy1):
    df_new = df_copy1[["time_avail_m", "at", "che","dltt","mib","dc","ceq"]].groupby('time_avail_m').mean()
    df_new["OA"] =df_new["at"] - df_new["che"]
    df_new["OL"] =df_new["at"] - df_new["dltt"] - df_new["mib"]- df_new["dc"]- df_new["ceq"]
    NOA =(df_new["OA"] - df_new["OL"]) / (df_new["at"].shift(12))
    return NOA




# 57 Change in Net Working Capital
# gen temp = ( (act - che) - (lct - dlc) )/at
# gen ChNWC = temp - l12.temp
# drop temp*
# label var ChNWC "Change in Net Working Capital"

def ChNWC(df_copy1):
    df_new = df_copy1[["time_avail_m", "at","act", "che","lct","dlc","dc","ceq"]].groupby('time_avail_m').mean()
    df_new["temp"] =((df_new["act"] - df_new["che"]) -(df_new["lct"] - df_new["dlc"]) )/df_new["at"]
    ChNWC =df_new["temp"] -df_new["temp"].shift(12)
    return ChNWC




# 58 Change in Net Noncurrent Operating Assets
# gen temp = ( (at - act - ivao)  - (lt - dlc - dltt) )/at
# gen ChNNCOA = temp - l12.temp
# drop temp*
# label var ChNNCOA "Change in Net Noncurrent Operating Assets"


def ChNNCOA(df_copy1):
    df_new = df_copy1[["time_avail_m", "at","act", "ivao","lt","dlc","dltt","ceq"]].groupby('time_avail_m').mean()
    df_new["temp"] =((df_new["at"] - df_new["act"] - df_new["ivao"]) -(df_new["lt"] - df_new["dlc"] \
                                                                       - df_new["dltt"]) )/df_new["at"]
    ChNNCOA =df_new["temp"] -df_new["temp"].shift(12)
    return ChNNCOA



# 59 Operating Leverage
# * aka OperLeverage
# gen tempxsga      = 0
# replace tempxsga  = xsga if xsga != 0.
# gen OPLeverage = (tempxsga + cogs)/at
# label var OPLeverage "Operating Leverage"
# drop temp*


def OPLeverage(df_copy1):
    df_new = df_copy1[["time_avail_m", "xsga","cogs", "at","lt","dlc","dltt","ceq"]].groupby('time_avail_m').mean()
    df_new["tempxsga"] = 0
    df_new.loc[df_new["xsga"] != 0, "tempxsga"] = df_new["xsga"]
    OPLeverage = (df_new["tempxsga"] + df_new["cogs"]) / df_new["at"]
    return OPLeverage


# 74_1a Seasonality (1 year)
# gen MomSeasAlt1a = l11.ret2
# label var MomSeasAlt1a "Return Seasonality (1 year)"

def MomSeasAlt1a(df_copy1):
    df_new = df_copy1[["time_avail_m", "ret2"]].groupby('time_avail_m').mean()
    MomSeasAlt1a = df_new["ret2"].shift(11)
    return MomSeasAlt1a



# 75 Share issuance (1 year)
# gen temp = shrout/cfacshr
# gen ShareIss1Y = (l6.temp - l18.temp)/l18.temp
# drop temp*
# label var ShareIss1Y "Share Issuance (1 year)"

def ShareIss1Y(df_copy1):
    df_new = df_copy1[["time_avail_m", "shrout", "cfacshr"]].groupby('time_avail_m').mean()
    df_new["temp"] = df_new["shrout"] /df_new["cfacshr"] 
    ShareIss1Y = (df_new["temp"].shift(6)-df_new["temp"].shift(8))/df_new["temp"].shift(18)
    return ShareIss1Y



# 76 Share issuance (5 year)
# gen temp = shrout/cfacshr
# gen ShareIss5Y = (temp - l60.temp)/l60.temp
# drop temp*
# label var ShareIss5Y "Share Issuance (5 year)"

def ShareIss1Y(df_copy1):
    df_new = df_copy1[["time_avail_m", "shrout", "cfacshr"]].groupby('time_avail_m').mean()
    df_new["temp"] = df_new["shrout"] /df_new["cfacshr"] 
    ShareIss1Y = (df_new["temp"]-df_new["temp"].shift(60))/df_new["temp"].shift(60)
    return ShareIss1Y


# 206 Change in Capex over one year
# replace capx = ppent - l12.ppent 
# gen grcapx1y   =  (l12.capx-l24.capx)/l24.capx 
# label var grcapx1y "Change in capex (one year)" 
def capx(df_copy1):
    df_new = df_copy1[["time_avail_m", "ppent"]].groupby('time_avail_m').mean()
    df_new["capx"] = df_new["ppent"] - df_new["ppent"].shift(12)
    grcapx1y = (df_new["capx"].shift(12) - df_new["capx"].shift(24)) / df_new["capx"].shift(24)
    return grcapx1y


# Divide CF and growth rates by 4 to approximate quarterly rates
# gen WW = -.091* (ib+dp)/(4*at) -.062*(dvpsx_c) + .021*dltt/at ///
#          -.044*log(at) - .035*(sale/l.sale - 1)/4
# label var WW "Whited-Wu index (annual)"
# drop temp*
def divideCF(df_copy1):
    df_new = df_copy1[["time_avail_m", "ib", "dp", "at", "dvpsx_c", "dltt", "sale"]].groupby('time_avail_m').mean()
    WW = -.091* (df_new["ib"] + df_new["dp"]) / (4 * df_new["at"]) - 0.062*(df_new["dvpsx_c"]) + 0.021 * \
                            df_new["dltt"] / df_new["at"] - 0.044 * np.log(df_new["at"]) - 0.035 * \
                            (df_new["sale"]/df_new["sale"].shift(1) - 1) / 4
    return WW



# 204 Asset liquidity (market assets)
# gen AssetLiquidityMarket = (che + .75*(act - che) + .5*(at - act - gdwl - intan))/(l.at + l.prcc_f*l.csho - l.ceq)
# label var AssetLiquidityMarket "Asset liquidity (scaled by market value of assets)"
def AssetLiquidityMarket(df_copy1):
    df_new = df_copy1[["time_avail_m", "che", "act", "at", "gdwl", "intan", "prcc_f", "csho", "ceq"]] \
                                                                    .groupby('time_avail_m').mean()
    AssetLiquidityMarket = (df_new["che"] + 0.75 * (df_new["act"] - df_new["che"]) + \
                           0.5* (df_new["at"]-df_new["act"]-df_new["gdwl"]-df_new["intan"])) \
                          / (df_new["at"].shift(1) + df_new["prcc_f"].shift(1) * df_new["csho"].shift(1)\
                            -df_new["ceq"].shift(1))
    
    return AssetLiquidityMarket



# 203 Asset liquidity (book assets)
# gen AssetLiquidityBook = (che + .75*(act - che) + .5*(at - act - gdwl - intan))/l.at
# label var AssetLiquidityBook "Asset liquidity (scaled by book value of assets)"
def AssetLiquidityBook(df_copy1):
    df_new = df_copy1[["time_avail_m", "che", "act", "at", "gdwl", "intan"]].groupby('time_avail_m').mean()
    AssetLiquidityMarket = (df_new["che"] + 0.75 * (df_new["act"] - df_new["che"]) + \
                           0.5* (df_new["at"]-df_new["act"]-df_new["gdwl"]-df_new["intan"])) \
                          / (df_new["at"].shift(1))
    return AssetLiquidityMarket




# 202 Change in Noncurrent Operating Liabilities
# gen temp = lt - dlc - dltt
# gen ChNCOL = (temp - l12.temp)/l12.at
# drop temp*
# label var ChNCOL "Change in Noncurrent Operating Liabilities"
def ChNCOL(df_copy1):
    df_new = df_copy1[["time_avail_m", "lt", "dlc", "dltt", "at"]].groupby('time_avail_m').mean()
    df_new["temp"] = df_new["lt"] - df_new["dlc"] - df_new["dltt"]
    ChNCOL = (df_new["temp"] - df_new["temp"].shift(12)) / df_new["at"].shift(12)
    return ChNCOL



# 201 Change in Noncurrent Operating Assets
# gen temp = at - act - ivao
# gen ChNCOA = (temp - l12.temp)/l12.at
# drop temp*
# label var ChNCOA "Change in Noncurrent Operating Assets"
def ChNCOA(df_copy1):
    df_new = df_copy1[["time_avail_m", "act", "ivao", "at"]].groupby('time_avail_m').mean()
    df_new["temp"] = df_new["at"] - df_new["act"] - df_new["ivao"]
    ChNCOL = (df_new["temp"] - df_new["temp"].shift(12)) / df_new["at"].shift(12)
    return ChNCOA



# 200 Laborforce efficiency
# gen temp = sale/emp
# gen LaborforceEfficiency = (temp - l12.temp)/l12.temp
# label var LaborforceEfficiency "Laborforce efficiency"
# drop temp
def LaborforceEfficiency(df_copy1):
    df_new = df_copy1[["time_avail_m", "sale", "emp"]].groupby('time_avail_m').mean()
    df_new["temp"] = df_new["sale"] / df_new["emp"]
    LaborforceEfficiency = (df_new["temp"] - df_new["temp"].shift(12)) / df_new["temp"].shift(12)
    return LaborforceEfficiency



# 404-405 Option volume
# *optVolume is from 1b_DownloadOptionsAndProcess
# gen OptionVolume1 = optvolume/vol
# replace OptionVolume1 = . if abs(prc) < 1 
# label var OptionVolume1 "Option Volume"

# foreach n of numlist 1/6 {
#   gen tempVol`n' = l`n'.OptionVolume1
#   }
# egen tempMean = rowmean(tempVol*)
# gen OptionVolume2 = OptionVolume1/tempMean
# label var OptionVolume2 "Option Volume (abnormal)"
def OptionVolume1(df_copy1):
    df_new = df_copy1[["time_avail_m", "optvolume", "vol", "prc"]].groupby('time_avail_m').mean()
    df_new["OptionVolume1"] = df_new["optvolume"] / df_new["vol"]
    df_new.loc[abs(df_new["prc"]<1), "OptionVolume1"] = 0
    OptionVolume1 = df_new["OptionVolume1"]
    return OptionVolume1



# 391 Capital turnover
# gen CapTurnover = l12.sale/l24.at
# label var CapTurnover "Capital turnover"
def CapTurnover(df_copy1):
    df_new = df_copy1[["time_avail_m", "sale", "at"]].groupby('time_avail_m').mean()
    CapTurnover = df_new["sale"].shift(12) / df_new["at"].shift(24)
    return CapTurnover



# 390 Composite debt issuance
# gen tempBD = dltt + dlc
# gen CompositeDebtIssuance = log(tempBD/l60.tempBD)
# label var CompositeDebtIssuance "Composite Debt Issuance"
def CompositeDebtIssuance(df_copy1):
    df_new = df_copy1[["time_avail_m", "dltt", "dlc"]].groupby('time_avail_m').mean()
    df_new["tempBD"] = df_new["dltt"] + df_new["dlc"]
    CompositeDebtIssuance = np.log(df_new["tempBD"] / df_new["tempBD"].shift(60))
    return CompositeDebtIssuance




# 388 R&D to sales
# gen rd_sale =   l12.xrd/l12.sale  // Returns seem to be strongest in ht second year after portfolio formation (table IV of Chan et al paper)
# replace rd_sale = . if rd_sale == 0
# label var rd_sale "R&D-to-sales ratio"

def rd_sale(df_copy1):
    df_new = df_copy1[["time_avail_m", "xrd", "sale"]].groupby('time_avail_m').mean()
    df_new["rd_sale"] = df_new["xrd"].shift(12) / df_new["sale"].shift(12)
    df_new.loc[df_new["rd_sale"] == 0, "rd_sale"] = 0
    rd_sale = df_new["rd_sale"]
    return rd_sale



# 387 Analyst revisions
# gen tempRev = (meanest - l.meanest)/abs(l.prc)
# gen REV6 = tempRev + l.tempRev + l2.tempRev + l3.tempRev + l4.tempRev + l5.tempRev + l6.tempRev
# label var REV6 "Earnings forecast revision"

def REV6(df_copy1):
    df_new = df_copy1[["time_avail_m", "meanest", "prc"]].groupby('time_avail_m').mean()
    df_new["tempRev"] = (df_new["meanest"] - df_new["meanest"].shift(1)) / abs(df_new["prc"].shift(1))
    REV6 = df_new["tempRev"] + df_new["tempRev"].shift(1) +df_new["tempRev"].shift(2)+df_new["tempRev"].shift(3) +\
           df_new["tempRev"].shift(4) + df_new["tempRev"].shift(5) + df_new["tempRev"].shift(6)
    
    return REV6




# 385 Net debt to price
# gen NetDebtPrice = ((dltt + dlc + pstk + dvpa - tstkp) - che)/mve_c
# label var NetDebtPrice "Net debt to price ratio"


def NetDebtPrice(df_copy1):
    
    df_copy1["NetDebtPrice"] = (df_copy1["dltt"]+df_copy1["dlc"]+df_copy1["pstk"]+ \
                               df_copy1["dvpa"]-df_copy1["tstkp"]-df_copy1["che"]) / df_copy1["mve_c"]
    
    NetDebtPrice = df_copy1["NetDebtPrice"]
    return NetDebtPrice



# 384 Order backlog
# gen OrderBacklog = ob/(.5*(at + l12.at))
# replace OrderBacklog = . if ob == 0
# label var OrderBacklog "Order Backlog"

def OrderBacklog(df_copy1):
    df_new = df_copy1[["time_avail_m", "ob", "at"]].groupby('time_avail_m').mean()
    df_new["OrderBacklog"] = df_new["ob"] / (0.5 *(df_new["at"]+df_new["at"].shift(12)) )
    df_new.loc[df_new["ob"] == 0, "OrderBacklog"] = 0
    OrderBacklog = df_new["OrderBacklog"]
    return OrderBacklog



# 382 Payout yield
# gen PayoutYield = (dvc + prstkc )/l6.mve_c
# replace PayoutYield = . if PayoutYield <= 0
# label var PayoutYield "Payout Yield"

def PayoutYield(df_copy1):
    df_new = df_copy1[["time_avail_m", "dvc", "prstkc", "mve_c"]].groupby('time_avail_m').mean()
    df_new["PayoutYield"] = (df_new["dvc"] + df_new["prstkc"]) / df_new["mve_c"].shift(6)
    df_new.loc[df_new["PayoutYield"]<=0, "PayoutYield"] = 0
    PayoutYield = df_new["PayoutYield"]
    return PayoutYield



# 366 Consistent earnings increase (continuous version)
# gen chearn = ibq - l12.ibq

# gen nincr = 0
# replace nincr = 1 if chearn > 0 & l3.chearn <=0
# replace nincr = 2 if chearn > 0 & l3.chearn >0 & l6.chearn <=0
# replace nincr = 3 if chearn > 0 & l3.chearn >0 & l6.chearn >0 & l9.chearn <=0
# replace nincr = 4 if chearn > 0 & l3.chearn >0 & l6.chearn >0 & l9.chearn >0 & l12.chearn <=0
# replace nincr = 5 if chearn > 0 & l3.chearn >0 & l6.chearn >0 & l9.chearn >0 & l12.chearn >0 & l15.chearn <=0
# replace nincr = 6 if chearn > 0 & l3.chearn >0 & l6.chearn >0 & l9.chearn >0 & l12.chearn >0 & l15.chearn >0 & l18.chearn <=0
# replace nincr = 7 if chearn > 0 & l3.chearn >0 & l6.chearn >0 & l9.chearn >0 & l12.chearn >0 & l15.chearn >0 & l18.chearn >0 & l21.chearn <=0
# replace nincr = 8 if chearn > 0 & l3.chearn >0 & l6.chearn >0 & l9.chearn >0 & l12.chearn >0 & l15.chearn >0 & l18.chearn >0 & l21.chearn >0 & l24.chearn <=0
# drop chearn
# rename nincr NumEarnIncrease
# label var NumEarnIncrease "Number of consecutive earnings increases"

def chearn(df_copy1):
    df_new = df_copy1[["time_avail_m", "ibq"]].groupby('time_avail_m').mean()
    df_new["chearn"] = df_new["ibq"] - df_new["ibq"].shift(12)
    df_new["nincr"] = 0
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) <= 0, "nincr"] = 1
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) <= 0, "nincr"] = 2
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) <= 0, "nincr"] = 3
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) <= 0, "nincr"] = 4
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) <= 0, "nincr"] = 5
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) > 0 and df_new["chearn"].shift(18) <= 0, "nincr"] = 6
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) > 0 and df_new["chearn"].shift(18) > 0 and \
               df_new["chearn"].shift(21) <= 0, "nincr"] = 7
    df_new.loc[df_new["chearn"]>0 and df_new["chearn"].shift(3) > 0 and df_new["chearn"].shift(6) > 0 \
               and df_new["chearn"].shift(9) > 0 and df_new["chearn"].shift(12) > 0 and \
               df_new["chearn"].shift(15) > 0 and df_new["chearn"].shift(18) > 0 and \
               df_new["chearn"].shift(21) > 0 and df_new["chearn"].shift(24) <= 0, "nincr"] = 8
    NumEarnIncrease = df_new["nincr"]
    return NumEarnIncrease



# 372 Net equity finance
# gen NetEquityFinance = (sstk - prstkc)/(.5*(at + l12.at))
# replace NetEquityFinance = . if abs(NetEquityFinance) > 1
# label var NetEquityFinance "Net Equity Finance"

def NetEquityFinance(df_copy1):
    df_new = df_copy1[["time_avail_m", "sstk", "prstkc", 'at']].groupby('time_avail_m').mean()
    df_new["NetEquityFinance"] = (df_new["sstk"] - df_new["prstkc"]) / (0.5 * (df_new["at"]+df_new["at"].shift(12)))
    df_new.loc[abs(df_new["NetEquityFinance"]) > 1, "NetEquityFinance"] = 0
    NetEquityFinance = df_new["NetEquityFinance"]
    return NetEquityFinance



# 373 Net debt finance
# replace dlcch = 0 if mi(dlcch)
# gen NetDebtFinance = (dltis - dltr - dlcch)/(.5*(at + l12.at))
# replace NetDebtFinance = . if abs(NetDebtFinance) > 1
# label var NetDebtFinance "NetDebtFinance"

def NetDebtFinance(df_copy1):
    df_copy1["dlcch"] = df_copy1["dlcch"].fillna(0)
    df_new = df_copy1[["time_avail_m", "dltis", "dltr", 'dlcch', "at"]].groupby('time_avail_m').mean()
    df_new["NetDebtFinance"] = (df_new["dltis"] - df_new["dltr"] - df_new["dlcch"]) / (0.5 * (df_new["at"]+df_new["at"].shift(12)))
    df_new.loc[abs(df_new["NetDebtFinance"]) > 1, "NetDebtFinance"] = 0
    NetDebtFinance = df_new["NetDebtFinance"]
    return NetDebtFinance



# 374 Growth in advertising expenses
# gen GrAdExp = log(xad) - log(l12.xad)
# replace GrAdExp = . if xad < .1 
# label var GrAdExp "Growth in advertising expenses"

def GrAdExp(df_copy1):
    df_new = df_copy1[["time_avail_m", "xad"]].groupby('time_avail_m').mean()
    df_new["GrAdExp"] = np.log(df_new["xad"]) - np.log(df_new["xad"].shift(12))
    df_new.loc[df_new["xad"]<0.1, "GrAdExp"] = 0
    GrAdExp = df_new["GrAdExp"]
    return GrAdExp




# 375 Gross Margin growth over sales growth
# gen tempGM = sale-cogs
# gen GrGMToGrSales =   ((tempGM- (.5*(l12.tempGM + l24.tempGM)))/(.5*(l12.tempGM + l24.tempGM))) ///
#   - ((sale- (.5*(l12.sale + l24.sale)))/(.5*(l12.sale + l24.sale)))
# drop tempGM
# label var GrGMToGrSales "Gross Margin growth over sales growth"

def GrGMToGrSales(df_copy1):
    df_new = df_copy1[["time_avail_m", "sale", "cogs"]].groupby('time_avail_m').mean()
    df_new["tempGM"] = df_new["sale"] - df_new["cogs"]
    df_new["GrGMToGrSales"] = ((df_new["tempGM"] - (0.5*(df_new["tempGM"].shift(12)+df_new["tempGM"].shift(24) \
                                            )))/ (0.5*(df_new["tempGM"].shift(12)+df_new["tempGM"].shift(24)))) \
                               - ( df_new["sale"]- (0.5*(df_new["sale"].shift(12)+df_new["sale"].shift(24)))) / \
                                (0.5*(df_new["sale"].shift(12)+df_new["sale"].shift(24)))
    
    GrGMToGrSales = df_new["GrGMToGrSales"]
    return GrGMToGrSales



# 377 Change in current operating assets
# gen tempAvAT = .5*(at + l12.at)
# gen DelCOA = (act - che) - (l12.act - l12.che)
# replace DelCOA = DelCOA/tempAvAT
# label var DelCOA "Change in current operating assets"

def DelCOA(df_copy1):
    df_new = df_copy1[["time_avail_m", "at", "act", "che"]].groupby('time_avail_m').mean()
    df_new["tempAvAT"] = 0.5 * (df_new["at"]+df_new["at"].shift(12))
    df_new["DelCOA"] = (df_new["act"] - df_new["che"]) / (df_new["act"].shift(12) + df_new["che"].shift(12))
    DelCOA = df_new["DelCOA"] / df_new["tempAvAT"]
    return DelCOA




# 378 Change in current operating liabilities
# gen DelCOL = (lct - dlc) - (l12.lct - l12.dlc)
# replace DelCOL = DelCOL/tempAvAT
# label var DelCOL "Change in current operating liabilities"

def DelCOL(df_copy1):
    df_new = df_copy1[["time_avail_m", "lct", "dlc", "che", "at"]].groupby('time_avail_m').mean()
    df_new["DelCOL"] = (df_new["lct"] - df_new["dlc"]) - (df_new["lct"].shift(12) + df_new["dlc"].shift(12))
    df_new["tempAvAT"] = 0.5 * (df_new["at"]+df_new["at"].shift(12))
    DelCOL = df_new["DelCOL"] / df_new["tempAvAT"]
    return DelCOL



# 379 Change in Long-term investment
# gen DelLTI = ivao - l12.ivao
# replace DelLTI = DelLTI/tempAvAT
# label var DelLTI "Change in long-term investment"

def DelLTI(df_copy1):
    df_new = df_copy1[["time_avail_m", "ivao",  "at"]].groupby('time_avail_m').mean()
    df_new["DelLTI"] = (df_new["ivao"] - df_new["ivao"].shift(12))
    df_new["tempAvAT"] = 0.5 * (df_new["at"]+df_new["at"].shift(12))
    DelLTI = df_new["DelLTI"] / df_new["tempAvAT"] 
    return DelLTI



# 380 Change in Financial Liabilities
# gen tempPSTK = pstk
# replace tempPSTK = 0 if mi(pstk)

# gen DelFINL = (dltt + dlc + tempPSTK) - (l12.dltt + l12.dlc + l12.tempPSTK)
# replace DelFINL = DelFINL/tempAvAT
# label var DelFINL "Change in financial liabilities"
# drop tempPSTK

def DelFINL(df_copy1):
    df_copy1["tempPSTK"] = df_copy1["pstk"].fillna(0)
    df_new = df_copy1[["time_avail_m", "dltt", "dlc", "tempPSTK", "at"]].groupby('time_avail_m').mean()
    df_new["DelFINL"] = (df_new["dltt"]+df_new["dlc"]+df_new["tempPSTK"]) - (df_new["dltt"].shift(12)\
                                                            +df_new["dlc"].shift(12)+df_new["tempPSTK"].shift(12))
    df_new["tempAvAT"] = 0.5 * (df_new["at"]+df_new["at"].shift(12))
    DelFINL = df_new["DelFINL"] / df_new["tempAvAT"] 
    return DelFINL



# 381 Change in Equity
# gen DelEqu = (ceq - l12.ceq)
# replace DelEqu = DelEqu/tempAvAT
# label var DelEqu "Change in common equity"

def DelEqu(df_copy1):
    df_new = df_copy1[["time_avail_m", "ceq", "at"]].groupby('time_avail_m').mean()
    df_new["DelEqu"] = df_new["ceq"] - df_new["ceq"].shift(12)
    df_new["tempAvAT"] = 0.5 * (df_new["at"]+df_new["at"].shift(12))
    DelEqu = df_new["DelEqu"] / df_new["tempAvAT"] 
    return DelEqu



