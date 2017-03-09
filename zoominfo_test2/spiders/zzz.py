import scrapy
from scrapy.http import FormRequest
from scrapy.selector import Selector
from zoominfo_test2.items import CompanyItem
from nameparser import HumanName
from collections import deque

class ZoomSpider(scrapy.Spider):
	name = 'zoominfo'
	home_page = 'http://subscriber.zoominfo.com/zoominfo/'
	company_list = [u'apple']
	
	def start_requests(self):
		#Please enter the username after `username=` and enter password after `password=`
		url = 'https://www.zoominfo.com/login?task=save&redirect=account%23myAccount%3Ftargetid%3Dcontent&username=%40salary.com&password='
		yield scrapy.Request(url=url, callback=self.parse)

	def parse(self,response):
		url_list = []
		for i in self.company_list:
			url = "http://subscriber.zoominfo.com/zoominfo/search/company?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22C_EXECUTIVES%22%2C%22isUsed%22%3Afalse%7D%2C%7B%22value%22%3A%22VP_EXECUTIVES%22%2C%22isUsed%22%3Afalse%7D%2C%7B%22value%22%3A%22DIRECTOR%22%2C%22isUsed%22%3Afalse%7D%2C%7B%22value%22%3A%22MANAGER%22%2C%22isUsed%22%3Afalse%7D%2C%7B%22value%22%3A%22NON_MANAGEMENT%22%2C%22isUsed%22%3Afalse%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22industryList%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%2268362%22%2C%22isUsed%22%3Afalse%7D%2C%7B%22value%22%3A%223338%22%2C%22isUsed%22%3Afalse%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false".format(i)
			company = CompanyItem()
			company['c_o_name'] = i
			yield scrapy.Request(url, meta={'company':company,'dont_redirect':True},callback=self.parse_company_1,dont_filter=True)

	def parse_company_1(self,response):
		company = response.meta['company']
		sel = Selector(response)
		if "No Results Found." in response.body:
			print "No Results Found."
			company['c_name'] = 'No Results Found.'
			yield company
		elif "An error occurred while running this search." in response.body:
			print "An error occurred while running this search."
			company['c_name'] = 'An error occurred while running this search./ NOT FOUND'
			yield company
		else:
			company_url = self.home_page+sel.xpath("//a[@class='companyResultsName']/@href").extract_first().strip('#!')
			yield scrapy.Request(
				company_url, meta={'company':company}, callback=self.parse_company_3, dont_filter=True
				)

	def parse_company_3(self,response):
		company = response.meta['company']
		sel = Selector(response)
		company['c_name'] = sel.xpath("//div[@class='companyLocation']/h1[@class='companyName']/text()").extract_first().strip('\n')
		street = sel.xpath("//div[@class='companyLocation']/span[@class='companyAddress']").extract_first()
		company['c_street'] = Selector(text=street).xpath("//span/text()[position()=1]").extract()
		company['c_state_zip_code'] = Selector(text=street).xpath("//span/text()[position()=2]").extract()
		company['c_country'] = Selector(text=street).xpath("//span/text()[position()=3]").extract()
		company['c_website'] = sel.xpath("//div[@class='companyContact']/a/@href").extract_first().strip("http://")
		company['c_employeeN'] = sel.xpath("//span[@class='employeeCount']/text()").extract_first()
			
		url_list = [
		#Compensation leads url
		{'url':'http://subscriber.zoominfo.com/zoominfo/search/person?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22C_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22VP_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22DIRECTOR%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22MANAGER%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22NON_MANAGEMENT%22%2C%22isUsed%22%3Afalse%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22industryList%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%2268362%22%2C%22isUsed%22%3Afalse%7D%2C%7B%22value%22%3A%223338%22%2C%22isUsed%22%3Afalse%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22title%22%3A%7B%22value%22%3A%22compensation%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%2C%22sortBy%22%3A%7B%22value%22%3A%22hierarchy%22%2C%22isUsed%22%3Atrue%7D%2C%22sortOrder%22%3A%7B%22value%22%3A%22DESCENDING%22%2C%22isUsed%22%3Atrue%7D%2C%22contactRequirements%22%3A%7B%22value%22%3A%22Email%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false'.format(company['c_website'])},
		#Hr leads url
		{'url':'http://subscriber.zoominfo.com/zoominfo/search/person?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22title%22%3A%7B%22value%22%3A%22hr%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22C_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22VP_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22DIRECTOR%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22MANAGER%22%2C%22isUsed%22%3Atrue%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22sortBy%22%3A%7B%22value%22%3A%22hierarchy%22%2C%22isUsed%22%3Atrue%7D%2C%22sortOrder%22%3A%7B%22value%22%3A%22DESCENDING%22%2C%22isUsed%22%3Atrue%7D%2C%22contactRequirements%22%3A%7B%22value%22%3A%22Email%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false'.format(company['c_website'])},
		#Total rewards leads url
		{'url':'http://subscriber.zoominfo.com/zoominfo/search/person?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22title%22%3A%7B%22value%22%3A%22total%2520rewards%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22C_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22VP_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22DIRECTOR%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22MANAGER%22%2C%22isUsed%22%3Atrue%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22sortBy%22%3A%7B%22value%22%3A%22hierarchy%22%2C%22isUsed%22%3Atrue%7D%2C%22sortOrder%22%3A%7B%22value%22%3A%22DESCENDING%22%2C%22isUsed%22%3Atrue%7D%2C%22contactRequirements%22%3A%7B%22value%22%3A%22Email%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false'.format(company['c_website'])},
		#Compensation staffs url
		{'url':'http://subscriber.zoominfo.com/zoominfo/search/person?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%2C%22title%22%3A%7B%22value%22%3A%22compensation%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22NON_MANAGEMENT%22%2C%22isUsed%22%3Atrue%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22sortBy%22%3A%7B%22value%22%3A%22hierarchy%22%2C%22isUsed%22%3Atrue%7D%2C%22sortOrder%22%3A%7B%22value%22%3A%22DESCENDING%22%2C%22isUsed%22%3Atrue%7D%2C%22contactRequirements%22%3A%7B%22value%22%3A%22Email%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false'.format(company['c_website'])},
		#Hr staffs url
		{'url':'http://subscriber.zoominfo.com/zoominfo/search/person?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22title%22%3A%7B%22value%22%3A%22hr%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22NON_MANAGEMENT%22%2C%22isUsed%22%3Atrue%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22sortBy%22%3A%7B%22value%22%3A%22hierarchy%22%2C%22isUsed%22%3Atrue%7D%2C%22sortOrder%22%3A%7B%22value%22%3A%22DESCENDING%22%2C%22isUsed%22%3Atrue%7D%2C%22contactRequirements%22%3A%7B%22value%22%3A%22Email%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false'.format(company['c_website'])}
		]

		url_list2 = [
		#Financial leads url
		{'url':'http://subscriber.zoominfo.com/zoominfo/search/person?criteria=%7B%22workHistory%22%3A%7B%22value%22%3A%22Current%22%2C%22isUsed%22%3Atrue%7D%2C%22boardMember%22%3A%7B%22value%22%3A%22Exclude%22%2C%22isUsed%22%3Atrue%7D%2C%22includePartialProfiles%22%3A%7B%22value%22%3Atrue%2C%22isUsed%22%3Afalse%7D%2C%22companyName%22%3A%7B%22value%22%3A%22{0}%22%2C%22isUsed%22%3Atrue%7D%2C%22address%22%3A%7B%22value%22%3A%22united%2520states%22%2C%22isUsed%22%3Atrue%7D%2C%22managementLevel%22%3A%7B%22value%22%3A%5B%7B%22value%22%3A%22C_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22VP_EXECUTIVES%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22DIRECTOR%22%2C%22isUsed%22%3Atrue%7D%2C%7B%22value%22%3A%22MANAGER%22%2C%22isUsed%22%3Atrue%7D%5D%2C%22isUsed%22%3Atrue%7D%2C%22title%22%3A%7B%22value%22%3A%22finance%22%2C%22isUsed%22%3Atrue%7D%2C%22sortBy%22%3A%7B%22value%22%3A%22hierarchy%22%2C%22isUsed%22%3Atrue%7D%2C%22sortOrder%22%3A%7B%22value%22%3A%22DESCENDING%22%2C%22isUsed%22%3Atrue%7D%2C%22contactRequirements%22%3A%7B%22value%22%3A%22Email%22%2C%22isUsed%22%3Atrue%7D%7D&isCountOnly=false'.format(company['c_website'])}
		
		]
		yield scrapy.Request(self.home_page, meta={'company':company,'url_list':url_list,'url_list2':url_list2}, callback=self.parse_middle,dont_filter=True
			)

	def parse_middle(self,response):
		url_list = response.meta['url_list']
		url_list2 = response.meta['url_list2']
		while len(url_list)>0:
			company = response.meta['company']
			yield scrapy.Request(url_list.pop(0)['url'],meta={'company':company}, callback=self.parse_person_1,dont_filter=True
				)
		while len(url_list2)>0:
			company = response.meta['company']
			yield scrapy.Request(url_list2.pop(0)['url'],meta={'company':company}, callback=self.parse_person_3,dont_filter=True
				)
	
	def parse_person_1(self,response):
		sel = Selector(response)
		company = response.meta['company']
		person_url = sel.xpath("//td[@class='personName']/a/@href").extract()
		person_list = []
		if 'No Results Found.' in response.body:
			print "No Results Found"
		else:
			for i in person_url[:5]:
				person = self.home_page+i.strip('#!')
				person_list.append(person)
				yield scrapy.Request(person, meta={'company':company}, callback=self.parse_person_2,dont_filter=True
					)
	def parse_person_3(self,response):
		sel = Selector(response)
		company = response.meta['company']
		person_url = sel.xpath("//td[@class='personName']/a/@href").extract()
		person_list = []
		if 'No Results Found.' in response.body:
			print "No Results Found"
		else:
			for i in person_url[:2]:
				person = self.home_page+i.strip('#!')
				person_list.append(person)
				yield scrapy.Request(person, meta={'company':company}, callback=self.parse_person_2)

	def parse_person_2(self,response):
		company = response.meta['company']
		sel = Selector(response)
		with open('11.html','w') as f:
			f.write(response.body)
		f.close()
		name = sel.xpath("//h1[@itemprop='name']/text()").extract_first().strip("\n")
		company['p_f_name'] = HumanName(name).first + ' ' + HumanName(name).middle
		company['p_l_name'] = HumanName(name).last
		company['p_role'] = sel.xpath("//h2[@itemprop='role']/text()").extract_first().strip("\n")
		phone = sel.xpath("//div[@class='phoneNumber']/text()[position()=2]").extract_first()
		if phone:
			company['p_phoneNumber'] = phone.strip("\n")
		else:
			company['p_phoneNumber'] = ''
		company['p_email'] = sel.xpath("//span[@class='personEmail']/a/text()").extract()
		#company['p_email'] = email.strip()
		yield company








































