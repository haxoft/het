from elasticsearch import Elasticsearch
from pdfminer.layout import *
from hetaddon.pdfparser import PdfParser
import os
import re
import math


es = Elasticsearch()


def test():
    index_name = "test-index2"
    res = es.index(index=index_name, doc_type='document', id=1, body="")
    print(res['created'])

    es.indices.refresh(index=index_name)

    index = es.indices
    term_info = index.get('employ')
    for pos in term_info:
        print(pos.startOffset)

    res = es.search(index="test-index", body={"query": {"match": {"text": "Employment"}}})
    print("Got %d Hits:" % res['hits']['total'])

    for hit in res['hits']['hits']:
        print("%(text)s" % hit["_source"])


def do_standard_extraction(documents: list):
    for document in documents:
        index_name = "document_" + str(document.id)
        es.indices.delete(index=index_name, ignore=[400, 404])
        es.indices.create(index=index_name)
        pdf_parser = PdfParser(document)
        pages = pdf_parser.get_pages()
        bulk_elements = []
        element_index = 0
        plain_content = ""
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
                                        "width": line.width, "height": line.height}
                        page_elements.append(page_element)
                elif element_type is LTFigure or element_type is LTRect or element_type is LTCurve:
                    page_element = {"text": "", "x": element.x0, "y": base_y + page_height - element.y0,
                                    "width": element.width, "height": element.height}
                    page_elements.append(page_element)
                else:
                    page_element = {"text": "", "x": element.x0, "y": base_y + page_height - element.y0,
                                    "width": element.width, "height": element.height}
                    page_elements.append(page_element)
            base_y += page_height
            for element in page_elements:
                element_text = element["text"]
                element["text_start_index"] = plain_content_index
                element["text_end_index"] = plain_content_index + len(element_text) - 1
                action = {
                    "index": {
                        "_index": index_name,
                        "_type": "document",
                        "_id": element_index
                    }
                }
                bulk_elements.append(action)
                bulk_elements.append(element)
                element_index += 1
                plain_content_index += len(element_text) + 1
            plain_content += ' '.join(e['text'] for e in page_elements)
            plain_content_index -= 1
        es.bulk(index=index_name, body=bulk_elements, refresh=True)

        extract_important_dates(index_name, plain_content)
        extract_budget(index_name, plain_content)
        extract_duration(index_name, plain_content)
        extract_funded_proposal_amount(index_name, plain_content)


def extract_important_dates(index_name, plain_content):
    timetable_results = es.search(index=index_name, body={"query": {"match": {"text": "timetable"}}})
    deadline_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "deadline"}}
    ], "should": [
        {"match_phrase": {"text": {"query": "deadline submission", "slop": 20}}},
        {"match_phrase_prefix": {"text": {"query": "deadline submit", "slop": 20}}}
    ]}}})
    evaluation_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "evaluation"}}
    ], "should": [
        {"match": {"text": "period"}}
    ]}}})
    signature_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "signature"}}
    ], "should": [
        {"match_phrase": {"text": {"query": "signature agreement", "slop": 20}}},
        {"match_phrase": {"text": {"query": "signature grant", "slop": 20}}}
    ]}}})
    applicant_information_results = es.search(index=index_name, body={"query": {"bool": {"should": [
        {"match": {"text": "information"}},
        {"match": {"text": "applicant"}}
    ]}}})
    publication_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "publication"}}
    ], "should": [
        {"match_phrase": {"text": {"query": "publication call", "slop": 20}}}
    ]}}})
    starting_date_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match_phrase_prefix": {"text": {"query": "date start", "slop": 10}}}
    ], "should": [
        {"match": {"text": "action"}}
    ]}}})
    date_matches = get_date_matches(plain_content)

    potential_deadlines = get_result_matches(deadline_results, date_matches, 250, index_name)
    potential_evaluation_dates = get_result_matches(evaluation_results, date_matches, 250, index_name)
    potential_signature_dates = get_result_matches(signature_results, date_matches, 250, index_name)
    potential_applicant_information_dates = get_result_matches(applicant_information_results, date_matches, 250, index_name)
    potential_publication_dates = get_result_matches(publication_results, date_matches, 250, index_name)
    potential_starting_dates = get_result_matches(starting_date_results, date_matches, 250, index_name)

    potential_deadlines.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)
    potential_evaluation_dates.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)
    potential_signature_dates.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)
    potential_applicant_information_dates.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)
    potential_publication_dates.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)
    potential_starting_dates.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)

    print()
    print("Deadline")
    for pot in potential_deadlines:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    print()
    print("Evaluation")
    for pot in potential_evaluation_dates:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    print()
    print("Signature")
    for pot in potential_signature_dates:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    print()
    print("Applicant Information")
    for pot in potential_applicant_information_dates:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    print()
    print("Publication")
    for pot in potential_publication_dates:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    print()
    print("Starting Date")
    for pot in potential_starting_dates:
        print(plain_content[pot["match"][0]:pot["match"][1]])

    return


