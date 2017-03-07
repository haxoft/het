from elasticsearch import Elasticsearch
from pdfminer.layout import *
from hetaddon.pdfparser import PdfParser
import os
import re
import math
from typing import List


es = Elasticsearch()


class BulletpointList:
    alpha = "alpha"
    roman_numeral = "roman"
    numeral = "numeral"

    roman_numerals = ["i","ii","iii","iv","v","vi","vii","viii","ix","x","xi","xii","xiii","xiv","xv","xvi","xvii",
                      "xviii","xix","xx","xxi","xxii","xxiii","xxiv","xxv","xxvi","xxvii","xxviii","xxix","xxx"]

    def __init__(self, bulletpoints, element_after):
        self.bulletpoints = bulletpoints
        self.element_after = element_after

    def validate(self) -> int:
        bulletpoint_index = 0
        if type == BulletpointList.alpha:
            bullet_parameter = ord('a')
            condition = lambda b: b.value[0] != chr(bullet_parameter)
        elif type == BulletpointList.roman_numeral:
            bullet_parameter = 0
            condition = lambda b: b.value.startswith(BulletpointList[bullet_parameter])
        elif type == BulletpointList.numeral:
            bullet_parameter = 1
            condition = lambda b: b.value.startswith(str(bullet_parameter))
        else:
            bullet_parameter = 0
            condition = lambda b: b.value.startswith(b.type)
        while bulletpoint_index < len(self.bulletpoints):
            bulletpoint = self.bulletpoints[bulletpoint_index]
            if condition(bulletpoint):
                break
            bullet_parameter += 1
            bulletpoint_index += 1
        return bulletpoint_index


class RankedResult:
    def __init__(self, value: str, rating: float):
        self.value = value
        self.rating = rating
        self.rejected = False


class RequirementResults:
    def __init__(self, name: str, ranked_results: List[RankedResult], values_shown: int):
        self.name = name
        self.ranked_results = ranked_results
        self.values_shown = values_shown

    def reject_current(self):
        first_unrejected = self.get_current()
        if first_unrejected is not None:
            first_unrejected.rejected = True

    def get_current(self):
        return next((r for r in self.ranked_results if not r.rejected), None)


