import unittest

from lc2anki import *

logging.getLogger().setLevel(logging.DEBUG)


class TestLeetCodeAPI(unittest.TestCase):
    def test_get_question_data(self):
        logging.debug(get_question_data('two-sum'))

    def test_generate_card(self):
        logging.debug(generate_card('two-sum'))

    def test_get_title_slugs_by_tag(self):
        logging.debug(get_title_slugs_by_tag('array'))

    def test_get_title_slugs_by_problem_set(self):
        logging.debug(get_title_slugs_by_problem_set('top-100-liked-questions'))

    def test_get_title_slugs_by_list(self):
        logging.debug(get_title_slugs_by_list('g71kzvs'))

    def test_get_title_slugs_by_problem_list(self):
        logging.debug(get_title_slugs_by_problem_list('93afdecd8402495fa94c8fb4b98be8fd'))

    def test_get_titles_by_url(self):
        tag_url = 'https://leetcode.com/tag/array/'
        set_url = 'https://leetcode.com/problemset/top-100-liked-questions/'
        list_url = 'https://leetcode.com/list/g71kzvs/'
        problem_list_url = 'https://leetcode.com/problem-list/93afdecd8402495fa94c8fb4b98be8fd/'
        logging.debug(get_title_slugs_by_url(tag_url))
        logging.debug(get_title_slugs_by_url(set_url))
        logging.debug(get_title_slugs_by_url(list_url))
        logging.debug(get_title_slugs_by_url(problem_list_url))

    def test_get_all_list(self):
        all_list = get_all_list()
        logging.debug(all_list)
        self.assertEqual('maximum-equal-frequency', all_list[1224])


if __name__ == '__main__':
    unittest.main()
