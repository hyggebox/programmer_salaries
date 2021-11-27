import os
import requests

from dotenv import load_dotenv
from itertools import count
from statistics import mean
from terminaltables import SingleTable



def predict_salary(salary_from, salary_to):
    if not salary_to or salary_to == 0:
        average_salary = salary_from * 1.2
    elif not salary_from or salary_from == 0:
        average_salary = salary_to * 0.8
    else:
        average_salary = mean([salary_from, salary_to])

    if average_salary == 0:
        return None
    return average_salary


def predict_rub_salary_for_hh(salary):
    if salary:
        if salary["currency"] == "RUR":
            return predict_salary(salary["from"], salary["to"])
        return None
    return None


def predict_rub_salary_for_superjob(vacancy):
    if vacancy["currency"] == "rub":
        return predict_salary(vacancy["payment_from"], vacancy["payment_to"])
    return None


def print_table(title, processed_vacancies):
    table_content = [["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]]
    for lang, vacancies in processed_vacancies.items():
        table_content.append([
            lang,
            vacancies["vacancies_found"],
            vacancies["vacancies_processed"],
            vacancies["average_salary"]
        ])
    table = SingleTable(table_content, title)
    print(table.table)


def handle_hh_vacancies(languages):
    hh_endpoint = "https://api.hh.ru/vacancies"
    search_template = "NAME:программист {}"
    average_salary_by_lang = {}

    for lang in languages:
        all_vacancies = []
        for page in count(0):
            params = {
                "text": search_template.format(lang),
                "area": 1,
                "page": page
            }

            page_response = requests.get(hh_endpoint, params)
            page_response.raise_for_status()
            page_vacancies = page_response.json()

            all_page_vacancies = [vacancy for vacancy in page_vacancies["items"]]
            all_vacancies += all_page_vacancies

            if page >= page_vacancies["pages"]-1:
                break

        all_salaries = [vacancy["salary"] for vacancy in all_vacancies]
        processed_vacancies_salary = [predicted_salary for salary in all_salaries
                                      if (predicted_salary := predict_rub_salary_for_hh(salary)) is not None]

        average_salary_by_lang[lang] = {
            "vacancies_found": len(all_salaries),
            "vacancies_processed": len(processed_vacancies_salary),
            "average_salary": int(mean(processed_vacancies_salary))
        }

    return average_salary_by_lang


def handle_sj_vacancies(languages):
    load_dotenv()

    sj_endpoint = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": os.environ["SUPERJOB_KEY"]
    }
    average_salary_by_lang = {}

    for lang in languages:
        processed_vacancies_salaries = []
        for page in count(0):
            params = {
                "keyword": f"Программист {lang}",
                "town": "Москва",
                "page": page,
                "count": 100
            }

            response = requests.get(sj_endpoint, headers=headers, params=params)
            response.raise_for_status()
            sj_vacancies_found = response.json()["total"]
            sj_page_vacancies = response.json()["objects"]

            for vacancy in sj_page_vacancies:
                if predict_rub_salary_for_superjob(vacancy):
                    processed_vacancies_salaries.append(predict_rub_salary_for_superjob(vacancy))

            if page >= sj_vacancies_found / 100:
                break

        average_salary_by_lang[lang] = {
            "vacancies_found": sj_vacancies_found,
            "vacancies_processed": len(processed_vacancies_salaries),
            "average_salary": int(mean(processed_vacancies_salaries))
        }

    return average_salary_by_lang



if __name__ == "__main__":
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C", "C#", "C++", "Swift", "Go"]
    hh_title = "HeadHunter, Москва"
    sj_title = "SuperJob, Москва"

    print_table(hh_title, handle_hh_vacancies(languages))
    print_table(sj_title, handle_sj_vacancies(languages))