class ExtractorDocument:
    def __init__(self, document):
        self.document = document
        self.index_name = "document_" + str(self.document.id)
        self.requirements = []
        self.plain_content = ""
        es.indices.delete(index=self.index_name, ignore=[400, 404])
        es.indices.create(index=self.index_name)

        if self.document.type == "pdf":
            self.do_parse_pdf()
        else:
            raise NotImplementedError

        self.initialize_matches()
        self.initialize_sections()
        self.initialize_bulletpoints()

    def initialize_matches(self):
        self.date_matches = get_date_matches(self.plain_content)
        self.money_matches = get_money_matches(self.plain_content)
        self.duration_matches = get_duration_matches(self.plain_content)
        self.funded_proposal_amount_matches = get_funded_proposal_amount_matches(self.plain_content)
        self.email_address_matches = get_email_address_matches(self.plain_content)
        self.phone_number_matches = get_phone_number_matches(self.plain_content)

    def initialize_sections(self):
        all_results = es.search(index=self.index_name, body={"size": 10000, "query": {"match_all": {}}})["hits"]["hits"]
        caption_pattern = re.compile("^([1-9][0-9]?\.)*[1-9][0-9]?\.")
        self.caption_results = [r for r in all_results if caption_pattern.match(r["_source"]["text"])]
        self.caption_results.sort(key=lambda r: r["_source"]["y"])

    def initialize_bulletpoints(self):
        all_results = es.search(index=self.index_name, body={"size": 10000, "query": {"match_all": {}}})["hits"]["hits"]
        all_results.sort(key=lambda r:r["_source"]["x"])
        all_results.sort(key=lambda r:r["_source"]["y"])
        bullet = "(•|􀂃|-|􀂃|-||||◦|●|◘|◉|·|—|–|→|■)"
        alpha = "(\([a-z]\)|[a-z]\.)"
        roman_numeral = "(x{0,3}(ix|iv|v?i{0,3})(\)|\.))"
        final_regex = "^\s*({bullet}|{alpha}|{roman_numeral})" \
            .format(bullet=bullet, alpha=alpha, roman_numeral=roman_numeral)
        # numeral = "([1-9][0-9]?(\)|\.)(?![0-9]))"
        # final_regex = "^\s*({bullet}|{alpha}|{roman_numeral}|{numeral})"\
        #     .format(bullet=bullet, alpha=alpha, roman_numeral=roman_numeral, numeral=numeral)
        bullet_pattern = re.compile(bullet)
        alpha_pattern = re.compile(alpha)
        roman_numeral_pattern = re.compile(roman_numeral)
        # numeral_pattern = re.compile(numeral)
        bulletpoint_pattern = re.compile(final_regex)
        bulletpoint_results = [r for r in all_results if bulletpoint_pattern.match(r["_source"]["text"])]
        bulletpoint_lists = []
        next_list = []
        while len(bulletpoint_results) > 0:
            if len(bulletpoint_lists) == 6:
                x = 5
            current_result = bulletpoint_results[0]
            current_text = current_result["_source"]["text"]
            if bullet_pattern.match(current_text):
                current_type = current_text[0]
            elif alpha_pattern.match(current_text):
                current_type = "alpha"
            elif roman_numeral_pattern.match(current_text):
                current_type = "roman_numeral"
            else:
                current_type = "numeral"
            current_y = current_result["_source"]["y"]
            current_x = current_result["_source"]["x"]
            current_parent = current_result["_source"]["parent_element"]
            potential_bulletpoint_list = [r for r in bulletpoint_results if abs(r["_source"]["x"] - current_x) < 3 and r["_id"] != current_result["_id"]]
            potential_bulletpoint_index = 0
            all_results_index = all_results.index(current_result) + 1
            contained = True
            bulletpoints = [current_result]
            while potential_bulletpoint_index < len(potential_bulletpoint_list):
                next_potential_bulletpoint = potential_bulletpoint_list[potential_bulletpoint_index]
                next_result_text = next_potential_bulletpoint["_source"]["text"]
                next_result_y = next_potential_bulletpoint["_source"]["y"]
                if bullet_pattern.match(next_result_text):
                    next_result_type = next_result_text[0]
                elif alpha_pattern.match(next_result_text):
                    next_result_type = "alpha"
                elif roman_numeral_pattern.match(next_result_text):
                    next_result_type = "roman_numeral"
                else:
                    next_result_type = "numeral"
                if next_result_y > current_y + 500:
                    break
                if current_type != next_result_type:
                    potential_bulletpoint_index += 1
                    continue
                while all_results[all_results_index] != next_potential_bulletpoint:
                    all_result_source = all_results[all_results_index]["_source"]
                    if all_result_source["parent_element"] == current_parent:
                        all_results_index += 1
                        continue
                    if all_result_source["x"] < current_x:
                        contained = False
                        break
                    if all_result_source["y"] > current_y + 300:
                        contained = False
                        break
                    all_results_index += 1
                if not contained:
                    break
                all_results_index += 1
                potential_bulletpoint_index += 1
                bulletpoints.append(next_potential_bulletpoint)
                current_y = next_result_y
            if len(bulletpoints) >= 2:
                bulletpoint_list = BulletpointList(bulletpoints, all_results[all_results_index])
                bulletpoint_lists.append(bulletpoint_list)
            bulletpoint_results = [r for r in bulletpoint_results if r not in bulletpoints]
        self.bulletpoint_lists = bulletpoint_lists

    def do_parse_pdf(self):
        pdf_parser = PdfParser(self.document)
        pages = pdf_parser.get_pages()
        bulk_elements = []
        element_index = 0
        element_group_index = 0
        self.plain_content = ""
        plain_content_index = 0
        base_y = 0
        for page in pages:
            page_elements = []
            page_height = page.height
            elements = list(page)
            elements.sort(key=lambda e: e.x0)
            elements.sort(key=lambda e: e.y0, reverse=True)
            for element in elements:
                element_type = type(element)
                if element_type is LTTextBoxHorizontal:
                    for line in element:
                        page_element = {"text": line.get_text(), "x": line.x0, "y": base_y + page_height - line.y0,
                                        "width": line.width, "height": line.height,
                                        "parent_element": element_group_index}
                        page_elements.append(page_element)
                elif element_type is LTFigure or element_type is LTRect or element_type is LTCurve:
                    page_element = {"text": "", "x": element.x0, "y": base_y + page_height - element.y0,
                                    "width": element.width, "height": element.height,
                                    "parent_element": element_group_index}
                    page_elements.append(page_element)
                else:
                    page_element = {"text": "", "x": element.x0, "y": base_y + page_height - element.y0,
                                    "width": element.width, "height": element.height,
                                    "parent_element": element_group_index}
                    page_elements.append(page_element)
                element_group_index += 1
            base_y += page_height
            for element in page_elements:
                element_text = element["text"]
                element["text_start_index"] = plain_content_index
                element["text_end_index"] = plain_content_index + len(element_text) - 1
                action = {
                    "index": {
                        "_index": self.index_name,
                        "_type": "document",
                        "_id": element_index
                    }
                }
                bulk_elements.append(action)
                bulk_elements.append(element)
                element_index += 1
                plain_content_index += len(element_text) + 1
            self.plain_content += '\n'.join(e['text'] for e in page_elements)
            self.plain_content = re.sub("-\n\s*", "-", self.plain_content)
            plain_content_index -= 1

        pdf_parser.close_file()
        es.bulk(index=self.index_name, body=bulk_elements, refresh=True)

        return

    def do_extraction(self):
        self.extract_important_dates()
        self.extract_budget()
        self.extract_duration()
        self.extract_funded_proposal_amount()
        self.extract_communication_channels()
        self.extract_types_of_actions()
        self.extract_admissibility_requirements()
        self.extract_eligibility_requirements()

    def extract_important_dates(self):
        deadline_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"bool": {"should": [
                {"match": {"text": "deadline"}},
                {"match_phrase": {"text": "closing date"}}
            ]}}
        ], "should": [
            {"match_phrase": {"text": {"query": "deadline submission", "slop": 20}}},
            {"match_phrase_prefix": {"text": {"query": "deadline submit", "slop": 20}}}
        ]}}})
        evaluation_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match": {"text": "evaluation"}}
        ], "should": [
            {"match": {"text": "period"}}
        ]}}})
        signature_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match": {"text": "signature"}}
        ], "should": [
            {"match_phrase": {"text": {"query": "signature agreement", "slop": 20}}},
            {"match_phrase": {"text": {"query": "signature grant", "slop": 20}}}
        ]}}})
        applicant_information_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"should": [
            {"match": {"text": "information"}},
            {"match": {"text": "applicant"}}
        ]}}})
        publication_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match": {"text": "publication"}}
        ], "should": [
            {"match_phrase": {"text": {"query": "publication call", "slop": 20}}}
        ]}}})
        starting_date_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match_phrase_prefix": {"text": {"query": "date start", "slop": 10}}}
        ], "should": [
            {"match": {"text": "action"}}
        ]}}})

        potential_deadlines = self.get_result_matches(deadline_results, self.date_matches, 250)
        potential_evaluation_dates = self.get_result_matches(evaluation_results, self.date_matches, 250)
        potential_signature_dates = self.get_result_matches(signature_results, self.date_matches, 250)
        potential_applicant_information_dates = self.get_result_matches(applicant_information_results, self.date_matches, 250)
        potential_publication_dates = self.get_result_matches(publication_results, self.date_matches, 250)
        potential_starting_dates = self.get_result_matches(starting_date_results, self.date_matches, 250)

        potential_deadlines.sort(key=lambda r: r.rating, reverse=True)
        potential_evaluation_dates.sort(key=lambda r: r.rating, reverse=True)
        potential_signature_dates.sort(key=lambda r: r.rating, reverse=True)
        potential_applicant_information_dates.sort(key=lambda r: r.rating, reverse=True)
        potential_publication_dates.sort(key=lambda r: r.rating, reverse=True)
        potential_starting_dates.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Deadline", potential_deadlines, 1))
        self.requirements.append(RequirementResults("Evaluation", potential_evaluation_dates, 1))
        self.requirements.append(RequirementResults("Signature", potential_signature_dates, 1))
        self.requirements.append(RequirementResults("Applicant Information", potential_applicant_information_dates, 1))
        self.requirements.append(RequirementResults("Publication", potential_publication_dates, 1))
        self.requirements.append(RequirementResults("Starting Date", potential_starting_dates, 1))

        return

    def extract_budget(self):
        total_budget_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match": {"text": "budget"}}
        ], "should": [
            {"match_phrase": {"text": {"query": "total budget", "slop": 10}}}
        ]}}})
        grant_amount_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"should": [
            {"match": {"text": "grant"}},
            {"match": {"text": "budget"}},
            {"match": {"text": "between"}}
        ]}}})

        potential_total_budgets = self.get_result_matches(total_budget_results, self.money_matches, 250)
        potential_grant_amounts = self.get_result_matches(grant_amount_results, self.money_matches, 250)

        potential_total_budgets.sort(key=lambda r: r.rating, reverse=True)
        potential_grant_amounts.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Total Budget", potential_total_budgets, 1))
        self.requirements.append(RequirementResults("Grant Amount", potential_grant_amounts, 2))

        return

    def extract_duration(self):
        duration_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match": {"text": "duration"}}
        ], "should": [
            {"match_phrase": {"text": {"query": "project duration", "slop": 10}}}
        ]}}})

        potential_durations = self.get_result_matches(duration_results, self.duration_matches, 250)

        potential_durations.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Duration", potential_durations, 1))

        return

    def extract_funded_proposal_amount(self):
        funded_proposal_amount_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"prefix": {"text": "fund"}}
        ], "should": [
            {"match_phrase_prefix": {"text": {"query": "approximately fund", "slop": 10}}},
            {"regexp": {"text": "[1-9][0-9]*\s*to\s*[1-9][0-9]*\s*proposals"}},
            {"match_phrase": {"text": {"query": "single proposal", "slop": 5}}},
            {"match_phrase": {"text": {"query": "only one proposal", "slop": 5}}}
        ]}}})

        potential_funded_proposal_amounts = self.get_result_matches(funded_proposal_amount_results,
                                                                    self.funded_proposal_amount_matches, 250)

        potential_funded_proposal_amounts.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Amount of Funded Proposals", potential_funded_proposal_amounts, 1))

        return

    def extract_communication_channels(self):
        technical_contact_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"match": {"text": "technical"}},
            {"match": {"text": "contact"}}
        ], "should": [
            {"match_phrase": {"text": {"query": "technical problem", "slop": 10}}},
            {"match_phrase": {"text": {"query": "technical questions", "slop": 10}}}
        ]}}})
        general_contact_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"bool": {"should": [
                {"match": {"text": "contact"}},
                {"match": {"text": "enquiries"}},
                {"match": {"text": "questions"}}
            ]}}
        ], "should": [
        ]}}})

        potential_technical_contact_emails = self.get_result_matches(technical_contact_results, self.email_address_matches, 250)
        potential_technical_contact_phone_numbers = self.get_result_matches(technical_contact_results, self.phone_number_matches, 250)
        potential_general_contact_emails = self.get_result_matches(general_contact_results, self.email_address_matches, 250)
        potential_general_contact_phone_numbers = self.get_result_matches(general_contact_results, self.phone_number_matches, 250)

        potential_technical_contact_emails.sort(key=lambda r: r.rating, reverse=True)
        potential_technical_contact_phone_numbers.sort(key=lambda r: r.rating, reverse=True)
        potential_general_contact_emails.sort(key=lambda r: r.rating, reverse=True)
        potential_general_contact_phone_numbers.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Technical Contact Email", potential_technical_contact_emails, 1))
        self.requirements.append(RequirementResults("Technical Contact Phone Number", potential_technical_contact_phone_numbers, 1))
        self.requirements.append(RequirementResults("General Contact Email", potential_general_contact_emails, 1))
        self.requirements.append(RequirementResults("General Contact Phone Number", potential_general_contact_phone_numbers, 1))

        return

    def extract_types_of_actions(self):
        types_of_actions_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"bool": {"should": [
                {"match_phrase": {"text": {"query": "type action", "slop": 10}}},
                {"match_phrase": {"text": {"query": "types action", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "type activit", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "types activit", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "activities support", "slop": 10}}},
                {"match_phrase": {"text": {"query": "funding be granted", "slop": 5}}},
                {"match_phrase_prefix": {"text": {"query": "activities includ", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "applications fund", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "applications support", "slop": 10}}},
                {"match_phrase": {"text": {"query": "specific objective", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "objective fund", "slop": 10}}},
                {"match_phrase_prefix": {"text": {"query": "applications address", "slop": 15}}}
            ]}}
        ], "should": [
            {"match_phrase": {"text": "to be funded"}},
            {"match_phrase": {"text": "activities aimed to"}},
            {"match_phrase": {"text": "activities aimed to"}}
        ]}}})

        potential_types_of_actions = self.get_result_bulletpoint_lists(types_of_actions_results, 300)

        potential_types_of_actions.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Types of Actions", potential_types_of_actions, 2))

    def extract_admissibility_requirements(self):
        admissibility_requirements_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"bool": {"should": [
                {"match_phrase": {"text": {"query": "admissibility requirements", "slop": 3}}}
            ]}}
        ], "should": [
        ]}}})

        potential_admissibility_requirements = self.get_result_sections(admissibility_requirements_results)

        potential_admissibility_requirements.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Admissibility Requirements", potential_admissibility_requirements, 1))

    def extract_eligibility_requirements(self):
        eligibility_requirements_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must": [
            {"bool": {"should": [
                {"match_phrase": {"text": "eligibility requirements"}},
                {"match_phrase": {"text": "eligibility criteria"}}
            ]}}
        ], "should": [
        ]}}})

        potential_eligibility_requirements = self.get_result_sections(eligibility_requirements_results)

        potential_eligibility_requirements.sort(key=lambda r: r.rating, reverse=True)

        self.requirements.append(RequirementResults("Eligibility Requirements", potential_eligibility_requirements, 1))

    def get_result_matches(self, search_results, match_positions, maximum_distance: float) -> List[RankedResult]:
        if not match_positions:
            return []
        result_matches = []
        for result in search_results["hits"]["hits"]:
            for match in match_positions:
                result_match_difference = self.get_result_match_distance(result, match)
                if result_match_difference <= maximum_distance:
                    match_string = self.plain_content[match[0]:match[1]].replace("\r", " ").replace("\n", " ")
                    match_string = re.sub("[\s\r\n]+", " ", match_string)
                    result_matches.append(RankedResult(match_string, get_result_match_weighting(result["_score"], result_match_difference)))
        return result_matches

    def get_result_sections(self, search_results):
        if not self.caption_results:
            return []
        result_sections = []
        for result in search_results["hits"]["hits"]:
            y_result = result["_source"]["y"]
            previous_caption = None
            next_caption = None
            for caption_result in self.caption_results:
                if caption_result["_source"]["y"] <= y_result:
                    previous_caption = caption_result
                else:
                    if not previous_caption:
                        next_caption = caption_result
                        break
                    previous_caption_number = re.search("^([1-9][0-9]?\.)*[1-9][0-9]?\.", previous_caption["_source"]["text"]).group()
                    previous_caption_depth = previous_caption_number.count('.')
                    current_caption_number = re.search("^([1-9][0-9]?\.)*[1-9][0-9]?\.", caption_result["_source"]["text"]).group()
                    current_caption_depth = current_caption_number.count('.')
                    if current_caption_depth <= previous_caption_depth:
                        next_caption = caption_result
                        break
            if previous_caption is None:
                if next_caption is None:
                    value = ""
                else:
                    value = self.plain_content[:next_caption["_source"]["text_start_index"] - 1]
            else:
                if next_caption is None:
                    value = self.plain_content[previous_caption["_source"]["text_start_index"]:]
                else:
                    value = self.plain_content[previous_caption["_source"]["text_start_index"]:next_caption["_source"]["text_start_index"] - 1]
            value_word_count = len(re.findall("[a-zA-Z]+", value)) + 1
            if value_word_count < 20:
                distance = 20.0 / value_word_count
            else:
                distance = 1.0
            result_sections.append(RankedResult(value, get_result_section_weighting(result["_score"], distance)))
        return result_sections

    def get_result_bulletpoint_lists(self, search_results, maximum_distance: float):
        if not self.bulletpoint_lists:
            return []
        result_bulletpoint_lists = []
        for result in search_results["hits"]["hits"]:
            for bulletpoint_list in self.bulletpoint_lists:
                result_bulletpoint_list_difference = self.get_result_bulletpoint_list_distance(result, bulletpoint_list)
                if result_bulletpoint_list_difference <= maximum_distance:
                    rating = get_result_bulletpoint_list_weighting(result["_score"], result_bulletpoint_list_difference)
                    for bulletpoint_index in range(0, len(bulletpoint_list.bulletpoints) - 1):
                        start_index = bulletpoint_list.bulletpoints[bulletpoint_index]["_source"]["text_start_index"]
                        end_index = bulletpoint_list.bulletpoints[bulletpoint_index + 1]["_source"]["text_start_index"] - 1
                        bulletpoint_string = self.plain_content[start_index:end_index]
                        bulletpoint_string = re.sub("(\r?\n)+", "\n", bulletpoint_string)
                        result_bulletpoint_lists.append(RankedResult(bulletpoint_string, rating))
                    start_index = bulletpoint_list.bulletpoints[-1]["_source"]["text_start_index"]
                    end_index = bulletpoint_list.element_after["_source"]["text_start_index"] - 1
                    bulletpoint_string = self.plain_content[start_index:end_index]
                    bulletpoint_string = re.sub("(\r?\n)+", "\n", bulletpoint_string)
                    result_bulletpoint_lists.append(RankedResult(bulletpoint_string, rating))
        return result_bulletpoint_lists

    def get_result_match_distance(self, result, match) -> float:
        match_start = match[0]
        match_end = match[1]
        match_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must_not": [
            {"range":
                {"text_end_index":
                    {
                        "lt": match_start
                    }
                }
            },
            {"range":
                {"text_start_index":
                    {
                        "gt": match_end
                    }
                }
            }
        ]}}})

        distance = min(get_distance(result, e) for e in match_results["hits"]["hits"])
        if distance == 0:
            distance = 0.1
        return distance

    def get_result_bulletpoint_list_distance(self, result, bulletpoint_list: BulletpointList) -> float:
        first_element = bulletpoint_list.bulletpoints[0]
        element_after = bulletpoint_list.element_after
        bulletpoint_list_results = es.search(index=self.index_name, body={"size": 10000, "query": {"bool": {"must_not": [
            {"range":
                {"text_end_index":
                    {
                        "lt": first_element["_source"]["text_start_index"]
                    }
                }
            },
            {"range":
                {"text_start_index":
                    {
                        "gte": element_after["_source"]["text_start_index"]
                    }
                }
            }
        ]}}})["hits"]["hits"]
        distance = min(get_distance(result, e) for e in bulletpoint_list_results)
        if distance < 5:
            distance = 5
        return distance

    def print_requirements(self):
        for requirement in self.requirements:
            print()
            print(requirement.name)
            for result in requirement.ranked_results:
                print(result.value)


