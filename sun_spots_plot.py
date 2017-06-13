#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
from datetime import datetime
from time import time, strftime, localtime, sleep
from numpy import array, arange
import matplotlib.pyplot as plt

import ftplib
from os import chdir

from  subprocess import Popen, PIPE, STDOUT
from  shlex import split


sins_years = 7
#Колличество лет, которые нужно выводить в граффике, пока что поставил 7.

spots = {}
key = ['date','N','fi','l','r/R','S','Smm','Smaxi','n','?','W','year','month','day']
manth = {'янв. ':1,
         'февр.':2,
         'марта':3,
         'апр. ':4,
         'мая  ':5,
         'июня ':6,
         'июля ':7,
         'авг. ':8,
         'сент.':9,
         'окт. ':10,
         'нояб.':11,
         'дек. ':12}
file_data = {}

def sendToFTP(filename1):

    '''
    ftp = ftplib.FTP('158.250.29.123')
    ftp.login('sun', 'pasworld')
    ftp_server_dir = '/usr/local/solar/apache/htdocs/web/Soln_Dann/'
    ftp_file_dir = '/home/pa_antya/spbu/sun_spots'
    '''
    ftp = ftplib.FTP('www.solarstation.ru')
    ftp.login('sun', 'pasworld')
    ftp_server_dir = '/www/solarstation.ru/lastdata/Graphs/'
    ftp_file_dir = '/home/pa_antya/spbu/sun_spots/'
    ftp.cwd(ftp_server_dir)
    chdir(ftp_file_dir)
    print(ftp.retrlines('LIST'))
    file = open(filename1, 'w')
    print('send to ftp: begin')
    #ftp.storlines('STOR_'+ filename1, file.read)

    ftp.retrbinary('Wolf_NS.gif', file.read) #скачивание файлов и запись в filename
    print('send to ftp: done.')
    file.close()
    ftp.quit()


def printBase():
    for i in spots:
        for j in spots[i]:
            for l in spots[i][j]:
                print('{} {} {}:'.format(i,j,l))
                for k in spots[i][j][l]:
                    print('{}'.format(k))
            print()

def summSpotsDay(a,st):
    summ_W = 0
    for i in a:
        summ_W += i[st]
    return summ_W

def summSpotsMonth(a,st):
    summ_W_m = 0
    for i in a:
        summ_W_m += summSpotsDay(a[i],st)
    return summ_W_m / len(a)

def creatAndSendPlot():
    fig, ax = plt.subplots()
    #plt.axes([0.05, 0.05, 1, 1])
    fig.subplots_adjust(left=0.085, bottom=0.1, top=0.85, right = 0.985)

    #plt.figure(1, figsize=(10, 8))
    x = array([datetime(i, j, k) for i in file_year[-sins_years:] for j in spots[i] for k in spots[i][j]])
    y = array([summSpotsDay(spots[i][j][k],'W') for i in file_year[-sins_years:] for j in spots[i] for k in spots[i][j]])
    ax.plot(x,y,linewidth=0.5,label='Daily',linestyle='-', color = '#46A0A6',markersize=6)

    x = array([datetime(i, j, 1) for i in file_year[-sins_years:] for j in spots[i]])
    y = array([summSpotsMonth(spots[i][j],'W') for i in file_year[-sins_years:] for j in spots[i]])
    ax.plot(x,y,linewidth=1.5,label='Monthly',linestyle='-', color = '#361686',markersize=6)
    del(x)
    del(y)

    #color = '#5636A6, 'Monthly'
    ax.legend(loc=2) # upper left corner

    ax.set_xlabel('Year', fontsize=16)
    ax.set_ylabel('W', fontsize=16)
    ax.set_title('Kislovodsk Wolf number'.format())

    #fig.show()
#    plt.grid(True)
    plotImg = './{}.png'.format('KWN')
    fig.savefig(plotImg, format='png')#, dpi=600)
    #fig.savefig('./{}.png'.format('Kislovodsk Wolf number grid'), dpi=600)
    plt.close(fig)
    sendToFTP(plotImg[2:])
    del(plotImg)

def datParser(f,spots_all):
    file = open(f,'r')
    for line in file:
        line_in = line
        if len(line_in) > 20:
            if line_in[26] == ' ':
                line_in = line_in[:24] + '0.0' + line_in[27:]
            if line_in[32] == ' ':
                line_in = line_in[:30] + '0.0' + line_in[33:]
        line_list = line_in.strip().split()
        spot = {}
        for i in arange(len(line_list)):
            if i != 9 and i != 0:
                spot[key[i]] = float(line_list[i])
            else:
                spot[key[i]] = line_list[i]
        spot['year'] = int(line_list[0][:4])
        spot['month'] = int(line_list[0][4:6])
        spot['day'] = int(line_list[0][6:8])
        if len(line_list) == 1:
            for i in arange(len(line_list)):
                if i != 0:
                    spot[key[i]] = -1
                else:
                    spot[key[i]] = line_list[i]
            spot['W'] = 0

        else:
            spot['W'] = int(spot['n']) + 10
            spot['N'] = int(spot['N'])
            spot['n'] = int(spot['n'])

        '''
        for i in spot:
            print('{} = {}'.format(i,spot[i]),end=', ')
        print()
        '''
        spots_all.append(spot)
    file.close()

