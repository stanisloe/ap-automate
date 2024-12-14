import time

import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

ADSPOWER_API_BASE_URL = "http://local.adspower.net:50362"
PROFILES_TO_OPEN ="profiles_to_open.xlsx"

def map_profile_name_to_id():
    result = {}

    pages_left = True
    page = 1
    profiles = []
    while pages_left:
        result = {}
        query = {'page_size': '100', 'page': page}
        response = requests.get(ADSPOWER_API_BASE_URL + "/api/v1/user/list", query)
        profiles.extend(response.json()['data']['list'])
        if len(response.json()['data']['list']) < 100:
            pages_left = False
        else:
            page += 1
        time.sleep(1)

    for profileInfo in profiles:
        name = profileInfo['name']
        id = profileInfo['user_id']
        result[name] = id
    return result

def connect_to_profile(profile_id):
    attempts = 3
    sleep_time = 20
    while attempts > 0:
        try:
            query = {'user_id': profile_id}
            response = requests.get(ADSPOWER_API_BASE_URL + "/api/v1/browser/start", query).json()
            print(response)
            selenium_url = response["data"]["ws"]["selenium"]
            driver_path = response["data"]["webdriver"]
            chrome_options = Options()
            chrome_options.page_load_strategy = 'none'
            chrome_options.add_experimental_option("debuggerAddress", selenium_url)
            capabilities = DesiredCapabilities.CHROME
            capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+
            service = Service(executable_path=driver_path, capabilities=capabilities)
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print("An exception occurred {}".format(e))
        time.sleep(sleep_time)
        sleep_time *= 2
        attempts -= 1


# def new_tab(url):
#     driver.switch_to.new_window()
#     driver.get(url)
#
#
# if __name__ == '__main__':
#     profiles_to_id = map_profile_name_to_id()
#
#     links_to_open = []
#     links_df = pd.read_excel(PROFILES_TO_OPEN, 'links')
#     for index, row in links_df.iterrows():
#         links_to_open.append(row["link"])
#
#     profiles_df = pd.read_excel(PROFILES_TO_OPEN, 'profiles')
#     profiles = []
#     for index, row in profiles_df.iterrows():
#         profiles.append(str(row["profile"]))
#
#     tabs_to_keep = {
#         "127.0.0.1",
#         "twitter", "web.telegram", "discord.com", "start.adspower.net"
#     }
#     for profile in profiles:
#         profile_id = profiles_to_id.get(profile)
#         driver = connect_to_profile(profile_id=profile_id)
#
#         time.sleep(10)
#
#         for link in links_to_open:
#             new_tab(link)
#         time.sleep(random.randint(3, 6))