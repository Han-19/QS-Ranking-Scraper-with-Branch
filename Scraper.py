import numpy as np
import time
from bs4 import BeautifulSoup as bs
import pandas as pd

from seleniumrequests import Firefox



class QS_SCAPER():
    def __init__(self):
        self.branch_list = ['art-design',
                            'business-management-studies', 
                            'computer-science-information-systems', 
                            'data-science',
                            'physics-astronomy', 
                            'politics',]
        self.df = pd.DataFrame(columns=['UNIVERSITY', 'RANK','Country','City/State', *self.branch_list])
        
        URL_main = "https://www.topuniversities.com/university-rankings/world-university-rankings/2024?&page="
        
        self.all_uni, self.all_rank = self.get_uni(URL_main,pages=50)
        
        self.parse_uni(self.all_uni,self.all_rank,'RANK')
        self.df.set_index('UNIVERSITY',inplace=True)
        
        URL_prefix =lambda branch:  "https://www.topuniversities.com/university-rankings/university-subject-rankings/2023/{}?&page=".format(branch)
        
        
        for branch in self.branch_list:
            self.unilist_raw,self.rank_list = self.get_uni(URL_prefix(branch),pages=25)

            self.parse_uni(self.unilist_raw,self.rank_list,branch)


    def parse_uni(self,raw,ranks,branch):

        for ind in range(len(raw)):
            name_loc =raw[ind].text.replace("""QS Stars\n\n\nMore Details""","").strip().split("\n\n\n")
            try:
                pdseries = pd.DataFrame({'UNIVERSITY':name_loc[0],
                                    branch:ranks[ind].text.strip("="),
                                    'Country':name_loc[1].split(", ")[1],
                                    'City/State':name_loc[1].split(", ")[0]},index=[name_loc[0]])
            except IndexError:
                continue
            if branch !="RANK":
                #print(ranks[ind].text)
                try :
                    self.df.loc[name_loc[0]][branch]= ranks[ind].text
                except KeyError:
                    pdseries = pdseries.drop('UNIVERSITY',axis=1)
                    self.df = pd.concat([self.df,pdseries],axis=0)
            else:
                self.df.loc[self.df.shape[0]] = pdseries.loc[name_loc[0]]
        
    def get_uni(self,url_prefix,pages=10):
        
        uni_list = []
        uni_rank_list = []
        driver = Firefox()
        for n in range(pages):
            time.sleep(0.5)
            
            driver.get(url_prefix+str(n))
            time.sleep(2)
            soup = bs(driver.page_source, 'html.parser')
            uni_details= soup.find_all('div',attrs={'class':'univ-details-right-pos'})
            uni_rank= soup.find_all('div',attrs={'class':'_univ-rank mw-100 hide-this-in-mobile-indi'})
            uni_list+=uni_details
            uni_rank_list+=uni_rank
        driver.close()
        return uni_list ,uni_rank_list




scraper =QS_SCAPER()

scraper.df.to_excel("BIG_UNI_LIST.xlsx")

