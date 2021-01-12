import requests


class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_content(self, relative_url):
        url = self.base_url + relative_url
        resp = requests.get(url, timeout=10, allow_redirects=True)

        if not resp.ok:
            self._raise_error(resp.status_code, resp.text)
        return resp.content

    @staticmethod
    def _raise_error(error_code, message):
        raise ArkDataError(message)


class ArkDataError(RuntimeError):
    pass