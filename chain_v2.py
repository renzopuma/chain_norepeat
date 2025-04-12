import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
st.set_page_config(layout="wide")
st.title("Chain")

coef_path=[st.secrets['chain_path0'], 
           st.secrets['chain_path1'], 
           st.secrets['chain_path2'], 
           st.secrets['chain_path3'], 
           st.secrets['chain_path4'], 
           st.secrets['chain_path5']]

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def load_data():
    dfs = {}
    i = 0
    for df in coef_path:
        dfs[i] = conn.read(spreadsheet=df)
        i +=1
    data = pd.concat(dfs).reset_index(drop=True)
    data = data[['code_country', 'year', 'num_sector', 'to_sector', 'sec_']]
    data['rank_dws'] = data.groupby(['code_country', 'year', 'num_sector'])['sec_'].rank(method="dense", ascending=False)
    data['rank_ups'] = data.groupby(['code_country', 'year', 'to_sector'])['sec_'].rank(method="dense", ascending=False)
    return data
coef_df = load_data()

def loop_buster_dws(s, t, sec_list, f1, f2, f3, f4, f5):
    c = f1.num_sector[s - 1]      
    if (c == t) or (t in sec_list):
        t = f2.to_sector[s - 1]
        if (c == t) or (t in sec_list):
            t = f3.to_sector[s - 1]
            if (c == t) or (t in sec_list):
                t = f4.to_sector[s - 1]
                if (c == t) or (t in sec_list):
                    t = f5.to_sector[s - 1]
    return t


def loop_buster_ups(s, t, sec_list, k1, k2, k3, k4, k5):
    c = k1.to_sector[s - 1]       
    if (c == s) or (s in sec_list):
        s = k2.num_sector[t - 1]
        if (c == s) or  (s in sec_list):
            s = k3.num_sector[t - 1]
            if (c == s) or (s in sec_list):
                s = k4.num_sector[t - 1]
                if (c == s) or (s in sec_list):
                    s = k5.num_sector[t - 1]
    return s


def dws(d, c1, f1, f2, f3, f4, f5):
    db = {}
    ds = {}
    v1 = ['c'] + d
    for j in range(len(c1)):
        c = f1.num_sector[j]
        db[j + 1] = [c]
        ds[v1[0]] = c
        for i in range(len(d)):
            s = v1[i]
            t = v1[i+1]   
            ds[t] = f1.to_sector.loc[ds[s]-1]
            ds[t] = loop_buster_dws(ds[s], ds[t], db[j+1], f1, f2, f3, f4, f5)
            #res[j+1].append((ds[s], ds[t]))
            db[j+1].append(ds[t])
                  
    df = pd.DataFrame.from_dict(db,orient='index', columns = v1)
    return df    


def ups(u, c1, k1, k2, k3, k4, k5):
    res = {}
    db = {}
    us = {name: pd.DataFrame() for name in u}
    v1 = ['c'] + u
    for j in range(len(c1)):
        c = k1.to_sector[j]
        u1 = k1.num_sector[c - 1]
        db[j+1] = [u1, c]
        us[u[0]] = u1
        for i in range(len(u)-1):
            t = u[i]
            s = u[i+1]   
            us[s] = k1.num_sector[us[t]-1]
            us[s] = loop_buster_ups(us[s], us[t], db[j+1], k1, k2, k3, k4, k5)
            #res[j+1].append((us[s], us[t]))
            db[j+1].insert(0,us[s])
    
    u.reverse()              
    df = pd.DataFrame.from_dict(db,orient='index', columns = u+['c'])
    return df   


def analisis(selected_ctry, selected_year):

    df1 = coef_df[coef_df["code_country"].isin(selected_ctry) & coef_df["year"].isin(selected_year)]
    
    f1 = df1[df1["rank_dws"]==1].reset_index(drop=True)
    f2 = df1[df1["rank_dws"]==2].reset_index(drop=True)
    f3 = df1[df1["rank_dws"]==3].reset_index(drop=True)
    f4 = df1[df1["rank_dws"]==4].reset_index(drop=True)
    f5 = df1[df1["rank_dws"]==5].reset_index(drop=True)

    k1 = df1[df1["rank_ups"]==1].sort_values(by=['to_sector']).reset_index(drop=True)
    k2 = df1[df1["rank_ups"]==2].sort_values(by=['to_sector']).reset_index(drop=True)
    k3 = df1[df1["rank_ups"]==3].sort_values(by=['to_sector']).reset_index(drop=True)
    k4 = df1[df1["rank_ups"]==4].sort_values(by=['to_sector']).reset_index(drop=True)
    k5 = df1[df1["rank_ups"]==5].sort_values(by=['to_sector']).reset_index(drop=True)


    c1 = df1.num_sector.unique()


    d = ['d1','d2', 'd3', 'd4', 'd5', 'd6', 'd7']
    u = ['u1','u2', 'u3', 'u4', 'u5', 'u6', 'u7']

    df = dws(d, c1, f1, f2, f3, f4, f5)
    df2 = ups(u, c1, k1, k2, k3, k4, k5)

    tot = pd.merge(df, df2, on='c')
    tot = tot[u + ['c'] + d]

    label_map = {
        1 : 'Agr',
        2 : 'Fish',
        3 : 'Minning',
        4 : 'Food',
        5 : 'Textiles',
        6 : 'Wood_pper',
        7 : 'Pet_Chems',
        8 : 'Metal-Prod',
        9 : 'Elec Eq',
        10: 'Trans Eq',
        11: 'Manufct',
        12: 'Recyclng',
        13: 'Utilities',
        14: 'Construct',
        15: 'Main_Rpair',
        16: 'Whlsale',
        17: 'Retail',
        18: 'Rest_Hots',
        19: 'Transport',
        20: 'Telecom',
        21: 'Finance',
        22: 'Public',
        23: 'Educ_Hlt'
    }


    for i in u + ['c'] + d: 
        tot[i] = tot[i].map(label_map)
    #return f1, f2, f3, f4, f5
    return tot

country_list = coef_df['code_country'].unique()
years = coef_df['year'].unique()

rws1 = st.columns(2)

with rws1[0]:
    selected_ctry = st.selectbox("Select a country", country_list, 1)
    selected_ctry = [selected_ctry]

##Select bench
with rws1[1]:
    selected_year = st.selectbox("Select a year", years, 1)
    selected_year = [selected_year]
    
#f1, f2, f3, f4, f5 = analisis(selected_ctry, selected_year)
tot = analisis(selected_ctry, selected_year)
container3 = st.container(height=950)
with container3:
    st.write(' ')
    st.write(' ')
    #st.dataframe(f1, width = 1500 ,height=850)
    st.dataframe(tot, width = 1500 ,height=850)

#st.dataframe(f2, width = 1500 ,height=850)
#st.dataframe(f3, width = 1500 ,height=850)
#st.dataframe(f4, width = 1500 ,height=850)
#st.dataframe(f5, width = 1500 ,height=850)