class RequirementExtractor:
    def __init__(self, documents):
        self.finished = False
        self.documents = []
        for document in documents:
            self.documents.append(ExtractorDocument(document))

    def do_extraction(self):
        self.finished = False
        for document in self.documents:
            document.do_extraction()
        self.finished = True


def get_date_matches(plain_content):
    plain_content = plain_content.lower()
    month = "(january|february|march|april|may|june|july|august|september|october|november|december)"
    short_month = "(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    month_number = "(0?[1-9]|1[0-2])"
    day = "([0-2]?[1-9]|[123]0|31)"
    year = "(2[0-1][0-9]{2})"
    time = "([0-9]{2}:[0-9]{2}(:[0-9]{2}))?"

    regex_1 = "(({month}|{short_month})\s*{day}(,\s*{year})?(?=[^0-9]))" \
        .format(month=month, short_month=short_month, day=day, year=year)
    regex_2 = "((({day}\s*(-|to|or|\/)\s*)?{day}\s*)?{month}(\s*{year})?)".format(day=day, year=year, month=month)
    regex_3 = "((({day}\s*(-|to|or|\/)\s*)?{day}\s*){short_month})(?=\s)".format(day=day, short_month=short_month)
    regex_4 = "({short_month}(\s*{year}))".format(short_month=short_month, year=year)
    regex_5 = "({day}(\/|\.|-){month_number}(\/|\.|-){year})".format(day=day, month_number=month_number, year=year)
    regex_6 = "({month_number}(\/|\.|-){day}(\/|\.|-){year})".format(day=day, month_number=month_number, year=year)
    regex_7 = "({year}(\/|\.|-){month_number}(\/|\.|-){day})".format(day=day, month_number=month_number, year=year)

    date = "({regex_1}|{regex_2}|{regex_3}|{regex_4}|{regex_5}|{regex_6}|{regex_7})" \
        .format(regex_1=regex_1, regex_2=regex_2, regex_3=regex_3, regex_4=regex_4, regex_5=regex_5, regex_6=regex_6,
                regex_7=regex_7)

    year_span = "({year}\s*-\s*{year})".format(year=year)
    date_span = "({date}\s*(-|to|or|\/)\s*{date})".format(date=date)
    verbose_date = "(((from|until)\s*)?(early(\sin)?|beginning\sof|end(\sof)?|mid(-|\sof)|as\sof)\s*({year}|{month}\s*{year}?))" \
        .format(month=month, year=year)

    final_regex = "{year_span}|{date_span}|{verbose_date}|{date}" \
        .format(date=date, year_span=year_span, date_span=date_span, verbose_date=verbose_date)

    return get_match_positions(final_regex, plain_content, 4)


