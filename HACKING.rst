Searchlight Style Commandments
==============================

- Step 1: Read the OpenStack Style Commandments
  http://docs.openstack.org/developer/hacking/
- Step 2: Read on

Searchlight Specific Commandments
---------------------------------

- [SL316] Change assertTrue(isinstance(A, B)) by optimal assert like
  assertIsInstance(A, B)
- [SL317] Change assertEqual(type(A), B) by optimal assert like
  assertIsInstance(A, B)
- [SL318] Change assertEqual(A, None) or assertEqual(None, A) by optimal assert like
  assertIsNone(A)
- [SL319] Validate that debug level logs are not translated
- [SL320] For python 3 compatibility, use six.text_type() instead of unicode()
- [SL321] Validate that LOG messages, except debug ones, have translations
- [SL327] Prevent use of deprecated contextlib.nested
- [SL343] Check for common double word typos