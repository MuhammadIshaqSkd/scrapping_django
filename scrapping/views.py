from django.contrib.auth import authenticate
from scrapping.models import UserData
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Create your views here.
from django.contrib.auth.models import User






class Login(View):
    @staticmethod
    def get(request):
        return render(request, "login.html")

    def post(self,request):
        Data = request.POST
        username = Data.get("username")
        Password = Data.get("password")
        user = authenticate(username=username, password=Password)

        if user:
            print(user)
            login(request, user)
            # messages.error(request, message)
            return redirect("/dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("/")


class Dashboard( LoginRequiredMixin,View):
    login_url = '/'
    @staticmethod
    def get(request):
        return render(request, "dashboard.html")

    @staticmethod
    def post(request):
        Data = request.POST
        url = Data.get("url")
        click_limit = Data.get("limit")
        click_limit = int(click_limit)


        def scroll_into_view(driver, element):
            driver.execute_script("arguments[0].scrollIntoView(true);", element)

        def get_ad_details(url, click_limit):
            options = Options()
            # Set up Selenium
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--start-maximized")
            service = Service('chromedriver-win64/chromedriver.exe')  # Change this to your chromedriver path
            driver = webdriver.Chrome(service=service, options=options)

            # Navigate to the URL
            driver.get(url)
            wait = WebDriverWait(driver, 10)

            ad_data = []
            clicks = 0
            scrolls = 0

            try:
                while clicks < click_limit:
                    try:
                        # Find and click "See ad details"
                        see_ad_details_buttons = driver.find_elements(By.XPATH,
                                                                      "//div[contains(@class, 'x8t9es0 x1fvot60 xxio538 x1heor9g xuxw1ft x6ikm8r x10wlt62 xlyipyv x1h4wwuj x1pd3egz xeuugli') and text()='See ad details']")
                        print(f"Found {len(see_ad_details_buttons)} 'See ad details' buttons")

                        if len(see_ad_details_buttons) == 0:
                            if scrolls > 20:
                                print("No more 'See ad details' buttons found after 20 scrolls")
                                break
                            driver.execute_script("window.scrollBy(0, 300);")
                            time.sleep(2)
                            scrolls += 1
                            continue

                        if clicks >= len(see_ad_details_buttons):
                            driver.execute_script("window.scrollBy(0, 300);")
                            time.sleep(2)
                            continue

                        # Ensure the button is clickable before clicking
                        button = see_ad_details_buttons[clicks]
                        wait.until(EC.element_to_be_clickable((By.XPATH,
                                                               "//div[contains(@class, 'x8t9es0 x1fvot60 xxio538 x1heor9g xuxw1ft x6ikm8r x10wlt62 xlyipyv x1h4wwuj x1pd3egz xeuugli') and text()='See ad details']")))
                        button.click()
                        time.sleep(1)  # Wait for the ad details to load

                        # Get ad title
                        ad_title = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                              "//div[contains(@class, '_4ik4 _4ik5') and contains(@style, 'line-height: 20px; max-height: 40px; -webkit-line-clamp: 2;')]"))).text
                        print(f"Ad Title: {ad_title}")

                        # Click on "European Union transparency"
                        transparency_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                                     "//div[contains(@class, 'x8t9es0 xm46was x1xlr1w8 x63nzvj x4hq6eo xq9mrsl x1yc453h x1h4wwuj xeuugli') and text()='European Union transparency']")))
                        transparency_button.click()
                        time.sleep(2)  # Wait for the transparency page to load

                        # Get the reach number
                        reach_divs = wait.until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                     "//div[contains(@class, 'x8t9es0 x10d9sdx xo1l8bm xrohxju x108nfp6 xq9mrsl x1h4wwuj xeuugli')]")))
                        if len(reach_divs) >= 3:
                            reach_number = reach_divs[2].text
                            print(f"Reach: {reach_number}")
                        else:
                            print("Not enough reach divs found")
                            reach_number = "N/A"

                        # Find the specific div and get the subsequent div elements with the desired class
                        heading_div = driver.find_element(By.XPATH,
                                                          "//div[contains(@class, 'x8t9es0 x1uxerd5 xrohxju x108nfp6 xq9mrsl x1h4wwuj x117nqv4 xeuugli') and text()='Reach by location, age and gender']")
                        table_divs = heading_div.find_elements(By.XPATH,
                                                               "following::div[contains(@class, 'x1yrsyyn x10b6aqq')]")
                        print(f"Found {len(table_divs)} divs with class 'x1yrsyyn x10b6aqq' after the specific heading")

                        table_data = []
                        for i in range(0, len(table_divs),
                                       4):  # Ensure there are enough divs left to form a complete row
                            if i + 3 < len(table_divs):  # Ensure there are enough divs left to form a complete row
                                row = [table_divs[i].text, table_divs[i + 1].text, table_divs[i + 2].text,
                                       table_divs[i + 3].text]
                                table_data.append(row)
                                print(f"Row data: {row}")

                        # Add data to the list
                        ad_data.append({
                            "Ad Title": ad_title,
                            "Reach": reach_number,
                            "Table Data": table_data
                        })

                        # Press escape to go back
                        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(1)
                        clicks += 1

                    except Exception as e:
                        print(f"An error occurred: {e}")
                        # Press escape to go back and continue
                        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(1)
                        clicks += 1  # Ensure we move to the next button


            finally:

                print("finally calls")

                # Save data to CSV

                if ad_data:

                    print("finally calls 2")

                    try:

                        df = pd.DataFrame(ad_data)

                        df.to_csv('ad_data.csv', index=False)

                        print("Data saved to ad_data.csv")
                        df = pd.read_csv('ad_data.csv')

                        df = pd.read_csv('ad_data.csv')

                        # The user who triggered the action
                        current_user = request.user

                        # Iterate through the DataFrame rows and save to the UserData model
                        for _, row in df.iterrows():
                            ad_title = row.get("Ad Title", "")
                            reach = row.get("Reach", "")
                            countries = row.get("Table Data", "")  # Adjust field names as necessary

                            # Create a UserData instance and save it
                            user_data = UserData(
                                user=current_user,
                                link=url,
                                ad_title=ad_title,
                                reach=reach,
                                countries=countries
                            )
                            user_data.save()

                        # Display the data
                        print(df.head())
                        print(request.user)

                    except Exception as e:
                        print(f"Error saving file: {e}")

                else:
                    print(request.user)

                    print("No data to save")

                # Quit the driver
                driver.quit()

        get_ad_details(url, click_limit)
        return redirect("/dashboard")

class Migrations(View):
    @staticmethod
    def get(request):
        admin_email = "admin@gmail.com"

        if not User.objects.filter(email=admin_email).exists():
            admin_user = User(
                username="admin",
                email=admin_email,
                is_superuser=True,
                is_active=True,
                is_staff=True,
            )
            admin_user.set_password('Admin@123')
            admin_user.save()
        return redirect("/")