def setBaseSpotsForDate(spots_all):
    for i in spots_all:
        if int(i['date'][:4]) not in spots:
            spots[int(i['date'][:4])] = {}
        if int(i['date'][4:6]) not in  spots[int(i['date'][:4])]:
            spots[int(i['date'][:4])][int(i['date'][4:6])] = {}
        if int(i['date'][6:8]) not in spots[int(i['date'][:4])][int(i['date'][4:6])]:
            spots[int(i['date'][:4])][int(i['date'][4:6])][int(i['date'][6:8])] = []

        if i not in spots[int(i['date'][:4])][int(i['date'][4:6])][int(i['date'][6:8])]:
#            if i['N'] not in [j['N'] for j in spots[int(i['date'][:4])][int(i['date'][4:6])][int(i['date'][6:8])]]:
            spots[int(i['date'][:4])][int(i['date'][4:6])][int(i['date'][6:8])].append(i)
        else:
            print('0'.format(i,),end='')


def editFileData(file_data, file_data_tmp, file_year, sins_years):
    for i in file_data_tmp:
        if i not in file_data:
            file_data[i] = {}
        for j in file_data_tmp[i]:
            if j not in file_data[i]:
                file_data[i][j] = {}
            file_data[i][j] = file_data_tmp[i][j]
    file_data_tmp = {}
    filee = ['k{}.dat'.format(i) for i in file_year[-sins_years:]]
    spots_all = []
    for f in filee:
        if f.find('.dat') != -1 and f[-1] != '~':
            datParser(f,spots_all)
    setBaseSpotsForDate(spots_all)

def isChengFileData(file_data, file_data_tmp, file_year, sins_years):
    filee = ['k{}.dat'.format(i) for i in file_year[-sins_years:]]
    for i in filee:
        if i not in file_data:
            print('file_date ещё пуста. Нет файла {} в ней'.format(i))
            return True
    for i in filee:
        if file_data[i]['day'] != file_data_tmp[i]['day'] or \
                        file_data[i]['size'] != file_data_tmp[i]['size'] or \
                        file_data[i]['h'] != file_data_tmp[i]['h'] or \
                        file_data[i]['min'] != file_data_tmp[i]['min'] or \
                        file_data[i]['month'] != file_data_tmp[i]['month'] or \
                        file_data[i]['year'] != file_data_tmp[i]['year']:
            print('Файл {} изменили.'.format(i))
            return True
    return False


def parserFold(file_data_tmp ,file_year):
    manth = {1:'янв. ',
             2:'февр.',
             3:'марта',
             4:'апр. ',
             5:'мая  ',
             6:'июня ',
             7:'июля ',
             8:'авг. ',
             9:'сент.',
             10:'окт. ',
             11:'нояб.',
             12:'дек. '}
    # содержит :'year', 'month', 'day', 'h', 'min','file'
    cmd = "ls -lt"
    args = split(cmd)
    p = Popen(args, stdout=PIPE, stderr=STDOUT)
    files = p.communicate()[0].decode('utf-8').rstrip('\n').split('\n')[1:]
    for f in files:
        if (f[54:].find('.dat') != -1 and f[-1] != '~'):
            data = {}
            #print(f)
            if f[49] == ':':
                data['year'] = int(strftime('%Y',localtime(time())))
                data['h'] = int(f[47:49])
                data['min'] = int(f[50:52])
            else:
                data['year'] = int(f[46:51])
            data['size'] = int(f[30:37])
            data['month'] = 0
            for i in manth:
                if f[38:43] == manth[i]:
                    data['month'] = i
            data['day'] = f[44:46]
            data['file'] = f[53:]
            file_data_tmp[data['file']] = data
    for i in file_data_tmp:
        file_year.append(int(i[1:i.find('.')]))
    file_year.sort()


'''
for i in spots[2016][8][12]:
    print(i)
print(len(spots[2016][8][12]))
for i in spots_all[-7:-1]:
    print(i)
'''
it = 0
file_data_tmp = {}
while True:
    it = it + 1
    file_year = []
    parserFold(file_data_tmp,file_year)
    if isChengFileData(file_data, file_data_tmp, file_year, sins_years):
        editFileData(file_data, file_data_tmp, file_year, sins_years)
        print('edit dat, and creatPlot')
        creatAndSendPlot()
        print('complite 100%')
    '''
    if it % 120 == 0:
        print(it / 12)
        '''
    sleep(5)#(60*60)# Время до следующей проверки папки