def get_money_matches(plain_content):
    plain_content = plain_content.lower()
    currency = "(eur|€|\$)"
    amount_number = "([1-9][0-9]{0,2}(.?[0-9]{3})+)"
    amount_verbose = "[0-9]+(\.[0-9]+)?\s*(million|billion|thousand)"
    amount = "({amount_verbose}|{amount_number})".format(amount_verbose=amount_verbose, amount_number= amount_number)

    regex_1 = "({currency}\s*{amount})".format(currency=currency, amount=amount)
    regex_2 = "({amount}\s*{currency})".format(currency=currency, amount=amount)

    final_regex = "{regex_1}|{regex_2}".format(regex_1=regex_1, regex_2=regex_2)

    return get_match_positions(final_regex, plain_content)


def get_duration_matches(plain_content):
    plain_content = plain_content.lower()

    regex_1 = "(((between\s*)[1-9][0-9]*\s*(and|to)\s*?)?[1-9][0-9]*\s*(months|years))"

    final_regex = "{regex_1}".format(regex_1=regex_1)

    return get_match_positions(final_regex, plain_content)


def get_funded_proposal_amount_matches(plain_content):
    plain_content = plain_content.lower()

    regex_1 = "((single\s*|only\s*one\s*|((approximately\s*|between\s*)?[1-9][0-9]*\s*(to|and)\s*)[1-9][0-9]*)\s*proposal(s)?)"

    final_regex = "{regex_1}".format(regex_1=regex_1)

    return get_match_positions(final_regex, plain_content)


