#!/usr/bin/env python3

import argparse
import csv
import gzip
import json
import logging
import re
import socket
from io import BytesIO
from typing import List, Iterator
from urllib import request
from urllib.request import Request

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'utf-8,*;q=0.5',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 '
}

URL_QUERY = 'https://leetcode.com/graphql'

output_file_name = 'cards.txt'

lang = 'C++'

title_slugs = []

skipped = []


def urlopen_with_retry(req: Request, retry=5):
    for i in range(1, retry + 1):
        try:
            return request.urlopen(req)
        except Exception as e:
            if isinstance(e, socket.timeout):
                logging.warning('request attempt {} timeout'.format(i))
            else:
                logging.warning(e)
            if i == retry:
                raise e


def retrieve_content(req: Request):
    response = urlopen_with_retry(req)
    data = response.read()
    content_encoding = response.getheader('Content-Encoding')
    logging.debug('Content-Encoding: {}'.format(content_encoding))
    if content_encoding == 'gzip':
        data = gzip.GzipFile(fileobj=BytesIO(data)).read()
    charset = 'UTF-8'
    match = re.search(r'charset=([\w-]+)', response.getheader('Content-Type'))
    if match:
        charset = match.group(1)
    return data.decode(charset, 'ignore')


def get_content(url: str, headers: dict = None) -> str:
    if headers is None:
        headers = HEADERS
    logging.debug('url: {}, headers: {}'.format(url, headers))
    return retrieve_content(Request(url, headers=HEADERS))


def post_content(url: str, data: bytes = None, headers: dict = None) -> str:
    if headers is None:
        headers = HEADERS
    logging.debug('url: {}, data: {}, headers: {}'.format(url, data, headers))
    return retrieve_content(Request(url, data=data, headers=headers))


POST_DATA_QUESTION = {
    "operationName": "questionData",
    "variables": {"titleSlug": 'two-sum'},
    "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    boundTopicId\n    title\n    titleSlug\n    content\n    translatedTitle\n    translatedContent\n    isPaidOnly\n    difficulty\n    likes\n    dislikes\n    isLiked\n    similarQuestions\n    contributors {\n      username\n      profileUrl\n      avatarUrl\n      __typename\n    }\n    langToValidPlayground\n    topicTags {\n      name\n      slug\n      translatedName\n      __typename\n    }\n    companyTagStats\n    codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n    stats\n    hints\n    solution {\n      id\n      canSeeDetail\n      __typename\n    }\n    status\n    sampleTestCase\n    metaData\n    judgerAvailable\n    judgeType\n    mysqlSchemas\n    enableRunCode\n    enableTestMode\n    envInfo\n    libraryUrl\n    __typename\n  }\n}\n"
}


def get_question_data(title_slug: str) -> dict:
    logging.debug('getting question data: {}'.format(title_slug))
    headers = HEADERS
    headers['Content-Type'] = 'application/json'
    post_data = POST_DATA_QUESTION
    post_data['variables']['titleSlug'] = title_slug
    content = post_content(URL_QUERY, json.dumps(post_data).encode('utf-8'), headers)
    return json.loads(content)


# 1. ID
# 2. TitleSlug
# 3. Title
# 4. Content
# 5. Difficulty
# 6. CodeSnippet
# 7. Code
# 8. Tags
def generate_card(title_slug: str) -> List[str]:
    logging.debug('generating card: {}'.format(title_slug))
    question = get_question_data(title_slug)['data']['question']
    card = [
        question['questionFrontendId'],
        question['titleSlug'],
        question['title'],
        question['content'],
        question['difficulty'],
        next(
            s['code'] for s in question['codeSnippets'] if
            s['lang'].lower() == lang.lower() or s['langSlug'] == lang.lower()
        ),
        '',  # empty code by design
        ' '.join(t['slug'] for t in question['topicTags']),
    ]
    return card


