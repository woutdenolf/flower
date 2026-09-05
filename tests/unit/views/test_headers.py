from tests.unit import AsyncHTTPTestCase


class SecurityHeaderTests(AsyncHTTPTestCase):
    def test_nosniff_on_page(self):
        r = self.get('/')
        self.assertEqual('nosniff', r.headers.get('X-Content-Type-Options'))

    def test_nosniff_on_api_error(self):
        # send_error clears the headers, so it has to be re-applied there
        with self.mock_option('basic_auth', ['user:pass']):
            r = self.post('/api/worker/shutdown/test', body={},
                          auth_username='user', auth_password='pass')
            self.assertEqual(404, r.code)
            self.assertEqual('nosniff', r.headers.get('X-Content-Type-Options'))
