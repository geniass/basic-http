from html.parser import HTMLParser


class ResourceHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.resources_to_download = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            src = [attr[1] for attr in attrs if attr[0] == 'src']
            self.resources_to_download.extend(src)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        pass

    def extract_resource_urls(self, html):
        self.feed(html)
        return self.resources_to_download
