import re
import json
import io
import csv
import sys
from pprint import pprint
from collections import defaultdict
import time
import datetime
import numpy as np
from bs4 import BeautifulSoup
import urllib.request


class Analyzer:

  def __init__(self):

    self.rank_buildings_by_evictions()


  def rank_buildings_by_evictions(self):

    d = defaultdict(int)
    csv_read = "output_data/inwood_evictions_cleaned.csv"
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)

    for row in reader:
      d[row[14]] += 1

    s = [(k, d[k]) for k in sorted(d, key=d.get, reverse=True)]

    csv_write = "output_data/evictions_by_bin.csv"
    with open(csv_write,'w') as out:
      writer=csv.writer(out)
      for k,v in s:
        row = [k,v]
        writer.writerow(row)





class Parser:

  def __init__(self, csv_read, csv_write1, csv_write2):

    self.get_zip_counts()
    
    self.csv_read = csv_read
    self.csv_write1 = csv_write1
    self.csv_write2 = csv_write2
    # self.evictions = self.sanitize() 
    # self.scrape_goat()   



  def sanitize(self):

    csv_read = self.csv_read
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)
    sanitized = []


    for row in reader:
      s = row[2]

      # SPECIAL CASES

      s = s.replace(" - ", " ")
      s = s.replace(" CLAYTON PWLL", " CLAYTON POWELL")
      s = s.replace(" DOUGL ASSS", " DOUGLASS")
      s = s.replace(" DOUGL ASS", " DOUGLASS")
      s = s.replace(" BREWE R", " BREWER")
      s = s.replace(" FRANCIS LEWI S", " FRANCIS LEWIS")
      s = s.replace(" CLAYTON PO WELL", " CLAYTON POWELL")
      s = s.replace(" FREDERICK DOUGLAS ", " FREDERICK DOUGLASS ")
      s = s.replace(" FREDERICK DOUGL AS ", " FREDERICK DOUGLASS ")
      s = s.replace(" FORT WASHINGTO N AVENUE ", " FORT WASHINGTON AVENUE ")
      s = s.replace(" JR. ", " JR ")
      s = s.replace(" WILLIAMSBRID GE ROAD", " WILLIAMSBRIDGE ROAD")
      s = s.replace(" VALENTI NE AVENUE", " VALENTINE AVENUE")
      s = s.replace(" WHITE PLAI NS ROAD", " WHITE PLAINS ROAD")
      s = s.replace(" KI NG ", " KING ")
      s = s.replace(" WASHINGTO N AVENUE", " WASHINGTON AVENUE")
      s = s.replace(" CRESCE NT", " CRESCENT")
      s = s.replace(" ATLANT IC", " ATLANTIC")
      s = s.replace(" P OLITE AV", " POLITE AV")
      s = s.replace(" KINGSBR IDGE", " KINGSBRIDGE")
      s = s.replace(" HARDIN G", " HARDING")


      # MISC

      patterns = [" I N THE BUILDING(.*)| IN TH(.*)", " ENTIRE(.*)", " ALL(.*)", " RIGHT(.*)", " BASEMENT(.*)"]

      for p in patterns:
        r = re.compile(p)
        if(r.search(s)):
          s = (re.sub(p, "", s)).strip()

      p = " SQUAR E$"
      r = re.compile(p)
      if(r.search(s)):
        s = (re.sub(p, " SQUARE", s)).strip()

      # Remove extraneous information from end of string. #

      r = re.compile("(.*)\((.*)\)")
      if(r.search(s)):
        s = re.sub("\((.*)\)","", s)

      p = "( APT. (.*)| APT (.*)| - APT. (.*)| - APT (.*))| APT.(.*)"
      r = re.compile(p)
      if(r.search(s)):
        s = (re.sub(p, "", s)).strip()

      p = "( AKA (.*)| AK A (.*)| A KA (.*)| A/K/A (.*)| A/K/ A (.*)| A/ K/A (.*)| A /K/A (.*)| A/K /A (.*)| A.K.A (.*))"
      r = re.compile(p)
      if(r.search(s)):
        s = (re.sub(p, "", s)).strip()

      p = "(-UNIT (.*)| - UNIT (.*)| UNIT (.*)| STORAGE UNIT (.*)| IN BKA (.*)| @(.*)|-BKA WHSE(.*))"
      r = re.compile(p)
      if(r.search(s)):
        s = (re.sub(p, "", s)).strip()

      # Avenues

      av = False
      p = " AVE (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z) (.*)"
      r = re.compile(p)
      if(r.search(s)):
        av = True
        t = s[s.index("AVE") + 4]
        s = (re.sub(p, " AVENUE", s)).strip()
        s += (" "+t)

      p = " AVE. (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z) (.*)"
      r = re.compile(p)
      if(r.search(s)):
        av = True
        t = s[s.index("AVE") + 5]
        s = (re.sub(p, " AVENUE", s)).strip()
        s += (" "+t)

      p = " AVE (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)$| AVE. (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)$"
      r = re.compile(p)
      if(r.search(s)):
        av = True
        t = s[-1]
        s = (re.sub(p, " AVENUE", s)).strip()
        s += (" "+t)


      p = " AVENUE (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z) (.*)"
      r = re.compile(p)
      if(r.search(s)):
        av = True
        t = s[s.index("AVENUE") + 7]
        s = (re.sub(p, " AVENUE", s)).strip()
        s += (" "+t)

      p = " AVENUE (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)$"
      r = re.compile(p)
      if(r.search(s)):
        av = True
        t = s[s.index("AVENUE") + 7]
        s = (re.sub(p, " AVENUE", s)).strip()
        s += (" "+t)

      p = " AVENUE(.*)| A VENUE(.*)| AVENUE (.*)| AVENU E$| AV ENUE$| AVEN UE$| AVE$| AVE.$| AV | A VE.$| A VE$| AVE.(.*)| AV$| AV E$| AVE. (.*)| AVE (.*)| AV-(.*)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = (re.sub(p, " AVENUE ", s)).strip()

      s = (re.sub("[ ]{2,}", " ", s)).strip()


      # TERRACES

      p = "( TERR$| TERR.$)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = (re.sub(p, " TERRACE", s)).strip()

      p = "( TERRAC E$| TER RACE | TER RACE$)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = (re.sub(p, " TERRACE ", s)).strip()
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      
      # BOULEVARDS

      p = "( BLVD (.*)| BO ULEVARD$| BO ULEVARD (.*)| BOULEVA RD(.*)| BOULEVARD (.*)| B LVD.$| BLV D.| B LVD. (.*)| BLVD. (.*)| BLVD.$| BLVD$| BOULEVAR D$| BL VD (.*)| BOULEV ARD | BOULEV ARD$| BL VD$| BOUL EVARD(.*))"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " BOULEVARD ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()


      # COURTS

      p = "( COURT$| COURT (.*)| CT.$| CT.(.*))"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " COURT ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()


      # DRIVES

      p = "( DR$| DR.$| DR )"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " DRIVE ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = " DRIVE (.*)"
      r = re.compile(p)
      if(r.search(s)):
        if( "DRIVE SO" not in s and "DRIVE NO" not in s and "DRIVE EA" not in s and "DRIVE WE" not in s ):
          s = re.sub(p, " DRIVE", s)
          s = (re.sub("[ ]{2,}", " ", s)).strip()
        elif("DRIVE EA" in s):
          s = re.sub(p, " DRIVE EAST", s)
        elif("DRIVE WE" in s):
          s = re.sub(p, " DRIVE WEST", s)
        elif("DRIVE NO" in s):
          s = re.sub(p, " DRIVE NORTH", s)
        elif("DRIVE SO" in s):
          s = re.sub(p, " DRIVE SOUTH", s)


      # LANES

      p = "( LN$| LN.$| LANE (.*))"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " LANE", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = " LANE (.*)"
      r = re.compile(p)
      if(r.search(s) and "LANE NO" not in s and "LANE SO" not in s and "LANE EA" not in s and "LANE WE" not in s ):
        s = re.sub(p, " LANE", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()


      # PARKWAYS

      p = " PARKWA$"
      r = re.compile(p)
      if(r.search(s)):
        s = (re.sub(p, " PARKWAY", s)).strip()

      p = "( PARK WAY| PARKWA Y|  P ARKWAY| P ARKWAY| PKW Y| PAR KWAY | PK WAY| PK WAY| PKWY| PKWAY| PA RKWAY| PAR KWAY$)"
      r = re.compile(p)
      if(r.search(s)):
        s = (re.sub(p, " PARKWAY ", s)).strip()
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = " PARKWAY (.*)"
      r = re.compile(p)
      if(r.search(s) and "PARKWAY NO" not in s and "PARKWAY SO" not in s and "PARKWAY EA" not in s and "PARKWAY WE" not in s):
        s = (re.sub(p, " PARKWAY", s)).strip()


      # EXPRESSWAYS

      p = " EXPWY.$| EXPWY$| EXPRESSWAY(.*)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = (re.sub(p, " EXPRESSWAY", s)).strip()


      # ROADS

      p = "( RD (.*)| ROAD (.*)| RD. (.*)| RD.$| ROA D$| RO AD(.*)| RO AD(.*)| R OAD(.*)| ROA D$| RD$)"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " ROAD ", s)
       
      s = s.strip()
      s = (re.sub("[ ]{2,}", " ", s)).strip()


      #PLACES

      place = False 
      p = "( PL. SO(.*)| PL SO(.*)| PL. S.(.*)| PL. SO(.*)| PLACE SO(.*)|PLACE S.(.*))"
      r = re.compile(p)
      if(r.search(s)):
        place = True
        s = re.sub(p, " PLACE SOUTH", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( PL. NO(.*)| PL NO(.*)| PL. NO(.*)| PLACE NO(.*))"
      r = re.compile(p)
      if(r.search(s)):
        place = True
        s = re.sub(p, " PLACE NORTH", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( PL (.*)| PLACE (.*)| PL. (.*)| PL.$| PL$| P LACE(.*))"
      r = re.compile(p)
      if(r.search(s) and not place):
        s = re.sub(p, " PLACE ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( PLAC E | PLACE$)"
      r = re.compile(p)
      if(r.search(s) and not place):
        s = re.sub(p, " PLACE", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      # STREETS

      p = "(STREE T$| STREE T (.*)| STRE ET(.*)| REET$| ST )"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " STREET ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()


      #saints = ["ANN", "FELIX", "JAMES", "JOHN", "LAWRENCE", "MARK", "MARY", "NICHOLAS", "PAUL", "RAYMOND"]
      sf = False
      p = "( ST. ANN(.*) | ST. FELIX(.*) | ST. JAMES(.*) | ST. JOHN(.*) | ST. LAWRENCE(.*) | ST. MARK(.*) | ST. MARY(.*) | ST. NICHOLAS(.*) | ST. PAUL(.*) | ST. RAYMOND(.*))"
      r = re.compile(p)
      if(r.search(s)):
        sf = True

      p = "( ST. (.*)| ST (.*)| STREET (.*)| ST.$| ST$| STREET, (.*)| STREET(.*)| S TREET(.*))"
      r = re.compile(p)
      if(r.search(s) and not sf):
        s = re.sub(p, " STREET", s)
    

      if("ST." in s):
        idx = s.index("ST.")
        if(len(s) > (idx+3) and s[idx+3] != " "):
          s = s[0:idx+3] + " " + s[idx+3:]

      p = " BROADWAY(.*)"
      r = re.compile(p)
      if(r.search(s) and " TERRACE" not in s):
        s = re.sub(p, " BROADWAY", s)
      

      # NUMBERS

      for i in range(1,4):
        p = "\d{" + str(i) +"}[ND|RD|TH|ST]"
        r = re.compile(p)  
        if(r.search(s)):
          idx1 = (r.search(s)).start() + i
          idx2 = (r.search(s)).start() + i + 2
          s = s[0:idx1] + s[idx2:]


      n_dict = {"FIRST":1, "SECOND":2, "THIRD":3, "FOURTH":4, "FIFTH":5, "SIXTH":6, "SEVENTH":7, "EIGHTH":8, "NINTH":9, "TENTH":10}
      for key in n_dict.keys():
        if(key in s):
          s = s.replace(key, str(n_dict[key]))


      # DIRECTIONALS

      av = False
      p = " AVENUE (H|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)$"
      r = re.compile(p)
      if(r.search(s)):
        av = True

      p = "( N ORTH | NO RTH | NOR TH | NORT H | N ORTH$| NO RTH$| NOR TH$| NORT H$)"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " NORTH ", s)

      s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( N | N. | N.$| N$)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = re.sub(p, " NORTH ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( S OUTH | SO UTH | SOU TH | SOUT H | S OUTH$| SO UTH$| SOU TH$| SOUT H$)"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " SOUTH ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( S | S. | S.$| S$)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = re.sub(p, " SOUTH ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( E AST | EA ST | EAS T | E AST$| EA ST$| EAS T$)"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " EAST ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( E | E. | E.$| E$)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = re.sub(p, " EAST ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( W EST(.*)| WE ST(.*)| WES T(.*))"
      r = re.compile(p)
      if(r.search(s)):
        s = re.sub(p, " WEST ", s)
        s = (re.sub("[ ]{2,}", " ", s)).strip()

      p = "( W | W. | W.$ | W$)"
      r = re.compile(p)
      if(r.search(s) and not av):
        s = re.sub(p, " WEST ", s)

      s = (re.sub("[ ]{2,}", " ", s)).strip()

      
      row[2] = s
      sanitized.append(row)

    # print("ENDS: ", s)
    return sanitized


  # http://a030-goat.nyc.gov/goat/Default.aspx?boro=4&addressNumber=133-24&street=HAWTREE+CREEK+ROAD
  def scrape_goat(self):

    field_names = ["court_index_no", "docket_no", "eviction_address", "eviction_apt_no", "executed_date", "marshall_first_name", "marshall_last_name", "residential_commercial_ind", "borough", "eviction_zip", "schedule_status", "bbl", "block", "lot", "bin_no", "hnum_lo", "hnum_hi", "condo_no", "coop_no", "zip_code", "coordinates", "str_name", "from_node", "from_xy_coordinate, to_node", "to_xy_coordinate", "segment_from_node", "segment_from_xy_coordinate", "segment_to_node", "segment_to_xy_coordinate", "segment_id_length"]
    borough_map = {"MANHATTAN":"1", "BRONX":"2", "BROOKLYN":"3", "QUEENS":"4", "STATEN ISLAND":"5"}
    malformed = []

    first = True

    with open(r'output_data/inwood_evictions_cleaned.csv', 'a') as f:
      writer = csv.writer(f)
      writer.writerow(field_names)

    for i in range(len(self.evictions)):
      print(i)
      
      #if(i % 100 == 0):
      print("Completed " + str(i) + " evictions...")

      eviction = self.evictions[i]
      address = eviction[2]
      borough = eviction[8]
      street_no = address.split(" ")[0]
      if(" " in address):
        idx = address.index(" ")
        street = (address[idx+1:]).replace(" ","+")
        # print(address, borough)
        if("NEW YORK" in borough):
          borough = "MANHATTAN"
        url = "http://a030-goat.nyc.gov/goat/Default.aspx?boro=" + borough_map[borough] + "&addressNumber=" + street_no + "&street=" + street 
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        soup = BeautifulSoup(response,  "html.parser")
        output = []

        try:
          
          bbl = (soup.find("span", {"id": "label_bbl_output"})).text
          block = (soup.find("span", {"id": "label_tax_block_output"})).text
          lot = (soup.find("span", {"id": "label_tax_lot_output"})).text
          bin_no = (soup.find("span", {"id": "label_bin_output"})).text
          hnum_lo = (soup.find("span", {"id": "label_low_house_num_output"})).text
          hnum_hi = (soup.find("span", {"id": "label_high_house_num_output"})).text
          condo_no = (soup.find("span", {"id": "label_rapd_condo_num_output"})).text
          coop_no = (soup.find("span", {"id": "label_coop_num_output"})).text
          zip_code = (soup.find("span", {"id": "label_zip_code_output"})).text 
          coordinates = (soup.find("span", {"id": "label_lat_long_output"})).text 
          str_name = (soup.find("span", {"id": "label_preferred_lgc_output"})).text
          from_node = (soup.find("span", {"id": "label_from_node_output"})).text 
          from_xy_coordinate = (soup.find("span", {"id": "label_from_xy_coord_output"})).text 
          to_node = (soup.find("span", {"id": "label_to_xy_coord_output"})).text 
          to_xy_coordinate = (soup.find("span", {"id": "label_to_xy_coord_output"})).text 
          segment_from_node = (soup.find("span", {"id": "label_seg_from_node"})).text 
          segment_from_xy_coordinate = (soup.find("span", {"id": "label_seg_from_xy"})).text 
          segment_to_node = (soup.find("span", {"id": "label_seg_to_node"})).text 
          segment_to_xy_coordinate = (soup.find("span", {"id": "label_seg_to_xy"})).text 
          segment_id_length = (soup.find("span", {"id": "label_segmentid_length_output"})).text  


          labels = soup.find("tr", {"class":"labels"})
          ctr = 0
          
          for elem in labels.findAll("td"):
            form = (elem.text).strip()
            if ctr == 1:
              hnum_lo = form
            elif ctr == 2:
              hnum_hi = form
            elif ctr == 3:
              str_name = form
            ctr += 1

          output = [bbl, block, lot, bin_no, hnum_lo, hnum_hi, condo_no, coop_no, zip_code, coordinates, str_name, from_node, from_xy_coordinate, to_node, to_xy_coordinate, segment_from_node, segment_from_xy_coordinate, segment_to_node, segment_to_xy_coordinate, segment_id_length]
          for el in output:
            eviction.append(el)

          with open(self.csv_write1, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(eviction)
        except:
          malformed.append(eviction)
          with open(self.csv_write2, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(eviction)


    for address in malformed:
      print("-----------------------------------------------------------------------------------")
      print(address)
      print("-----------------------------------------------------------------------------------")





  def get_zip_counts(self):


    csv_read = "data/evictions.csv"
    reader = csv.reader(open(csv_read, 'rU'), delimiter=",", dialect=csv.excel_tab)
    d = defaultdict(int)
    a = []


    for row in reader:
      #if(row[4][-1] == "8"):
      d[row[9]] += 1

    for v in d.values():
      a.append(v)


    s = [(k, d[k]) for k in sorted(d, key=d.get, reverse=True)]

    with open("output_data/evictions_by_zip.csv", 'a') as f:
      writer = csv.writer(f)
      
      for k, v in s:
        writer.writerow([k, v])


    
    print(d["10034"])
    print(d["10040"])
    print("****")
    print(d["10029"])
    print(d["10035"])
    print("****")
    print(np.mean(a))
    print(np.median(a))

  


if __name__ == '__main__':

  p = Parser("input_data/upper_east_evictions.csv", "output_data/upper_east_evictions_cleaned.csv", "output_data/upper_east_malformed.csv");
  #a = Analyzer();






