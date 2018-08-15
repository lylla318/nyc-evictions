#!/usr/bin/env python

import re
import json
import io
import csv
import sys
from pprint import pprint
from collections import defaultdict
import mysql.connector
import numpy as np
from pathlib import Path


# dynamic terminal printing -- lookup


class Parser:

  def __init__(self, password):

    self.password = password
    # self.table = table
    # self.year = year
    # self.csv_read = csv_readls



    self.tax_rates = {"19": {"tc1":0.21861, "tc234":0.12690}, 
                      "18": {"tc1":0.20385, "tc234":0.12719},
                      "17": {"tc1":0.19991, "tc234":0.12892}, 
                      "16": {"tc1":0.19554, "tc234":0.12883},
                      "15": {"tc1":0.19157, "tc234":0.12855}, 
                      "14": {"tc1":0.19191, "tc234":0.13145},
                      "13": {"tc1":0.18569, "tc234":0.13181}, 
                      "12": {"tc1":0.18205, "tc234":0.13433},
                      "11": {"tc1":0.17364, "tc234":0.13353}, 
                      "10": {"tc1":0.17088, "tc234":0.13241},
                      "09": {"tc1":0.16196, "tc234":0.12596}
                      }

    # self.query_by_bble()
    # self.get_inwood_properties()
    # self.get_units_by_zip()
    # self.get_monthly_evictions()
    # self.get_units_by_building()
    # self.get_units_per_zip()
    results = defaultdict(float)
    years = ["09","10","11","12","13","14","15","16","17","18","19"]
    for i in range(len(years)-1):
      results[years[i+1]] = self.get_inwood_increases(years[i],years[i+1])
    print("***********************************************")
    for k in results.keys():
      print(k,results[k])
       



  def get_inwood_increases(self, y1, y2):

    dy1 = defaultdict(float)
    dy2 = defaultdict(float)
    bbles = defaultdict(list)

    cnx = mysql.connector.connect(user='root', password=self.password,
                                  host='127.0.0.1',
                                  database='dof_tax_roll_archives')

    cursor = cnx.cursor()

    print("Beginning processing... ")

    # Tax bill of every NYC class 2 property in 2017
    query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from tc234_" + y1 + " as roll where roll.`TXCL` = 2 and roll.`ZIP` = 10034"  
    cursor.execute(query)
    result_set = cursor.fetchall()

    for property in result_set:
      tax_bill_y1 = property[11] * self.tax_rates[y1]["tc234"]
      zip_code = str(int(property[1]))
      dy1[property[4]] = tax_bill_y1
      bbles[property[4]].append(tax_bill_y1)

    print("Finished " + y1 + "... ")

    # Tax bill of every NYC class 2 property in 2018
    query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from tc234_" + y2 + " as roll where roll.`TXCL` = 2 and roll.`ZIP` = 10034"  
    cursor.execute(query)
    result_set = cursor.fetchall()

    for property in result_set:
      tax_bill_y2 = property[11] * self.tax_rates[y2]["tc234"]
      zip_code = str(int(property[1]))
      dy2[property[4]] = tax_bill_y2
      bbles[property[4]].append(tax_bill_y2)

    print("Finished " + y2 + "... ")
    p_increases = []

    for bble in dy1.keys():
      if(dy1[bble] > 0):
        p_increase = (dy2[bble] - dy1[bble]) / dy1[bble] * 100
        p_increases.append(p_increase)

    avg_inc = np.mean(p_increases)

    print("AVERAGE OF PERCENT INCREASES: ",)

    return avg_inc
  


















  def get_monthly_evictions(self):

    csv_read = "input_data/east_harlem_evictions.csv"
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)
    d = defaultdict(int)

    for row in reader:
      try:
        tmp = row[4].split("/")
        month = str(int(tmp[0])) + "-" + tmp[2] 
        d[month] += 1
      except:
        print("x")

    # s = [(k,d[k]) for k in sorted(d, key=d.get, reverse=True)]

    for i in range(1,12):
      x = str(i)+"-"+"2017"
      print(x, d[x])

    for i in range(1,7):
      x = str(i)+"-"+"2018"
      print(x, d[x])


  def get_units_by_building(self):

    buildings = defaultdict(int)

    cnx = mysql.connector.connect(user='root', password=self.password,
                                  host='127.0.0.1',
                                  database='dof_tax_roll_archives')

    cursor = cnx.cursor()

    # Tax bill of every NYC class 2 property in 2017
    query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from tc234_18 as roll where roll.`TXCL` = 2"  
    cursor.execute(query)
    result_set = cursor.fetchall()

    for property in result_set:
      bbl = str(int(property[0])) + "-" + str(int(property[2])) + "-" + str(int(property[3]))
      buildings[bbl] = property[12]

    output_file = "output_data/units_by_building.csv"
    with open(output_file,'a') as out:
      writer=csv.writer(out)
      for bbl in buildings.keys():
        writer.writerow([bbl,buildings[bbl]])


  def get_units_per_zip(self):

    zip_dict = defaultdict(int)
    buildings = defaultdict(int)

    csv_read = "output_data/units_by_building.csv"
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)
    for row in reader:
      buildings[row[0]] = int(float(row[1]))

    csv_read = "input_data/multi_story.csv"
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)
    for b in reader:
      bbl = b[2] + "-" + b[10] + "-" + b[11]
      # print(type(buildings[bbl]))
      try:
        zip_dict[b[9]] += buildings[bbl]
      except:
        print("TypeError")

    s = [(k, zip_dict[k]) for k in sorted(zip_dict, key=zip_dict.get, reverse=True)]

    for k,v in s:
      print(k,v)



  def get_units_by_zip(self):

    unit_dict = defaultdict(float)
    evictions_dict = defaultdict(float)
    evictions_by_unit = defaultdict(float)
    buildings = defaultdict(int)

    cnx = mysql.connector.connect(user='root', password=self.password,
                                  host='127.0.0.1',
                                  database='dof_tax_roll_archives')

    cursor = cnx.cursor()

    print("Beginning processing... ")

    # Tax bill of every NYC class 2 property in 2017
    query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from tc234_18 as roll where roll.`TXCL` = 2"  
    cursor.execute(query)
    result_set = cursor.fetchall()

    for property in result_set:

      zip_code = str(int(property[1]))
      res_units = property[12]
      if(res_units > 1):
        unit_dict[zip_code] += res_units

    csv_read = "output_data/evictions_by_zip.csv"
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)

    for row in reader:
      evictions_dict[str(row[0])] = row[1]

    print(unit_dict)
    print(evictions_dict)

    for zip_code in unit_dict.keys():
      print("*")
      print(evictions_dict[zip_code])
      print(unit_dict[zip_code])
      try:
        evictions_by_unit[zip_code] = float(evictions_dict[zip_code]) / float(unit_dict[zip_code]) * 100
      except:
        print("Exception")

    s = [(k,evictions_by_unit[k]) for k in sorted(evictions_by_unit, key=evictions_by_unit.get, reverse=True)]

    for k,v in s:
      print(k,v)



  def get_citywide(self):

    d17 = defaultdict(lambda: defaultdict(float))
    d18 = defaultdict(lambda: defaultdict(float))
    dxx = defaultdict(lambda: defaultdict(list))
    dff = defaultdict(float)
    bbles = defaultdict(list)

    cnx = mysql.connector.connect(user='root', password=self.password,
                                  host='127.0.0.1',
                                  database='dof_tax_roll_archives')

    cursor = cnx.cursor()

    print("Beginning processing... ")

    # Tax bill of every NYC class 2 property in 2017
    query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from tc234_17 as roll where roll.`TXCL` = 2 and roll.`ZIP` = 10034"  
    cursor.execute(query)
    result_set = cursor.fetchall()

    for property in result_set:
      # print(property)
      tax_bill_17 = property[11] * self.tax_rates["17"]["tc234"]
      zip_code = str(int(property[1]))
      d17[zip_code][property[4]] = tax_bill_17
      bbles[property[4]].append(tax_bill_17)

    # Tax bill of every NYC class 2 property in 2018
    query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from tc234_18 as roll where roll.`TXCL` = 2"  
    cursor.execute(query)
    result_set = cursor.fetchall()

    print("Finished 2017... ")

    for property in result_set:
      tax_bill_18 = property[11] * self.tax_rates["18"]["tc234"]
      zip_code = str(int(property[1]))
      d18[zip_code][property[4]] = tax_bill_18
      bbles[property[4]].append(tax_bill_18)

    print("Finished 2018... ")

    for zip_code in d17.keys():
      for bble in d17[zip_code].keys():
        if(d17[zip_code][bble] > 0):
          p_increase = (d18[zip_code][bble] - d17[zip_code][bble]) / d17[zip_code][bble] * 100
          
          #   print(d18[zip_code][bble])
          #   print(d17[zip_code][bble])
          dxx[zip_code] = p_increase

    print("Finished calculating percent increases... ")
    avg = []
    for zip_code in dxx.keys():
      dff[zip_code] = round(np.mean(dxx[zip_code]),2)
      avg.append(np.mean(dxx[zip_code]))

    # print(np.mean(avg))

    print("Finished averaging zip codes... ")

    s = [(k, dff[k]) for k in sorted(dff, key=dff.get, reverse=True)]
    
    # output_file = "output_data/class4_tax_increases.csv"
    # with open(output_file,'a') as out:
    #   writer=csv.writer(out)
    
    #   for k, v in s:
    #     print(k,v)
    #     writer.writerow([k,v])

    # print("Finished writing output... ")
    


  def get_inwood_properties(self):

    bus = defaultdict(lambda: defaultdict(list))
    businesses = defaultdict(lambda: defaultdict(list))
    years = ["09","10","11","12","13","14","15","16","17","18","19"]
    cnx = mysql.connector.connect(user='root', password=self.password,
                                  host='127.0.0.1',
                                  database='dof_tax_roll_archives')

    cursor = cnx.cursor()

    for year in years:
      table = "tc234_"+year
      t = "tc234"
      query = "select `BORO`, `ZIP`, `BLOCK`, `LOT`, `BBLE`, `TXCL`, `HNUM_LO`, `HNUM_HI`,`STR_NAME`, `GR_SQFT`, `NEW_FV_T`, `FN_AVT`, `RES_UNIT` from " + table + " as roll where roll.`TXCL` = 2 AND (roll.`ZIP` = 10034 or roll.`ZIP` = 10040)"  
      cursor.execute(query)
      result_set = cursor.fetchall()
      for data in result_set:
        tax_bill = data[11]*self.tax_rates[year][t]
        if(tax_bill != 0):
          bus[data[4]][year].append(str(int(round(tax_bill, 0)))) 



    for k in bus.keys():
      if("19" in bus[k].keys()):
        businesses[k] = bus[k]

    output = []
    for entry in businesses.keys():
      tmp = [entry]
      for yr in businesses[entry].keys():
        tmp.append(businesses[entry][yr][0])
      print(tmp)

      output.append(tmp)

    output_file = "output_data/class4_tax_increases2.csv"
    with open(output_file,'w') as out:
      csv_out=csv.writer(out)
      for row in output:
        csv_out.writerow(row)
    # return businesses
    
  




if __name__ == '__main__':

  password = "lylla318"
  
  # csv_read = "inwood_class_4.csv"
  # d = defaultdict(list)

  # for year in years:
  #   table = "tc234_"+year
  p = Parser(password);



















