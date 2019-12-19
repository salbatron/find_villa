import time
import pandas as pd
import datetime
from set_browser import set_selenium_local_session

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_table():
    return pd.DataFrame(columns=['vila_name', 
                                'location',
                                'latitude',
                                'longitude',
                                'avg_rate', 
                                'indor_area', 
                                'total_plot_area',
                                'max_guests', 
                                'pool',
                                'num_bedrooms', 
                                'num_bathrooms', 
                                'num_reviews', 
                                'rating', 
                                'not_available_num_days'])

def get_attributes(elements):
    pool = False
    max_guests = 0
    indor_area = 0
    total_plot_area = 0
    num_bedrooms = 0
    num_bathrooms = 0

    for element in elements:
        if "OUTDOORS" in element[0]:
            for e in element[1:]:
                if "pool" in e:
                    pool = True
        if "TYPE & SIZE" in element[0]:
            for e in element[1:]:
                if "Max. guests" in e:
                    max_guests = int(e.split(' ')[-1])
                if "Indoor area:" in e:
                    indor_area = int(e.split(' ')[-2])
                if "Total plot area" in e:
                    total_plot_area = int(e.split(' ')[-2])
        if "BEDROOMS" in element[0]:
            for e in element[1:]:
                if "Bedroom #" in e:
                    num_bedrooms += 1
        if "BATHROOMS" in element[0]:
            for e in element[1:]:
                if "Bathroom #" in e:
                    num_bathrooms += 1     

    return pool, max_guests, indor_area, total_plot_area, num_bedrooms, num_bathrooms  


def fill_table(table, 
                vila_name, 
                avg_rate, 
                elements, 
                location, 
                latitude, 
                longitude, 
                num_reviews, 
                rating, 
                not_available_num_days):

    pool, max_guests, indor_area, total_plot_area, num_bedrooms, num_bathrooms = get_attributes(elements)

    table = table.append({'vila_name': vila_name, 
                        'location': location,
                        'latitude': latitude,
                        'longitude': longitude,
                        'avg_rate': avg_rate, 
                        'indor_area': indor_area, 
                        'total_plot_area': total_plot_area,
                        'max_guests': max_guests, 
                        'pool': pool,
                        'num_bedrooms': num_bedrooms, 
                        'num_bathrooms': num_bathrooms, 
                        'num_reviews': num_reviews, 
                        'rating': rating, 
                        'not_available_num_days': not_available_num_days},ignore_index=True)
    return table
    

if __name__ == "__main__":

    #define table
    table = create_table()

    browser = set_selenium_local_session()
    
    get_links_from_site = False

    if get_links_from_site:
        link = "https://www.myistria.com/en/villas/list?page=86"
        browser.get(link)

        #find all villa links
        all_vila_links = browser.find_elements_by_class_name("title-villa-a")
        all_vila_links = [x.get_attribute('href') for x in all_vila_links]

        #write links in txt
        with open('link_list.txt', 'w') as f:
            for link in all_vila_links:
                f.write("%s\n" % link)
        f.close()

    else:
        f = open('link_list.txt', 'r')  
        all_vila_links = f.readlines()
        f.close()

    for vila in all_vila_links:
        try:
            browser.get(vila)

            #show more facilities
            show_more_facilities_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "btnShowMoreFacilities")))
            browser.execute_script("arguments[0].click()", show_more_facilities_button)

            #get vila name
            vila_name = vila.split('/')[-1]

            #find categories
            facilities_rows = browser.find_elements_by_class_name("facilities-row")
            elements = [x.text.split('\n') for x in facilities_rows]
            categories = [x[0] for x in elements]
            subcategories = [x[1:] for x in elements]

            #find location
            location = browser.find_element_by_xpath("//span[@itemprop='addressLocality']").text
            latitude = float(browser.find_element_by_xpath("//meta[@itemprop='latitude']").get_attribute("content"))
            longitude = float(browser.find_element_by_xpath("//meta[@itemprop='longitude']").get_attribute("content"))

            #get reviews
            try:
                review = browser.find_element_by_class_name("villa-average-rating").text.split(' ')
                num_reviews = int(review[4])
                rating = float(review[2].replace(',','.'))
            except:
                num_reviews = 0
                rating = 0.0

            #get bookings
            #datum = pd.date_range('2019-01-01', '2022-01-01', freq='D')   
            not_available_dates = browser.find_elements_by_class_name("notAvailable")
            not_available_dates = [x.get_attribute('data-datum') for x in not_available_dates]
            not_available_dates = pd.to_datetime(not_available_dates)
            #select start date
            start_date = pd.to_datetime('2020-04-01')
            not_available_num_days = sum(not_available_dates >= start_date)

            #show all rates
            show_all_rates_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "btn-all-rates")))
            browser.execute_script("arguments[0].click()", show_all_rates_button)
            #get rates
            rates = browser.find_elements_by_class_name("currency")
            rates = [x.get_attribute('data-eur') for x in rates]
            rates = [float(x.replace('.','').split(',')[0]) for x in rates]
            if(rates):
                avg_rate = sum(rates)/len(rates)

            table = fill_table(table, 
                            vila_name, 
                            avg_rate, 
                            elements, 
                            location, 
                            latitude, 
                            longitude, 
                            num_reviews, 
                            rating, 
                            not_available_num_days)
        except:
            continue

    #save table
    table.to_pickle('table_19_12_2019.pkl')