POST_DATA_TAG = {
    "operationName": "getTopicTag",
    "variables": {"slug": "array"},
    "query": "query getTopicTag($slug: String!) {\n  topicTag(slug: $slug) {\n    name\n    translatedName\n    questions {\n      status\n      questionId\n      questionFrontendId\n      title\n      titleSlug\n      translatedTitle\n      stats\n      difficulty\n      isPaidOnly\n      topicTags {\n        name\n        translatedName\n        slug\n        __typename\n      }\n      companyTags {\n        name\n        translatedName\n        slug\n        __typename\n      }\n      __typename\n    }\n    frequencies\n    __typename\n  }\n  favoritesLists {\n    publicFavorites {\n      ...favoriteFields\n      __typename\n    }\n    privateFavorites {\n      ...favoriteFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment favoriteFields on FavoriteNode {\n  idHash\n  id\n  name\n  isPublicFavorite\n  viewCount\n  creator\n  isWatched\n  questions {\n    questionId\n    title\n    titleSlug\n    __typename\n  }\n  __typename\n}\n"
}


def get_title_slugs_by_tag(tag: str = None) -> List[str]:
    logging.debug('getting by tag: {}'.format(tag))
    headers = HEADERS
    headers['Content-Type'] = 'application/json'
    post_data = POST_DATA_TAG
    post_data['variables']['slug'] = tag
    content = post_content(URL_QUERY, json.dumps(post_data).encode('utf-8'), headers)
    questions = json.loads(content)['data']['topicTag']['questions']
    return [q['titleSlug'] for q in questions]


URL_PROBLEM_SET = 'https://leetcode.com/api/problems/favorite_lists/{}/'


def get_title_slugs_by_problem_set(problem_set: str = None) -> List[str]:
    logging.debug('getting by set: {}'.format(problem_set))
    headers = HEADERS
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    content = get_content(URL_PROBLEM_SET.format(problem_set), headers)
    questions = json.loads(content)['stat_status_pairs']
    # original data is reversed
    return [q['stat']['question__title_slug'] for q in questions][::-1]


URL_LIST = 'https://leetcode.com/list/api/get_list/{}/'


def get_title_slugs_by_list(_list: str = None) -> List[str]:
    logging.debug('getting by list: {}'.format(_list))
    headers = HEADERS
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    content = get_content(URL_LIST.format(_list), headers)
    questions = json.loads(content)['questions']
    return [q['title_slug'] for q in questions]


POST_DATA_PROBLEM_LIST = {
    "query": "\n    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      topicTags {\n        name\n        id\n        slug\n      }\n      hasSolution\n      hasVideoSolution\n    }\n  }\n}\n    ",
    "variables": {
        "categorySlug": "",
        "skip": 0,
        "limit": 1000000,  # LeetCode is unhappy if too large
        "filters": {
            "listId": "93afdecd8402495fa94c8fb4b98be8fd"
        }
    }
}


def get_title_slugs_by_problem_list(pl: str = None) -> List[str]:
    logging.debug('getting by problem list: {}'.format(pl))
    headers = HEADERS
    headers['Content-Type'] = 'application/json'
    post_data = POST_DATA_PROBLEM_LIST
    post_data['variables']['filters']['listId'] = pl
    content = post_content(URL_QUERY, json.dumps(post_data).encode('utf-8'), headers)
    questions = json.loads(content)['data']['problemsetQuestionList']['questions']
    return [q['titleSlug'] for q in questions]


def match_group1(pattern: str, string) -> str:
    m = re.match(pattern, string)
    if m:
        return m.group(1)


def get_title_slugs_by_url(url: str = None) -> List[str]:
    logging.debug('handling url: {}'.format(url))
    tag = match_group1(r'^https?://leetcode.com/tag/([^\s/]+)\S*$', url)
    if tag:
        return get_title_slugs_by_tag(tag)
    _set = match_group1(r'^https?://leetcode.com/problemset/([^\s/]+)\S*$', url)
    if _set:
        return get_title_slugs_by_problem_set(_set)
    _list = match_group1(r'https?://leetcode.com/list/([^\s/]+)\S*$', url)
    if _list:
        return get_title_slugs_by_list(_list)
    _pl = match_group1(r'https?://leetcode.com/problem-list/([^\s/]+)\S*$', url)
    if _pl:
        return get_title_slugs_by_problem_list(_pl)
    logging.error('unknown url: {}'.format(url))


