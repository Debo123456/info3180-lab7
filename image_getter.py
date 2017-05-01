import requests
from bs4 import BeautifulSoup
import urlparse

def getUrls(url):
    
    url = url
    result = requests.get(url)
    images = []
    soup = BeautifulSoup(result.text, "html.parser")

    # This will look for a meta tag with the og:image property
    og_image = (soup.find('meta', property='og:image') or
                    soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        images.append(og_image['content'])
        
    
    # This will look for a link tag with a rel attribute set to 'image_src'
    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        images.append(thumbnail_spec['href'])
    
    
    #image = """<img src="%s"><br />"""
    for img in soup.findAll("img", src=True):
        images.append( urlparse.urljoin(url, img["src"]) )
    return images
    
