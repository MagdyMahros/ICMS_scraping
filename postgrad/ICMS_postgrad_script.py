"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 19-11-20
    * description:This script extracts the corresponding undergraduate courses details and tabulate it.
"""

import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/ICMS_postgrad_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/ICMS_postgrad.csv'

course_data = {'Level_Code': '', 'University': 'International College of Management Sydney', 'City': '',
               'Country': 'Australia', 'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD',
               'Currency_Time': 'year', 'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '',
               'Prerequisite_1': '', 'Prerequisite_2': 'IELTS', 'Prerequisite_3': '', 'Prerequisite_1_grade': '',
               'Prerequisite_2_grade': '7', 'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '',
               'Availability': 'A', 'Description': '', 'Career_Outcomes': '', 'Online': '', 'Offline': '',
               'Distance': 'no', 'Face_to_Face': '', 'Blended': 'no', 'Remarks': ''}

possible_cities = {
                   'online': 'Online', 'mixed': 'Online', 'brisbane': 'Brisbane', 'sydney': 'Sydney',
                   'melbourne': 'Melbourne', 'perth': 'Perth'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    remarks_list = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # COURSE TITLE
    title_tag = soup.find('h1', class_='page-title')
    if title_tag:
        course_data['Course'] = title_tag.get_text().strip()
        print('COURSE TITLE: ', course_data['Course'])

        # DECIDE THE LEVEL CODE
        for i in level_key:
            for j in level_key[i]:
                if j in course_data['Course']:
                    course_data['Level_Code'] = i
        print('COURSE LEVEL CODE: ', course_data['Level_Code'])

        # DECIDE THE FACULTY
        for i in faculty_key:
            for j in faculty_key[i]:
                if j.lower() in course_data['Course'].lower():
                    course_data['Faculty'] = i
        print('COURSE FACULTY: ', course_data['Faculty'])

        # COURSE LANGUAGE
        for language in possible_languages:
            if language in course_data['Course']:
                course_data['Course_Lang'] = language
            else:
                course_data['Course_Lang'] = 'English'
        print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # COURSE DESCRIPTION
    desc_container = soup.find('div', class_='card-body')
    if desc_container:
        desc_list = []
        desc_p_list = desc_container.find_all('p')
        if desc_p_list:
            for p in desc_p_list:
                desc_list.append(p.get_text().strip())
            desc_list = ' '.join(desc_list)
            course_data['Description'] = desc_list
            print('DESCRIPTION: ', desc_list)

    # DURATION
    duration_title = soup.find('span', text=re.compile('Duration:', re.IGNORECASE))
    if duration_title:
        duration = duration_title.find_next_sibling('span')
        if duration:
            duration_text = duration.get_text().lower()
            if 'part-time' in duration_text:
                course_data['Part_Time'] = 'yes'
                course_data['Full_Time'] = 'yes'
            else:
                course_data['Part_Time'] = 'no'
                course_data['Full_Time'] = 'yes'
            converted_duration = dura.convert_duration(duration_text)
            if converted_duration is not None:
                duration_l = list(converted_duration)
                if duration_l[0] == 1 and 'Years' in duration_l[1]:
                    duration_l[1] = 'Year'
                if duration_l[0] == 1 and 'Months' in duration_l[1]:
                    duration_l[1] = 'Month'
                course_data['Duration'] = duration_l[0]
                course_data['Duration_Time'] = duration_l[1]
                print('COURSE DURATION: ', str(duration_l[0]) + ' / ' + duration_l[1])
            print('FULL-TIME/PART-TIME: ', course_data['Full_Time'] + ' / ' + course_data['Part_Time'])

    # STUDY MODE
    studyMode_title = soup.find('span', text=re.compile('Study Mode:', re.IGNORECASE))
    if studyMode_title:
        studyMode_p = studyMode_title.find_next_sibling('span')
        if studyMode_p:
            mode_text = studyMode_p.get_text().lower()
            if 'on-campus' in mode_text:
                course_data['Face_to_Face'] = 'yes'
                course_data['Offline'] = 'yes'
            else:
                course_data['Face_to_Face'] = 'no'
                course_data['Offline'] = 'no'
            if 'online' in mode_text:
                course_data['Online'] = 'yes'
            else:
                course_data['Online'] = 'no'
    print('DELIVERY: online: ' + course_data['Online'] + ' offline: ' + course_data['Offline'] +
          ' face to face: ' + course_data['Face_to_Face'] + ' blended: ' + course_data['Blended'] +
          ' distance: ' + course_data['Distance'])

    # CITY
    campus_title = soup.find('span', text=re.compile('Campus:', re.IGNORECASE))
    if campus_title:
        location = campus_title.find_next_sibling('span')
        if location:
            location_text = location.get_text().lower().strip()
            if 'northern beaches campus' in location_text:
                actual_cities.append('sydney')
            if 'online' in location_text:
                actual_cities.append('online')
        print('LOCATION: ', actual_cities)

    # CAREER OUTCOMES
    career_container = soup.find('ul', class_='table-data')
    if career_container:
        career_list = []
        career_li = career_container.find_all('li')
        if career_li:
            for li in career_li:
                career_list.append(li.get_text().strip())
            career_list = ' / '.join(career_list)
            course_data['Career_Outcomes'] = career_list
            print('CAREER OUTCOMES: ', career_list)

    # AQF LEVEL (Australian Qualification Framework)
    aqf_level_title = soup.find('span', text=re.compile('AQF Level:', re.IGNORECASE))
    if aqf_level_title:
        aqf = aqf_level_title.find_next_sibling('span')
        if aqf:
            aqf_text = aqf.get_text().strip()
            course_data['Prerequisite_1'] = 'AQF Level'
            course_data['Prerequisite_1_grade'] = aqf_text
            print('AQF LEVEL: ', aqf_text)

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance',
                          'Face_to_Face', 'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('ICMS_postgrad_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)