def get_email_address_matches(plain_content):
    plain_content = plain_content.lower()

    regex_1 = "([a-zA-Z0-9_+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+){1,2})"

    final_regex = "{regex_1}".format(regex_1=regex_1)

    return get_match_positions(final_regex, plain_content)


def get_phone_number_matches(plain_content):
    plain_content = plain_content.lower()

    regex_1 = "((\+?[0-9]+[\s-]?)?(\([0-9]+\)\s?)?[0-9]+([\s-][0-9]+)*)"

    final_regex = "{regex_1}".format(regex_1=regex_1)

    return get_match_positions(final_regex, plain_content, 9, False)


def get_match_positions(regex, text, minimum_length=0, multiline=True):
    results = []
    flags = 0
    if multiline:
        flags |= re.MULTILINE
    for match in re.compile(regex, flags).finditer(text):
        start_position = match.start()
        end_position = match.end()
        if end_position - start_position < minimum_length:
            continue
        results.append((start_position, end_position))
    return results


def get_distance(result1, result2):
    source1 = result1["_source"]
    source2 = result2["_source"]
    x1 = source1["x"]
    w1 = source1["width"]
    x1b = x1 + w1
    y1 = source1["y"]
    h1 = source1["height"]
    y1b = y1 + h1
    e1 = {"x": x1, "w": w1, "xb": x1b, "y": y1, "h": h1, "yb": y1b}
    x2 = source2["x"]
    w2 = source2["width"]
    x2b = x2 + w2
    y2 = source2["y"]
    h2 = source2["height"]
    y2b = y2 + h2
    e2 = {"x": x2, "w": w2, "xb": x2b, "y": y2, "h": h2, "yb": y2b}
    left = x2b < x1
    right = x1b < x2
    bottom = y1b < y2
    top = y2b < y1

    if h1 < h2:
        small = e1
        large = e2
    else:
        small = e2
        large = e1
    if small["y"] >= large["y"] and small["yb"] <= large["yb"]:
        aligned_horizontally = True
        v_offset = 0
    elif small["y"] < large["y"] and large["y"] - small["y"] <= small["h"] * 0.1:
        aligned_horizontally = True
        v_offset = large["y"] - small["y"]
    elif small["yb"] > large["yb"] and small["yb"] - large["yb"] <= small["h"] * 0.1:
        aligned_horizontally = True
        v_offset = small["yb"] - large["yb"]
    else:
        aligned_horizontally = False
        v_offset = 0
    if large["xb"] < small["x"]:
        h_offset = small["x"] - large["xb"]
    elif small["xb"] < large["x"]:
        h_offset = large["x"] - small["xb"]
    else:
        h_offset = 0
    if aligned_horizontally:
        v_offset_score = v_offset / small["h"] * 10 * 50
        h_offset_score = h_offset / (h_offset + small["w"]) * 50
        return v_offset_score + h_offset_score

    if w1 < w2:
        small = e1
        large = e2
    else:
        small = e2
        large = e1
    if small["x"] > large["x"] and small["xb"] < large["xb"]:
        aligned_vertically = True
        h_offset = 0
    elif small["x"] < large["x"] and large["x"] - small["x"] <= small["w"] * 0.3:
        aligned_vertically = True
        h_offset = large["x"] - small["x"]
    elif small["xb"] > large["xb"] and small["xb"] - large["xb"] <= small["w"] * 0.3:
        aligned_vertically = True
        h_offset = small["xb"] - large["xb"]
    else:
        aligned_vertically = False
        h_offset = 0
    if large["yb"] < small["y"]:
        v_offset = small["y"] - large["yb"]
    elif small["yb"] < large["y"]:
        v_offset = large["y"] - small["yb"]
    else:
        v_offset = 0
    maximum_v_offset = 100
    if aligned_vertically and v_offset <= maximum_v_offset:
        h_offset_score = h_offset * 10/3 * 50
        v_offset_score = v_offset / (v_offset + small["h"]) * 50
        return v_offset_score + h_offset_score

    if top:
        v_offset = y1 - y2b
    elif bottom:
        v_offset = y2 - y1b
    else:
        v_offset = 0
    if left:
        h_offset = x1 - x2b
    elif right:
        h_offset = x2 - x1b
    else:
        h_offset = 0

    return v_offset + h_offset + 100


