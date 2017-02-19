from elasticsearch import Elasticsearch
from elasticsearch.compat import *
from elasticsearch.connection import *
from elasticsearch.helpers import *

from hetaddon.pdfparser import PdfParser
import os
import re


es = Elasticsearch()


def test():
    index_name = "test-index2"
    res = es.index(index=index_name, doc_type='document', id=1, body="")
    print(res['created'])

    es.indices.refresh(index=index_name)

    index = es.indices
    termInfo = index.get('employ')
    for pos in termInfo:
        print(pos.startOffset)

    res = es.search(index="test-index", body={"query": {"match": {"text":"Employment"}}})
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
        for page_index, page in enumerate(pages):
            page_elements = []
            for element in page:
                if hasattr(element, "get_text"):
                    element_text = element.get_text().lower()
                else:
                    element_text = ""
                page_element = {"text": element_text, "x":element.x0, "y": element.y0, "width": element.width,
                                "height": element.height, "page_number": page_index}
                page_elements.append(page_element)
            page_elements.sort(key=lambda e: e['x'])
            page_elements.sort(key=lambda e: e['y'], reverse=True)
            for element in page_elements:
                element_text = element["text"]
                element["plain_content_index"] = plain_content_index
                element["length"]: len(element_text)
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


def extract_important_dates(index_name, plain_content):
    timetable_results = es.search(index=index_name, body={"query": {"match": {"text": "timetable"}}})
    deadline_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "deadline"}}
    ], "should": [
        {"match": {"text": "submission"}},
        {"prefix": {"text": "submit"}}
    ]}}})
    evaluation_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "evaluation"}}
    ], "should": [
        {"match": {"text": "period"}}
    ]}}})
    signature_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "signature"}}
    ], "should": [
        {"match": {"text": "agreement"}},
        {"match": {"text": "grant"}}
    ]}}})
    applicant_information_results = es.search(index=index_name, body={"query": {"bool": {"should":[
        {"match": {"text": "information"}},
        {"match": {"text": "applicant"}}
    ]}}})
    publication_results = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "publication"}}
    ], "should": [
        {"match": {"text": "call"}}
    ]}}})
    date_matches = get_date_matches(plain_content)

    return


def extract_budget(index_name, plain_content):
    total_budget_matches = es.search(index=index_name, body={"query": {"bool": {"must": [
        {"match": {"text": "total budget"}}
    ]}}})
    grant_amount_matches = es.search(index=index_name, body={"query": {"bool": {"should": [
        {"match": {"text": "grant"}},
        {"match": {"text": "budget"}},
        {"match": {"text": "between"}}
    ]}}})
    money_matches = get_money_matches(plain_content)
    return


def get_date_matches(plain_content):
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
    currency = "(eur|€|\$)"
    amount = "([1-9][0-9]{0,2}(.?[0-9]{3})+)"

    regex_1 = "({currency}\s*{amount})".format(currency=currency, amount=amount)
    regex_2 = "({amount}\s*{currency})".format(currency=currency, amount=amount)

    final_regex = "{regex_1}|{regex_2}".format(regex_1=regex_1, regex_2=regex_2)

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


class SearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

path = "C:/Users/User/Google Drive/Planspiel_WebEngineering/Research/C4P/EC1/VP-2016-001.pdf"
file = open(path, "rb")
content = file.read()
size = os.path.getsize(path)
do_standard_extraction([MicroMock(id=1,content=content,size=size)])