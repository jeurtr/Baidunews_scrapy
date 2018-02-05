from scrapy.exceptions import IgnoreRequest

HTTP_BAD_STATUS = [403]


class ProcessErrorDownloadingMiddleware(object):

    def process_response(self, request, response, spider):
        """handle error downloading"""
        if response.status != 200:
            print("ignore this error request: " + response.url)
            raise IgnoreRequest(response.url)
        else:
            return response

    def process_exception(self, request, exception, spider):
        return None
