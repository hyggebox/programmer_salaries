import os
import requests

from dotenv import load_dotenv
from itertools import count
from statistics import mean
from terminaltables import SingleTable



def predict_salary(salary_from, salary_to):
    if not salary_to:
        average_salary = salary_from * 1.2
    elif not salary_from:
        average_salary = salary_to * 0.8
    else:
        average_salary = mean([salary_from, salary_to])

    if average_salary == 0:
        return None
    return average_salary


def predict_rub_salary_for_hh(salary):
    if salary and salary["currency"] == "RUR":
        return predict_salary(salary["from"], salary["to"])
    return None


def predict_rub_salary_for_superjob(vacancy):
    if vacancy["currency"] == "rub":
        return predict_salary(vacancy["payment_from"], vacancy["payment_to"])
    return None


def make_table(title, processed_vacancies):
    table_content = [["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]]
    for lang, vacancies in processed_vacancies.items():
        table_content.append([
            lang,
            vacancies["vacancies_found"],
            vacancies["vacancies_processed"],
            vacancies["average_salary"]
        ])
    table = SingleTable(table_content, title)
    return table.table


def handle_hh_vacancies(languages):
    hh_endpoint = "https://api.hh.ru/vacancies"
    search_template = "NAME:программист {}"
    average_salary_by_lang = {}

    for lang in languages:
        all_vacancies = []
        moscow_id = 1
        params = {
            "text": search_template.format(lang),
            "area": moscow_id
        }
        for page in count(0):
            params["page"] = page
            page_response = requests.get(hh_endpoint, params)
            page_response.raise_for_status()
            page_vacancies = page_response.json()

            all_vacancies += [vacancy for vacancy in page_vacancies["items"]]

            if page >= page_vacancies["pages"]-1:
                break

        all_salaries = [vacancy["salary"] for vacancy in all_vacancies]
        processed_vacancies_salary = [predicted_salary for salary in all_salaries
                                      if (predicted_salary := predict_rub_salary_for_hh(salary))]

        average_salary_by_lang[lang] = {
            "vacancies_found": page_vacancies["found"],
            "vacancies_processed": len(processed_vacancies_salary),
            "average_salary": int(mean(processed_vacancies_salary))
        }

    return average_salary_by_lang


def handle_sj_vacancies(languages, token):
    sj_endpoint = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": token
    }
    average_salary_by_lang = {}

    for lang in languages:
        processed_vacancies_salaries = []
        for page in count(0):
            params = {
                "keyword": f"Программист {lang}",
                "town": "Москва",
                "page": page
            }

            response = requests.get(sj_endpoint, headers=headers, params=params)
            response.raise_for_status()
            sj_response = response.json()
            sj_vacancies_found = sj_response["total"]
            sj_page_vacancies = sj_response["objects"]

            for vacancy in sj_page_vacancies:
                if predict_rub_salary_for_superjob(vacancy):
                    processed_vacancies_salaries.append(predict_rub_salary_for_superjob(vacancy))

            if not sj_response["more"]:
                break

        average_salary_by_lang[lang] = {
            "vacancies_found": sj_vacancies_found,
            "vacancies_processed": len(processed_vacancies_salaries),
            "average_salary": int(mean(processed_vacancies_salaries))
        }

    return average_salary_by_lang



if __name__ == "__main__":
    load_dotenv()
    sj_token = os.environ["SUPERJOB_KEY"]
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C", "C#", "C++", "Swift", "Go"]
    hh_title = "HeadHunter, Москва"
    sj_title = "SuperJob, Москва"

    print(make_table(hh_title, handle_hh_vacancies(languages)))
    print(make_table(sj_title, handle_sj_vacancies(languages, sj_token)))



