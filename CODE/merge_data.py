import sys
import string
import re
import math
import pandas as pd

path_A = '../DATA/imdb3_neg_nan.csv'
path_B = '../DATA/thenumbers3_neg_nan.csv'
path_M = '../DATA/MatchPredctionsOnAllTuplePairs.csv'
A = pd.read_csv(path_A)
B = pd.read_csv(path_B)
Matches = pd.read_csv(path_M)
print(len(Matches))
#Matches.head()

def merge_title(title1, title2):
    #take the longer title
    title1= title1.item()
    title2=title2.item()
    l1 = len(title1)
    l2= len(title2)
    res = title1 if l1>l2 else title2
    return res

def merge_year(year1, year2):
    #if value form B exists, take it else from A
    if year2.item() != -1:
        return year2.item()
    return year1.item()

def merge_mpaa(mpaa1,mpaa2):
    mpaa1=mpaa1.item()
    mpaa2=mpaa2.item()
    return mpaa1 if mpaa1 != "Not Rated" and mpaa1 != "-1" else mpaa2

def merge_runtime(rt1,rt2):
    rt1=rt1.item()
    rt2=rt2.item()
    regex = re.compile('[^0-9]')
    a=regex.sub('',rt1)
    b=regex.sub('',rt2)
    rt1 = int(a)
    rt2 = int(b)
    rt = rt1 if rt1>rt2 else rt2
    return str(rt)+" min"

def split_and_union(g1,g2):
    g1 = g1.lower()
    g2= g2.lower()
    g1 = g1.split(",")
    g2= g2.split(",")
    final_list = g1+g2
    final_list = set(final_list)
    
    return ','.join(final_list)

def merge_genres(g1,g2):
    g1=g1.item()
    g2=g2.item()
    if g1=="-1": return g2
    if g2=="-1": return g1
    return split_and_union(g1,g2)

def merge_director_name(dir1,dir2):
    dir1=dir1.item()
    dir2=dir2.item()
    if dir1=="-1": return dir2
    if dir2=="-1": return dir1
    return split_and_union(dir1,dir2)

def merge_stars(stars1, stars2):
    stars1=stars1.item()
    stars2=stars2.item()
    if stars1=="-1": return stars2
    if stars2=="-1": return stars1
    return split_and_union(stars1,stars2)

def merge_gross(grossL, grossR):
    grossL=grossL.item()
    grossR=grossR.item()
    #remove the '$' or any other special character from gross value of right table-
    #is of the form "$1234,123"
    if grossR == "-1" and grossL == "-1":
        return grossL
    grossRint=grossLint=0
    if grossR != "-1":
        grossclean2 = ''.join(ch for ch in grossR if ch in string.digits)
        grossRint = int(grossclean2)
    #grossL is of the form "$4.4M"
    if grossL != "-1":
        dictL={'M':1e6,'B':1e9,'T':1e12,'k':1e3, 'K':1e3}
        grossL.replace(" ","")
        if grossL[-1] in dictL:
               multfact=dictL[grossL[-1]]
        grossclean1 = ''.join(ch for ch in grossL if ch in string.digits)
        grossLint = float(grossclean1)
        grossLint *= multfact
    f = grossLint if grossLint>grossRint else grossRint
    return "$"+str(f)

# Combine a pair of tuple into a single tuple
def combine(lt,rt):    
    a = merge_title(lt.title,rt.title)
    b = merge_year(lt.year,rt.year)
    c=merge_mpaa(lt.mpaa,rt.mpaa)
    d=merge_runtime(lt.runtime,rt.runtime)
    e=merge_genres(lt.genres,rt.genres)
    f=merge_director_name(lt.director,rt.director)
    g=merge_stars(lt.stars,rt.stars)
    h=merge_gross(lt.gross,rt.gross)
    return (lt.id.item(),a,b,c,d,e,f,g,h)

#pick each matching tuple pair from M and take out corresponding
#tuples from A and B, and pass them through combine method above
finalist=[]
for row in Matches.itertuples():
    #print(row)
    lid = row.ltable_id
    rid = row.rtable_id
    ltup = A.loc[(A["id"]==lid)]
    rtup = B.loc[(B["id"]==rid)]
    tup = combine(ltup,rtup)
    # Append to final table E
    finalist.append(tup)
df = pd.DataFrame(finalist, columns=['id', 'title', 'year', 'mpaa','runtime','genres','director','stars','gross'])
#Save to file
df.to_csv('../DATA/integrated_table.csv', index=False)