def get_result_match_weighting(score: float, distance: float):
    return score * score / distance


def get_result_section_weighting(score: float, distance: float):
    return score / distance


def get_result_bulletpoint_list_weighting(score: float, distance: float):
    return score * score / distance


class SearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class DocumentMock:
    def __init__(self, path: str, id: int):
        file = open(path, "rb")  # opening for [r]eading as [b]inary
        data = file.read()
        size = os.path.getsize(path)
        self.id = id
        self.name = path.split("/")[-1]
        self.type = "pdf"
        self.category = "oth"
        self.content = data
        self.size = size
        file.close()


class ExtractionTest:
    id = 1

    def __init__(self):
        self.documents = []
        self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC1/VP-2016-001.pdf",
                          "30 June 2016", "Until end September 2016", "From mid-November", "From beginning of November",
                          "April 2016", None, "EUR 9 300 000", ["EUR 150 000", "EUR 500 000"], "24 months", None,
                          "empl-swim-support@ec.europa.eu", None, "empl-vp-social-dialogue@ec.europa.eu", None,
                          None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC2/Call VS-2016-015 - EN.pdf",
        #                   ("30 March 2017", "30/03/2017"), ["April 2017- June 2017", "June to September 2017"], "November 2017",
        #                   ["July 2017", "October 2017"], "21 December 2016",
        #                   "The actual starting date of the action will either be the first day following the date when the last of the two parties signs the grant agreement, or the first day of the month following the date when the last of the two parties signs or a date agreed upon between the parties.",
        #                   "EUR 14.200.000", None, "between 24 and 36 months", "approximately 5 to 7 proposals",
        #                   "empl-swim-support@ec.europa.eu", None, "empl-vp-2016-015@ec.europa.eu", None,
        #                   None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC3/VP 2016 018_ESC call text_final.pdf",
        #                   ("17 March 2017", "17 MARCH 2017"), "March/April 2017", "April 2017", "April 2017", "December 2016", "2 May 2017",
        #                   ["EUR 8.243.895", "EUR 14,243.895"], None, "24 months", "single proposal",
        #                   "empl-swim-support@ec.europa.eu", None, "empl-vp-2016-018@ec.europa.eu", None,
        #                   None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC7/2016_ceftelecom_calltext_eprocurement_final_030316.pdf",
        #                   "19 May 2016", "May-August 2016", "As of October 2016", None, "3 March 2016", None, "€4.5 million",
        #                   None, "12 months", None, None, None, "INEA-CEF-Telecom-Calls@ec.europa.eu", None,
        #                   None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC8/2016-2_ceftelecom_calltext_edelivery_superfinal_120516_0.pdf",
        #                   "15 September 2016", "September-December 2016", "As of February 2017", None, "12 May 2016", None,
        #                   "€0.5 million", None, "24 months", None, None, None, "INEA-CEF-Telecom-Calls@ec.europa.eu", None,
        #                   None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC9/2016-3_ceftelecom_calltext_cybersecurity_200916_final.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC10/2016-3_ceftelecom_calltext_einvoicing_200916_final.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC11/2016-3_ceftelecom_calltext_europeana_200916_final.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC12/2016-4_ceftelecom_call-text_safer_internet_200916_final.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC13/2016-cef-synergy_call_text_final_for_publication.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC14/2016-cef-transport_ap_general_call_text.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC15/9386_Terms of Reference_Women Part SME Instrv2 .pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC16/call_for_proposals_2015_isfb_esur_en.doc.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC17/call-text-ja-gpsd-2016_en.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC18/EIT 2016 Call for KICs proposals.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC19/EIT_2014_Call_for_KIC_proposals_0.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC20/hp-pj-2016-call-text_en.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC21/isfb_schengen_ml_call_for_proposal_en.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC22/VP 2015 009 call_mobility experience_REV_FIN.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC23/VP 2016 011_Reactivate_publication.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/ACBAR1/Attachment A - RFA - Media and Communication.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/CEPF1/RIT-Request-EOIs-Mediterranean-Basin-EN.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
        # self.add_document("C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/DFAT1/australia-indonesia-institute-grant-guidelines-2017.pdf",
        #                   None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

    def add_document(self, path: str, deadline, evaluation, signature, applicant_information, publication, starting_date,
                     total_budget, grant_amount, duration, funded_proposals_amount, technical_contact_email,
                     technical_contact_phone_number, general_contact_email, general_contact_phone_number,
                     types_of_actions, admissibility_requirements, eligibility_requirements):
        document_mock = DocumentMock(path, self.id)
        requirements_dict = {}
        requirements_dict["Deadline"] = deadline
        requirements_dict["Evaluation"] = evaluation
        requirements_dict["Signature"] = signature
        requirements_dict["Applicant Information"] = applicant_information
        requirements_dict["Publication"] = publication
        requirements_dict["Starting Date"] = starting_date
        requirements_dict["Total Budget"] = total_budget
        requirements_dict["Grant Amount"] = grant_amount
        requirements_dict["Duration"] = duration
        requirements_dict["Amount of Funded Proposals"] = funded_proposals_amount
        requirements_dict["Technical Contact Email"] = technical_contact_email
        requirements_dict["Technical Contact Phone Number"] = technical_contact_phone_number
        requirements_dict["General Contact Email"] = general_contact_email
        requirements_dict["General Contact Phone Number"] = general_contact_phone_number
        requirements_dict["Types of Actions"] = types_of_actions
        requirements_dict["Admissibility Requirements"] = admissibility_requirements
        requirements_dict["Eligibility Requirements"] = eligibility_requirements
        self.documents.append(ExtractionTestDocument(document_mock, requirements_dict))
        self.id += 1

    def do_extraction(self):
        for document in self.documents:
            document.calculate_requirement_scores()


