import re


def get_content(soup_link, content_class, content_length=75):
    for script in soup_link.find_all(['script', 'a', 'figure', 'header']):
        script.extract()

    content = soup_link.find(class_=content_class).get_text().strip()
    content = re.sub('\n+', '\n', content)  # Remove multiple line breaks
    content = re.sub(' +', ' ', content)  # Remove multiple spaces
    if len(content) <= content_length:
        content = ' '.join(content)
    else:
        content = ' '.join(content.split(' ')[:content_length]) + '...'
    return content
