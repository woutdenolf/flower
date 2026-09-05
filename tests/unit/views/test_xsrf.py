import os

from tests.unit import AsyncHTTPTestCase


class XsrfProtectionTests(AsyncHTTPTestCase):
    def test_cookie_session_post_without_token_is_blocked(self):
        # OAuth (cookie) mode: a state-changing POST without an XSRF token is
        # rejected before it reaches the handler.
        with self.mock_option('auth', '.*@example.com'):
            r = self.post('/api/worker/shutdown/test', body={})
            self.assertEqual(403, r.code)
            self.assertIn(b'_xsrf', r.body)

    def test_header_auth_post_is_exempt(self):
        # A request carrying an Authorization header cannot be forged
        # cross-origin, so it needs no token: it reaches auth and fails there
        # (401), never at the XSRF check (403).
        with self.mock_option('basic_auth', ['user:pass']):
            r = self.post('/api/worker/shutdown/test', body={},
                          auth_username='user', auth_password='wrong')
            self.assertEqual(401, r.code)
            self.assertNotIn(b'_xsrf', r.body)

    def test_unauthenticated_server_needs_no_token(self):
        # No auth configured: nothing to protect, scripts keep working.
        os.environ['FLOWER_UNAUTHENTICATED_API'] = 'true'
        try:
            r = self.post('/api/worker/shutdown/test', body={})
            self.assertNotEqual(403, r.code)
        finally:
            del os.environ['FLOWER_UNAUTHENTICATED_API']

    def test_full_page_load_sets_xsrf_cookie(self):
        # The UI relies on the _xsrf cookie being present so its AJAX calls can
        # echo the token back.
        with self.mock_option('basic_auth', ['user:pass']):
            r = self.fetch('/', auth_username='user', auth_password='pass')
            self.assertEqual(200, r.code)
            self.assertIn('_xsrf', r.headers.get('Set-Cookie', ''))
