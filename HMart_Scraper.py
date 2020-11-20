from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup 
import datetime
from datetime import date as dt
from datetime import datetime 
import re
import psycopg2
 
#deal with pop up
#driver = webdriver.chrome()
#driver.get(url)
#driver.find_element_by_xpath("//*[@id="loyalty-onboarding-dismiss"]/span").click()
#time.sleep(5)
#driver.switch_to_alert().accept()

meat_url = "https://fresh.hmart.com/meat-seafood-produce?cat=468"
seafood_url = "https://fresh.hmart.com/meat-seafood-produce?cat=469&product_list_limit=all"
produce_url = "https://fresh.hmart.com/meat-seafood-produce?cat=471&product_list_limit=all"
chip_url = "https://fresh.hmart.com/groceries/snacks?cat=954&product_list_limit=all"
cookie_url = "https://fresh.hmart.com/groceries/snacks?cat=524&product_list_limit=all"
candy_url = "https://fresh.hmart.com/groceries/snacks?cat=528&product_list_limit=all"
dried_url = "https://fresh.hmart.com/groceries/snacks?cat=957&product_list_limit=all"
inst_noodle_url = "https://fresh.hmart.com/groceries?cat=513&product_list_limit=all"
inst_rice_url ="https://fresh.hmart.com/groceries?cat=918&product_list_limit=all"
inst_soup_url = "https://fresh.hmart.com/groceries?cat=930&product_list_limit=all"
inst_sauce_url = "https://fresh.hmart.com/groceries?cat=512&product_list_limit=all"
canned_url = "https://fresh.hmart.com/groceries?cat=1071&product_list_limit=all"
flavored_drink_url = "https://fresh.hmart.com/groceries?cat=963&product_list_limit=all"
coffee_tea_url = "https://fresh.hmart.com/groceries?cat=969&product_list_limit=all"
milk_url = "https://fresh.hmart.com/groceries?cat=1065&product_list_limit=all"
seaweed_url = "https://fresh.hmart.com/groceries?cat=534&product_list_limit=all"
rice_url = "https://fresh.hmart.com/groceries?cat=521&product_list_limit=all"
flour_url = "https://fresh.hmart.com/groceries?cat=975&product_list_limit=all"
grain_url = "https://fresh.hmart.com/groceries?cat=522&product_list_limit=all"
kimchi_url = "https://fresh.hmart.com/groceries?cat=505&product_list_limit=all"
side_url = "https://fresh.hmart.com/groceries?cat=506&product_list_limit=all"

#group the URLs together
hmart_url = [meat_url,seafood_url,produce_url, chip_url,cookie_url, candy_url,
			dried_url,inst_noodle_url,inst_rice_url,inst_soup_url,inst_sauce_url,
			canned_url,flavored_drink_url,coffee_tea_url,milk_url,seaweed_url,rice_url,
			flour_url,grain_url,kimchi_url,side_url]

#product type of each URL
product_type = ['meat','seafood','produce', 'chip','cookie','candy','dried',
				'instant noodle','instant rice','instant soup','instant sauce',
				'Canned','flavored_drink','coffee/tea','milk','seaweed','rice',
				'flour','grain','kimchi','side_dish']

## open up excel file

'''
filename = "HMart_Foods.csv"
f = open(filename,"w", encoding='utf-8')
headers = "Name, sale_ind ,sale_price ,orig_price, quantity, refrigerate, type, Market, date, time \n"
f.write(headers)
'''

#Establish the Connection
conn = psycopg2.connect(database="groceries", user='postgres', password='Umbreon11!', host='localhost', port= '5434')

#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#scraping hmart website specifically

array_length = len(hmart_url)

for i in range(array_length):
	#opening connection and grabbing the page
	uclient = uReq(hmart_url[i])
	page_html = uclient.read()
	uclient.close()

	#html parsing
	page_soup = soup(page_html,"html.parser")

	##define produc type
	p_type = product_type[i]

	###collect all of the products
	containers = page_soup.findAll("li", {"class":"item product product-item"})


	for container in containers:


		product  = container.div.img["alt"]

		#split product name between name and weight
		position = re.search(r"\d",product)
		if str(position) == "None":
			product_name = product
			product_quantity = "1 each"
		else:
			position = position.start()
			product_name = product[0:position-1]
			product_quantity = product[position:]

		#check if item needs to be refrigerated
		if len(container.find_all("span",{"class":"refrigerated-flag flag"})) > 0:
			refrigerate = "yes"
		else:
			refrigerate = "no"

		#Get price of product
		if len(container.find_all("span",{"class":"red-flag flag"})) > 0:
				#find sales container then pull from there
				sale_price_container = container.find('span',{'class':'special-price'})
				sale_price_container = sale_price_container.find('span',{'class':'price-wrapper'})
				sale_price = sale_price_container['data-price-amount']
				#find orignal price container then pull data from there
				orig_price_container = container.find('span',{'class':'old-price'})
				orig_price_container = orig_price_container.find('span',{'class':'price-wrapper'})
				orig_price = orig_price_container['data-price-amount']
				# Set sale indicator
				sale_ind = "yes"

		else:
			#rename as orig price
			price_container = container.find('span',{'class':'price-wrapper'})
			orig_price = price_container['data-price-amount']
			#create a Null for Sales price
			sale_price = ""
			sale_ind = "no"

		#market name

		market_name = "HMart"

		#Date & time of extract
		date = str(dt.today())
		now = datetime.now()
		time = now.strftime("%H:%M:%S")

		#insert values into database
		SQL = 'INSERT INTO temp_groceries (name,"SALE_IND","SALE_PRICE","ORIG_PRICE","QUANTITY","REFRIGERATE","TYPE","MARKET","DATE","TIME") VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
		data = (product_name,sale_ind,sale_price,orig_price,product_quantity,refrigerate,p_type,market_name,date,time)
		cursor.execute(SQL,data)
		conn.commit()

		print(product_name + "," + sale_ind + "," + sale_price + "," + orig_price  + "," + product_quantity.replace(",","|") + "," + refrigerate + "," + p_type + "," + market_name + "," + date + "," + time + "\n")

		#f.write(product_name + "," + sale_ind + "," + sale_price + "," + orig_price  + "," + product_quantity.replace(",","|") + "," + refrigerate + "," + p_type + "," + market_name + "," + date + "," + time + "\n")

#f.close()

# Closing the connection
conn.close()


# Commit your changes in the database
print("Records inserted DUI LAY!")


#print("done DUI LAY!")

