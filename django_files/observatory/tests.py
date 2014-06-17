from django.utils.unittest import TestCase

from observatory.views_search import make_extractor, remove_spans


class TestRemoveSpans(TestCase):

    def test_one_span(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals("I am a string! Hahaaa! Narwhals!",
                          remove_spans(s, [(6, 11)]))

    def test_two_spans(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals("I am a string! Narwhals!",
                          remove_spans(s, [(6, 11), (19, 27)]))

    def test_empty_span(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals(s, remove_spans(s, []))

    def test_consecutive_span(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals("I am a test string!",
                          remove_spans(s, [(19, 27), (27, 37)]))

    def test_one_gap_span(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals("I am a test string!!",
                          remove_spans(s, [(19, 26), (27, 37)]))

    def test_beginning_span(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals("a test string! Hahaaa! Narwhals!",
                          remove_spans(s, [(0, 5)]))

    def test_end_span(self):
        s = "I am a test string! Hahaaa! Narwhals!"
        self.assertEquals("I am a test string! Hahaaa!",
                          remove_spans(s, [(27, 37)]))


class SearchExtractorTest(TestCase):

    def test_one_match_one_group(self):
        string = "I have a cat."
        extractor = make_extractor(r"(cat)")
        result, processed_string = extractor(string)
        self.assertEqual(processed_string, "I have a .")
        self.assertEqual(result, [(("cat",), ((9, 12),))])

    def test_two_match_one_group(self):
        string = "I have a cat and another cat."

        extractor = make_extractor(r"(cat|dog)")
        result, processed_string = extractor(string)
        self.assertEqual(processed_string, "I have a  and another .")
        self.assertEqual(result, [(("cat", ), ((9, 12),)),
                                  (("cat", ), ((25, 28),))])

    def test_one_match_two_group(self):
        string = "I have a cat and another dog."

        extractor = make_extractor(r"(cat).*?(dog)")
        result, processed_string = extractor(string)
        self.assertEqual(processed_string, "I have a .")
        self.assertEqual(result, [(("cat", "dog"), ((9, 28),))])

        extractor2 = make_extractor(r"(cat).*?(dog)", remove_only_matches=True)
        result, processed_string = extractor2(string)
        self.assertEqual(processed_string, "I have a  and another .")
        self.assertEqual(result, [(("cat", "dog"), ((9, 12), (25, 28)))])

        #TODO: maybe match output and spans together?
