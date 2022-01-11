import os
import re

import numpy as np
import requests
import pandas as pd
import seaborn as sns
from fpdf import FPDF
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib import image as mpimg

sns.set_style("darkgrid")
colors = sns.color_palette('pastel')[0:5]
id_stephen_curry = str(3975)
id_kevin_durant = str(3202)
IDs = {id_stephen_curry : 'Stephen Curry', id_kevin_durant : 'Kevin Durant'}
root = os.getcwd()+ '//'

def list_2_int(lt):
    return [round(float(x)) for x in lt]

def append_row(df, td_list):
    new_row = {'DATE': td_list[0].text, 'OPP': td_list[1].text, 'RESULT': td_list[2].text, 'MIN': td_list[3].text,
               'FG': td_list[4].text, 'FG%': td_list[5].text, '3PT': td_list[6].text, '3P%': td_list[7].text, 'FT': td_list[8].text, 'FT%': td_list[9].text,
               'REB': td_list[10].text, 'AST': td_list[11].text, 'BLK': td_list[12].text, 'STL': td_list[13].text, 'PF': td_list[14].text, 'TO': td_list[15].text, 'PTS': td_list[16].text}
    df = df.append(new_row, ignore_index=True)
    return df

def split_fg(s):
    a, b = zip(*(x.split("-") for x in s))
    return list_2_int(list(a)), list_2_int(list(b))

def slice_3pt(arg):
    return arg.split('-')[1]

def scrap_gamelogs_by_id(player_IDs):
    years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    for id, name in player_IDs.items():
        if os.path.exists(os.getcwd()+ '//' + '{}.xlsx'.format(id)):
            print('player {} gamelog sheet already exists'.format(id))
        else:
            df = pd.DataFrame(columns=['DATE', 'OPP', 'RESULT', 'MIN', 'FG', 'FG%', '3PT', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS'])
            for year in years:
                soup = BeautifulSoup(requests.get('https://www.espn.com/nba/player/gamelog/_/id/{}/type/nba/year/{}'.format(id, year)).text, 'html.parser')
                rows = soup.find_all(('tr', {'class': ['Table__TR Table__TR--sm Table__even', 'filled Table__TR Table__TR--sm Table__even']}))
                for row in rows:
                    td_list = row.find_all('td')
                    try:
                        match = re.match('[a-z|A-Z]{4}', td_list[0].text)
                        if match == None:
                            df = append_row(df, td_list)
                    except IndexError:
                        pass
            df["3PT_SHOTs"] = df["3PT"].apply(lambda x: slice_3pt(x))
            df["PLAYER"] = name
            df.to_excel('{}.xlsx'.format(id))

def visualize_histogram_3pt(player_IDs):
    for id, name in player_IDs.items():
        value = pd.read_excel('{}.xlsx'.format(id))['3P%']
        ax = sns.distplot(value, bins=[0, 10, 20, 30, 40, 50 ,60 ,70, 80, 90, 100], kde=True, label=name)
    ax.legend()
    fig = ax.get_figure()
    fig.set_size_inches(8.0, 4.5)
    if os.path.exists(root + 'hist.png') == False:
        fig.savefig(root + 'hist.png')
    plt.show()

def visualize_quantity_3pt(player_IDs):
    FG_lt = []
    SM_lt = []
    for player_ID in player_IDs:
        FG = pd.read_excel('{}.xlsx'.format(player_ID))['3PT']
        FG, SM = split_fg(FG)
        Shots_Made = sum(FG)
        Shots_Missed = sum(SM) - sum(FG)
        FG_lt.append(Shots_Made)
        SM_lt.append(Shots_Missed)
    plt.bar(list(player_IDs.values()), FG_lt, alpha=0.6, width=0.7, color='royalblue', label='Shots_Made')
    plt.bar(list(player_IDs.values()), SM_lt, alpha=0.6, width=0.7, color='darkorange', label='Shots_Missed', bottom=FG_lt)
    if os.path.exists(root + 'bar.png') == False:
        plt.savefig(root + 'bar.png')
    plt.legend()
    plt.show()

def visualize_scatter_3pt(player_IDs):
    df = pd.DataFrame()
    for id, name in player_IDs.items():
        df = pd.concat([df, pd.read_excel('{}.xlsx'.format(id))])
    sns.lmplot(x='3PT_SHOTs', y="3P%", data=df, hue='PLAYER')
    if os.path.exists(root + 'scat.png') == False:
        plt.savefig(root + 'scat.png')
    plt.show()

def generate_analytics_report():
    width = 210
    height = 297
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(5, 10, f'Curry v.s. Durant: 3PT Shots Stability Analysis & Reporting')
    pdf.image(root + 'hist.png', 5, 20, width - 20)
    pdf.image(root + 'bar.png', 10, 130, width / 2 - 5)
    pdf.image(root + 'scat.png', width / 2, 130, width / 2 - 5)
    pdf.output('analytics_report.pdf', 'F')

if __name__ == '__main__':
    scrap_gamelogs_by_id(IDs)
    visualize_histogram_3pt(IDs)
    visualize_quantity_3pt(IDs)
    visualize_scatter_3pt(IDs)
    generate_analytics_report()