ALL_LIST = None

URL_ALL = 'https://leetcode.com/api/problems/all/'


def get_all_list() -> List[str]:
    logging.debug('getting all list')
    headers = HEADERS
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    content = get_content(URL_ALL, headers)
    all_data = json.loads(content)
    all_list = [''] * (int(all_data['num_total']) + 1)
    for question in all_data['stat_status_pairs']:
        all_list[int(question['stat']['frontend_question_id'])] = question['stat']['question__title_slug']
    return all_list


def get_title_slug_by_id(_id: int) -> str:
    global ALL_LIST
    if not ALL_LIST:
        ALL_LIST = get_all_list()
    return ALL_LIST[_id]


def parse_args():
    parser = argparse.ArgumentParser(
        prog='lc2anki',
        usage='lc2anki [OPTION]...',
        description='lc2anki is a tool generating Anki cards for LeetCode.',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='show this help message and exit'
    )
    parser.add_argument(
        '-l', '--lang', metavar='LANG',
        help='specify language, for example: C, C++, Java'
    )
    parser.add_argument(
        '-o', '--output-file', metavar='FILE',
        help='set output file'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='show debug info'
    )

    question_group = parser.add_argument_group('question options')
    question_group.add_argument(
        '-u', '--url', metavar='URL',
        help='generate cards from link, for example: {}'.format(', '.join([
            'https://leetcode.com/tag/array/',
            'https://leetcode.com/problemset/top-100-liked-questions/',
            'https://leetcode.com/list/foobar/',
            'https://leetcode.com/problem-list/93afdecd8402495fa94c8fb4b98be8fd'
        ]))
    )
    question_group.add_argument(
        '-q', '--question', metavar='QUESTION', nargs='*',
        help='specify question id or title slug, for example: 1, two-sum, 1-100'
    )
    question_group.add_argument(
        '-i', '--input-file', metavar='FILE', type=argparse.FileType('r'),
        help='specify question ids or titles from FILE split by lines'
    )

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        exit()

    logging.getLogger().setLevel(logging.DEBUG if args.debug else logging.INFO)

    global lang
    if args.lang:
        lang = args.lang.lower()
    else:
        logging.info('no language specified, using default: {}'.format(lang))

    global output_file_name
    if args.output_file:
        output_file_name = args.output_file

    global title_slugs

    if args.url:
        title_slugs.extend(get_title_slugs_by_url(args.url))

    def get_title_slugs(questions: List[str]) -> Iterator[str]:
        for q in questions:
            if q.isnumeric():
                yield get_title_slug_by_id(int(q))
            elif re.match(r'^(\d+)-(\d+)$', q):
                r = q.split('-')
                for i in range(int(r[0]), int(r[1]) + 1):
                    yield get_title_slug_by_id(i)
            else:
                yield '-'.join(q.lower().split())

    if args.question:
        title_slugs.extend(get_title_slugs(args.question))
    if args.input_file:
        title_slugs.extend(get_title_slugs(args.input_file.read().splitlines()))
        args.input_file.close()

    if not title_slugs:
        logging.error('no question specified')
        parser.print_help()
        exit(2)
    logging.debug('title slugs: {}'.format(title_slugs))


def main():
    socket.setdefaulttimeout(20)

    with open(output_file_name, 'a', encoding='utf8') as fp:
        writer = csv.writer(fp)
        visited = set()
        for title_slug in title_slugs:
            if title_slug in visited:
                logging.info('skipping duplicate: {}'.format(title_slug))
                continue
            try:
                card = generate_card(title_slug)
                writer.writerow(card)
            except Exception as e:
                logging.error('error happened when generating card: {}'.format(title_slug))
                logging.error(e)
                if isinstance(e, TypeError):
                    logging.error('is this premium only?')
                skipped.append(title_slug)
            else:
                visited.add(title_slug)
                logging.info('generated card: {}'.format(title_slug))

    logging.info('saved {} cards to: {}'.format(len(visited), output_file_name))
    if skipped:
        logging.error('skipped {} questions: {}'.format(len(skipped), skipped))


if __name__ == '__main__':
    parse_args()
    main()
