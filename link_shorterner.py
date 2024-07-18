import requests

def shorter_link (url):
    api = 'https://ulvis.net/api.php?url=' + url
    r = requests.get(api)
    link = r.text
    return link

if __name__ == '__main__':
    url = str(input('masukkan link untuk disingkat: '))
    link = shorter_link(url)
    print(link)