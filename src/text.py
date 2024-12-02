"""
Does formatting stuff, mainly markdown to plain text.
"""

import re
import markdown
import bs4


class Formatter:
    """
    Formats text.
    """

    def __init__(self, text: str = None):
        """
        Sets up the formatter. Needs text to do anything useful.
        """
        assert text is not None, "formatter - text must be provided in order to format"

        self.text = text

    def __to_text__(self) -> str:
        """
        Strips markdown down to plain text. Deals with code, links, headers, etc.
        Not perfect, but gets the job done.
        """
        assert self.text is not None, "formatter - text must be provided in order to format"

        md = markdown.markdown(self.text)

        md = re.sub(r"<pre><code>.*?</code></pre>", " ", md, flags=re.DOTALL)
        md = re.sub(r"<code>.*?</code>", " ", md, flags=re.DOTALL)

        md = re.sub(r"<a [^>]+>(.*?)</a>", r"\1", md)

        md = re.sub(r"!\[.*?\]\((.*?)\)", " ", md)
        md = re.sub(r"<img [^>]+alt=['\"](.*?)['\"][^>]*>", r"\1", md)

        soup = bs4.BeautifulSoup(md, "html.parser")
        self.text = soup.get_text(separator=" ", strip=True)

        self.text = re.sub(r"\s+", " ", self.text).strip()

        return self.text

    def format(self) -> str:
        """
        Takes input text, does formatting magic, and gives you back clean text.
        Strips markdown, HTML, and other fluff.
        """
        return self.__to_text__()
