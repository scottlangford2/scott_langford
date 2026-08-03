#!/usr/bin/env python3
"""Stage 2: merge Census SAIPE county income+poverty (by year) into the political panel.
Replaces the single-year ERS income/poverty with proper SAIPE series.
Reads _raw_county/saipe/*; rewrites TX_County_Political_Panel_2000_2024.{csv,xlsx}."""
import pandas as pd, glob, os, urllib.request, warnings; warnings.filterwarnings("ignore")
SA="_raw_county/saipe/"
# --- Auto-download SAIPE source files if missing ---
_SU="https://www2.census.gov/programs-surveys/saipe/datasets"
_SAIPE={"est04all.xls":f"{_SU}/2004/2004-state-and-county/est04all.xls",
        "est08all.xls":f"{_SU}/2008/2008-state-and-county/est08all.xls",
        "est12all.xls":f"{_SU}/2012/2012-state-and-county/est12all.xls",
        "est16all.xls":f"{_SU}/2016/2016-state-and-county/est16all.xls",
        "est20all.xls":f"{_SU}/2020/2020-state-and-county/est20all.xls",
        "est23all.xls":f"{_SU}/2023/2023-state-and-county/est23all.xls",
        "est00-tx.dat":f"{_SU}/2000/2000-state-and-county/est00-tx.dat"}
os.makedirs(SA, exist_ok=True)
for _fn,_url in _SAIPE.items():
    if not os.path.exists(SA+_fn):
        print("  downloading",_fn,"..."); _r=urllib.request.Request(_url,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(_r,timeout=300) as _resp, open(SA+_fn,"wb") as _f: _f.write(_resp.read())
# SAIPE year -> election year
XLS={2004:"est04all.xls",2008:"est08all.xls",2012:"est12all.xls",2016:"est16all.xls",2020:"est20all.xls",2023:"est23all.xls"}
elect={2004:2004,2008:2008,2012:2012,2016:2016,2020:2020,2023:2024}
rows=[]
for sy,fn in XLS.items():
    d=pd.read_excel(SA+fn, header=3, dtype=str)
    d=d.rename(columns={d.columns[0]:"st",d.columns[1]:"cty",d.columns[7]:"pov",d.columns[22]:"inc"})
    d=d[(d["st"]=="48") & (~d["cty"].isin(["0","000",None]))].copy()
    d["fips"]="48"+d["cty"].str.zfill(3)
    d["year"]=elect[sy]
    d["poverty_rate"]=pd.to_numeric(d["pov"],errors="coerce")
    d["median_household_income"]=pd.to_numeric(d["inc"].str.replace(",",""),errors="coerce")
    rows.append(d[["fips","year","poverty_rate","median_household_income"]])
# 2000 from whitespace .dat: state f0, county f1, pov% f5, median income f20
d00=[]
for ln in open(SA+"est00-tx.dat",encoding="latin-1"):
    f=ln.split()
    if len(f)<21 or f[0]!="48" or f[1] in ("0","000"): continue
    try: d00.append(("48"+f[1].zfill(3),2000,float(f[5]),float(f[20])))
    except: pass
rows.append(pd.DataFrame(d00,columns=["fips","year","poverty_rate","median_household_income"]))
saipe=pd.concat(rows,ignore_index=True)
print("SAIPE rows:",len(saipe),"| years:",sorted(saipe.year.unique()),"| counties/yr ~",saipe.groupby('year').size().to_dict())

p=pd.read_csv("TX_County_Political_Panel_2000_2024.csv",dtype={"fips":str})
p=p.drop(columns=[c for c in ["poverty_rate","median_household_income"] if c in p.columns])
p=p.merge(saipe,on=["fips","year"],how="left")
# reorder: put income/poverty back at the end (their original slot)
cols=[c for c in p.columns if c not in ("median_household_income","poverty_rate")]+["median_household_income","poverty_rate"]
p=p[cols]
p["poverty_rate"]=p["poverty_rate"].round(1)
p["median_household_income"]=p["median_household_income"].round(0)
p.to_csv("TX_County_Political_Panel_2000_2024.csv",index=False)

# regenerate xlsx with Panel + Summary + Coverage
summ=p.select_dtypes("number").drop(columns=["year"],errors="ignore").describe().T.round(3).reset_index().rename(columns={"index":"Variable"})
cov=p.groupby("year").apply(lambda g:(g.notna().mean()*100).round(0)).reset_index() if False else \
    pd.DataFrame({"Variable":p.columns,**{str(y):(p[p.year==y].notna().mean()*100).round(0).values for y in sorted(p.year.unique())}})
with pd.ExcelWriter("TX_County_Political_Panel_2000_2024.xlsx",engine="openpyxl") as xl:
    p.to_excel(xl,index=False,sheet_name="Panel")
    summ.to_excel(xl,index=False,sheet_name="Summary")
    cov.to_excel(xl,index=False,sheet_name="Coverage")
print("rebuilt CSV + XLSX. income non-null %.1f%% poverty non-null %.1f%%"%(100*p.median_household_income.notna().mean(),100*p.poverty_rate.notna().mean()))
print(p[p.fips=='48453'][['year','median_household_income','poverty_rate']].to_string(index=False))
