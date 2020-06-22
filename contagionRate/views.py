from django.shortcuts import render
from django.http import HttpResponse
import requests, re, math
import matplotlib.pyplot as plt 
import numpy as np; np.random.seed(1)
import matplotlib.pyplot as plt, mpld3
from mpld3 import plugins
from datetime import datetime, timedelta
from threading import Thread


# Create your views here.

def index(request):

  print("start")

  # Define some CSS to control our custom labels
  css = """
  table
  {
    border-collapse: collapse;
  }
  th
  {
    color: #ffffff;
    background-color: #000000;
  }
  td
  {
    background-color: #FFA500;
  }
  table, th, td
  {
    font-family:Arial, Helvetica, sans-serif;
    font-size:20;
    border: 1px solid black;
    text-align: right;
  }
  """

  # Set headers
  
  headers = requests.utils.default_headers()
  headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

  from bs4 import BeautifulSoup

  results = {}

  

  def scrape_worldometers():
    url_alt = 'https://www.worldometers.info/coronavirus/country/israel/'
    req = requests.get(url_alt, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    #print(soup)
    mydivs = soup.find_all("div", class_="number-table-main")
    #print(mydivs)
    divs = [ele.text.strip() for ele in mydivs]
    last_stat = divs[0]
    #print(last_stat)

    last_stat = re.sub(r'<div>.*>([\d,])<.*</div>', r'\1', last_stat, 0).replace(',', '')
    #print(last_stat)
    results['worldometers'] = last_stat


  def scrape_worldometers2():
    url_alt = 'https://www.worldometers.info/coronavirus/country/israel/'
    req = requests.get(url_alt, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    #print(soup)
    all_scripts = soup.find_all('script')
    dates = ""
    values = ""
    print(type(all_scripts))
    for script in all_scripts:
      print(type(script))
      print(type(script.text))
      print("in scripts for loop)")
      if script.text.find(r'graph-active-cases-total'):
        print(script.text)
        script_text = "".join(script.text)
        dates = re.sub(r'.*categories:\s*\[(.*?)\].*',  r'\1', script_text, flags=re.DOTALL)
        values = re.sub(r'.*data:\s*\[(.*?)\].*',  r'\1', script_text, flags=re.DOTALL)
        print (dates)
        print (values)

    d = dates.replace('"', '').split(',')
    v = values.split(',')
    dv = []
    for i in range(len(d)):
      dv.append((d[i], v[i]))

    results['worldometers2'] = dv
    #print(results['worldometers2'])

    #print(results['worldometers2']

    




  threads = []
  #process = Thread(target=scrape_wikipedia, args=[])
  #process.start()
  #threads.append(process)
  #process = Thread(target=scrape_worldometers, args=[])
  #process.start()
  #threads.append(process)
  process = Thread(target=scrape_worldometers2, args=[])
  process.start()
  threads.append(process)

  for process in threads:
    process.join()

  print("after processes")

  #print('w'+results['worldometers'])
  #print(results['mako'])
  ##last_stat = str(max(int(results['worldometers']), int(results['mako'])))
  last_stat = results['worldometers']
  #print(last_stat)
  #data = results['wikipedia']
  data2 = results['worldometers2']

  #print(data)
  #print(data2)


  
  realDatesList = []
  datesList = []
  numSickList = []

  
  print("before for item in data2")
  print(data2)
  for item in data2:
    print(item)
    #print(item[0])
    #print(item[1])
    fullDate = item[0]
    fullDate = "2020 " + fullDate
    real_date = datetime.strptime(fullDate, "%Y %b %d")
    date = re.sub(r'\d+-(\d+)-(\d+).*', r'\2-\1', str(real_date), 0)
    start_day = datetime.today() - timedelta(days=30)
    numSick = item[1]
    numSick = re.sub(r'([\d,]+).*', r'\1', numSick, 0).replace(',', '')
    print(item)
    if real_date >= start_day:
        #print(real_date)
        realDatesList.append(real_date)
        datesList.append(date)
        numSickList.append(numSick)



  #print(datesList)
  #print(numSickList)

  print("have dates and numbers")


  plt.rcParams.update({'font.size': 16})
  DAY_RATE=3
  START_RANGE=0

  sickRate=[]
  labels=[]
  for i in range(START_RANGE, len(numSickList)-DAY_RATE):
      sickRate.append( int(numSickList[i+DAY_RATE]) / int(numSickList[i]))
      #print(datesList[i+DAY_RATE] + " : " + numSickList[i+DAY_RATE] + "/" + numSickList[i] + "= " + str(sickRate[i-4]))
      labels.append("<table><tr><td>" + numSickList[i+DAY_RATE] + "</td></tr><tr><td>" + numSickList[i] + "</td></tr><tr><td><b>" + str(round(sickRate[i],3)) + "</b></td></tr></table>")
      i=i+1

  # x axis values
  x = datesList[START_RANGE+DAY_RATE:len(datesList)]
  # corresponding y axis values 

  y = sickRate
  #print(x)
  #print(y)


  # plotting the points  
  graph = plt.plot(x, y, color='green', linestyle='dashed', linewidth = 3, 
            marker='o', markerfacecolor='blue', markersize=20) 
    

  # setting x and y axis range 
  plt.ylim(0.8, 2.0) 
  plt.xlim(0,len(datesList)-START_RANGE) 


  #fig, ax = plt.subplots()

  ax = plt.gca()
  ax.set_xticklabels(x)
  ax.set_xticks(x)
    
  # naming the x axis 
  plt.xlabel('x - Date')  
  # naming the y axis 
  plt.ylabel('y - 3 day rate') 
    
  # giving a title to my graph 
  current_sickRate = round(sickRate[len(sickRate)-1], 3)
  current_sick = numSickList[len(numSickList)-1]
  #future_sick = float(current_sick) * math.pow(current_sickRate, 10)

  '''
  last = len(numSickList)-1
  factor_two = int(current_sick)/2
  past_sick = numSickList[last-1]
  i = 0
  j = last-1
  while int(past_sick) > int(factor_two) and j>=0:
    #print('past:'+past_sick)
    i+=1 
    j-=1
    past_sick = numSickList[j]

  p = last-i
  #print( 'factor_two: ' +  str(factor_two))
  #print( 'past_sick: ' +  str(past_sick))
  #print("i: " + str(i))
  days_to_multiple = i
  mod = int(factor_two) - int(past_sick)
  #print('mod: ' + str(mod))

  avg = (float(current_sick)- float(numSickList[p]))/float(i)
  #print('numSickList[p]: ' + numSickList[p])
  #print('avg : ' + str(avg))
  factor_mod = mod/avg
  #print('factor_mod : ' + str(factor_mod))

  total_mult_days = float(days_to_multiple) + round(factor_mod, 2)
  #ax.set_title('[ 3-day Contagion Rate: ' + str(current_sickRate) + ']  [ In 30 days, total of: ' + f'{round(future_sick):,}' + ' sick ]  [ Number of sick multiplies every ' + str(total_mult_days) + ' days ]')
  '''
  
  today_sick = float(current_sick)
  yesterday_sick = float(numSickList[len(numSickList)-2])
  next_day_sick = float(current_sick)
  day_by_day_sickRate = today_sick/yesterday_sick
  #print(next_day_sick)
  i = 0
  while next_day_sick < 2.0 * float(current_sick) :
    i += 1
    next_day_sick = next_day_sick * day_by_day_sickRate
    #print(next_day_sick)

  total_mult_days = i
  future_sick = float(current_sick) * math.pow(day_by_day_sickRate, 30)

  ax.set_title('[ PHASE 2 ACTIVE CASES ] [ Contagion Rate- 3-day: ' + str(current_sickRate) + ' 1-day: ' + str(round(day_by_day_sickRate,3)) + ' ]  [ In 30 days, total of: ' + f'{round(future_sick):,}' + ' (+ ' + str(round(float(future_sick) - float(current_sick))) + ')  sick ]  [ Number of sick multiplies every ' + str(total_mult_days) + ' days ]')
        
  fig = plt.gcf()

  fig.set_size_inches(18.5, 7.5) 



  # function to show the plot 
  #print(mpld3.fig_to_html(fig))
  tooltip = plugins.PointHTMLTooltip(graph[0], labels,
                                      voffset=-80, hoffset=30, css=css)
  plugins.connect(fig, tooltip)

  #mpld3.show() 

  
  htmlText = ''' <html>\n<head> 
        <meta equiv="refresh" content="300">
        <meta name="MobileOptimized" content="width">
        <meta name="HandheldFriendly" content="true">
        <meta name="viewport" content="width=device-width">
        <meta name="viewport" content="width=device-width, initial-scale=1">'''
        
  htmlText += mpld3.fig_to_html(fig)
  htmlText += '</head><body></body></html>'
  
  #print(htmlText)
  return HttpResponse(htmlText)

#index("aaa")