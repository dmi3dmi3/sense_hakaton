from typing import Dict

import transformators.format1.parsing
from transformators.format1.parsing import parse_file, Resume, Vacancy, EducationItem
import pandas as pd


class Result:
    vacancy_id: str
    vacancy_main_keywords: list[str]
    vacancy_sub_keywords: list[str]
    resume_id: str
    is_english: bool
    resume_main_keywords: list[str]
    resume_sub_keywords: list[str]
    edu: list[str]
    target: int


def parse_education_items(education_items: list[EducationItem]) -> str:
    if len(education_items) == 0:
        return 'no'
    levels = list(map(lambda x: x.education_level, education_items))
    if 'Высшее' in levels:
        return 'relevant_high'
    return 'courses'


def get_result(vacancy: Vacancy, resume: Resume, target: bool):
    result = Result()
    result.vacancy_id = vacancy.uuid
    result.vacancy_main_keywords = vacancy.name.split(' ')
    result.resume_id = resume.uuid
    result.is_english = "Английский" in resume.languageItems
    if resume.key_skills:
        skills_str = (resume.key_skills
                      .replace(';', ',')
                      .replace('(', '')
                      .replace(')', ''))
        skills_list = skills_str.split(',')
        skills_list = map(lambda x: x.strip(), skills_list)
        skills_list = filter(lambda x: x != '', skills_list)
        result.resume_main_keywords = list(skills_list)
    else:
        result.resume_main_keywords = []
    result.edu = parse_education_items(resume.educationItem)
    result.target = target
    return result.__dict__


def get_count_dict(keywords: list[list[str]]) -> dict[str, int]:
    count_dict = {}
    for keyword_list in keywords:
        for keyword in keyword_list:
            if keyword in count_dict:
                count_dict[keyword] += 1
            else:
                count_dict[keyword] = 1
    return count_dict


def main():
    vacancies = parse_file('case_2_data_for_members.json')
    results = []
    for vacancy in vacancies:
        for resume in vacancy.failed_resumes:
            result = get_result(vacancy, resume, False)
            results.append(result)
        for resume in vacancy.confirmed_resumes:
            result = get_result(vacancy, resume, True)
            results.append(result)
    df_results = pd.DataFrame(results)

    resume_keywords_count_dict = get_count_dict(df_results['resume_main_keywords'])
    print(len(resume_keywords_count_dict))
    rare_keywords = []
    for keyword, count in resume_keywords_count_dict.items():
        if count < 10:
            rare_keywords.append(keyword)

    # remove from resume_main_keywords rare keywords
    df_results['resume_main_keywords'] = df_results['resume_main_keywords'].apply(lambda x: list(filter(lambda y: y not in rare_keywords, x)))
    resume_keywords_count_dict = get_count_dict(df_results['resume_main_keywords'])
    print(len(resume_keywords_count_dict))
    df_results.to_csv('case_2_results.csv', index=False)


if __name__ == '__main__':
    main()
