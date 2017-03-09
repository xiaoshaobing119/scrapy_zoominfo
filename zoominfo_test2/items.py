# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyItem(scrapy.Item):
	#Company
	c_o_name = scrapy.Field()
	c_name = scrapy.Field()
	c_street = scrapy.Field()
	c_state_zip_code = scrapy.Field()
	c_country = scrapy.Field()
	c_website = scrapy.Field()
	c_employeeN = scrapy.Field()

	#Five compensation leads
	p_f_name = scrapy.Field()
	p_l_name = scrapy.Field()
	p_role = scrapy.Field()
	p_phoneNumber = scrapy.Field()
	p_email = scrapy.Field()