def extract_budget(index_name, plain_content):
    total_budget_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "budget"}}
    ], "should": [
        {"match_phrase": {"text": {"query": "total budget", "slop": 10}}}
    ]}}})
    grant_amount_results = es.search(index=index_name, body={"query": {"bool": {"should": [
        {"match": {"text": "grant"}},
        {"match": {"text": "budget"}},
        {"match": {"text": "between"}}
    ]}}})
    money_matches = get_money_matches(plain_content)

    potential_total_budgets = get_result_matches(total_budget_results, money_matches, 250, index_name)
    potential_grant_amounts = get_result_matches(grant_amount_results, money_matches, 250, index_name)

    potential_total_budgets.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)
    potential_grant_amounts.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)

    print()
    print("Total Budget")
    for pot in potential_total_budgets:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    print()
    print("Grant Amount")
    for pot in potential_grant_amounts:
        print(plain_content[pot["match"][0]:pot["match"][1]])
    return


def extract_duration(index_name, plain_content):
    duration_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "duration"}}
    ], "should": [
        {"match_phrase": {"text": {"query": "project duration", "slop": 10}}}
    ]}}})
    duration_matches = get_duration_matches(plain_content)

    potential_durations = get_result_matches(duration_results, duration_matches, 250, index_name)

    potential_durations.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)

    print()
    print("Duration")
    for pot in potential_durations:
        print(plain_content[pot["match"][0]:pot["match"][1]])

    return


def extract_funded_proposal_amount(index_name, plain_content):
    funded_proposal_amount_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"prefix": {"text": "fund"}}
    ], "should": [
        {"match_phrase_prefix": {"text": {"query": "approximately fund", "slop": 10}}},
        {"regexp": {"text": "[1-9][0-9]*\s*to\s*[1-9][0-9]*\s*proposals"}},
        {"match_phrase": {"text": {"query": "single proposal", "slop": 5}}},
        {"match_phrase": {"text": {"query": "only one proposal", "slop": 5}}}
    ]}}})
    funded_proposal_amount_matches = get_funded_proposal_amount_matches(plain_content)

    potential_funded_proposal_amounts = get_result_matches(funded_proposal_amount_results, funded_proposal_amount_matches, 250, index_name)

    potential_funded_proposal_amounts.sort(key=lambda rm: get_result_match_weighting(rm), reverse=True)

    print()
    print("Funded Proposal Amount")
    for pot in potential_funded_proposal_amounts:
        print(plain_content[pot["match"][0]:pot["match"][1]])

    return


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
    verbose_date = "(((from|until)\s*)?(early(\sin)?|beginning\sof|end(\sof)?|mid(-|\sof))\s*({year}|{month}\s*{year}?))" \
        .format(month=month, year=year)

    final_regex = "{year_span}|{date_span}|{verbose_date}|{date}" \
        .format(date=date, year_span=year_span, date_span=date_span, verbose_date=verbose_date)

    return get_match_positions(final_regex, plain_content)


def get_money_matches(plain_content):
    plain_content = plain_content.lower()
    currency = "(eur|€|\$)"
    amount = "([1-9][0-9]{0,2}(.?[0-9]{3})+)"

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


def get_match_positions(regex, text):
    results = []
    for match in re.compile(regex, re.MULTILINE).finditer(text):
        start_position = match.start()
        end_position = match.end()
        if end_position - start_position <= 3:
            continue
        results.append((start_position, end_position))
    return results


def get_result_matches(search_results, match_positions, maximum_distance, index_name) -> list:
    if len(match_positions) == 0:
        return []
    result_matches = []
    for result in search_results["hits"]["hits"]:
        for date_match in match_positions:
            result_match_difference = get_result_match_distance(result, date_match, index_name)
            if result_match_difference <= maximum_distance:
                result_matches.append({"match": date_match, "score": result["_score"], "distance": result_match_difference})
    return result_matches


def get_result_match_distance(result, match, index_name) -> float:
    match_start = match[0]
    match_end = match[1]
    match_results = es.search(index=index_name, body={"query": {"bool": {"must_not": [
        {"bool":
            {"must":
                [
                    {"range":
                        {"text_start_index":
                            {
                                "lte": match_start
                            }
                        }
                    },
                    {"range":
                        {"text_end_index":
                            {
                                "lte": match_start
                            }
                        }
                    }
                ]
            }
        },
        {"bool":
            {"must":
                [
                    {"range":
                        {"text_start_index":
                            {
                                "gte": match_end
                            }
                        }
                    },
                    {"range":
                        {"text_end_index":
                            {
                                "gte": match_end
                            }
                        }
                    }
                ]
            }
        }
    ]}}})

    distance = min(get_distance(result, e, match) for e in match_results["hits"]["hits"])
    if distance == 0:
        distance = 0.1
    return distance


def get_distance(result1, result2, match):
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
        v_offset_score = v_offset * 10 * 50
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


def get_result_match_weighting(result_match):
    return result_match["score"] * result_match["score"] / result_match["distance"]


class SearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC1/VP-2016-001.pdf"
#path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC2/Call VS-2016-015 - EN.pdf"
#path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC3/VP 2016 018_ESC call text_final.pdf"
#path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC4/Call VS-2016-015 - EN.pdf"
#path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC5/Call VS-2016-015 - EN.pdf"
#path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC6/Call VS-2016-015 - EN.pdf"
results = []
file = open(path, "rb")
content = file.read()
size = os.path.getsize(path)
do_standard_extraction([MicroMock(id=1,content=content,size=size)])