class ExtractionTestRequirementScore:
    def __init__(self, name: str, values_needed: int, values_found: int, offset: int, ranked_results: List[RankedResult],
                 expected_values):
        self.name = name
        self.values_needed = values_needed
        self.values_found = values_found
        self.offset = offset
        self.ranked_results = ranked_results
        self.expected_values = expected_values

    def print_score(self):
        print()
        print(self.name)
        print("Found " + str(self.values_found) + " of " + str(self.values_needed))
        print("Offset: " + str(self.offset))
        print("Top result:")
        print(self.ranked_results[0].value if self.ranked_results else "No result found")
        print("Expected results:")
        for value in self.expected_values:
            print(value)


class ExtractionTestDocument:
    def __init__(self, document: DocumentMock, requirements_dict):
        self.document = document
        self.requirements_dict = requirements_dict
        self.requirement_scores = []

    def calculate_requirement_scores(self):
        extractor = RequirementExtractor([self.document])
        extractor.do_extraction()
        requirement_results = extractor.documents[0].requirements
        for key, values in self.requirements_dict.items():
            matching_result = next(r for r in requirement_results if r.name == key)
            if values is None:
                values = []
            elif isinstance(values, str):
                values = [values]
            offset = 0
            offset_temp = 0
            ranked_result_index = 0
            ranked_results = matching_result.ranked_results
            if isinstance(values, tuple):
                found = False
                while ranked_result_index < len(ranked_results):
                    current_result = ranked_results[ranked_result_index]
                    if current_result.value in values:
                        found = True
                        offset += offset_temp
                        break
                    else:
                        offset_temp += 1
                requirement_score = ExtractionTestRequirementScore(key, 1, 1 if found else 0, offset, ranked_results, values)
            else:
                remaining_values = list(values)
                while len(remaining_values) > 0 and ranked_result_index < len(ranked_results):
                    current_result = ranked_results[ranked_result_index]
                    if current_result.value in remaining_values:
                        remaining_values.remove(current_result.value)
                        offset += offset_temp
                        offset_temp = 0
                    else:
                        offset_temp += 1
                    ranked_result_index += 1
                requirement_score = ExtractionTestRequirementScore(key, len(values), len(values) - len(remaining_values),
                                                                   offset, ranked_results, values)
            self.requirement_scores.append(requirement_score)

    def print_results(self):
        print()
        print(self.document.name)
        for score in self.requirement_scores:
            score.print_score()

# test = ExtractionTest()
# test.do_extraction()
# x = 5
# y = 3
#
# for document in test.documents:
#     document.print_results()
