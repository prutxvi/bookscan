import requests

urls = [
    'https://www.goodreads.com/book/show/40121378-atomic-habits?mobile=1',
    'https://goodreads.com/book/show/40121378-atomic-habits?mobile=1',
    'https://www.goodreads.com/book/reviews/40121378-atomic-habits'
]
for u in urls:
    try:
        r = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        print('\nURL:', u)
        print('Status:', r.status_code)
        txt = r.text
        print('Len:', len(txt))
        print(txt[:2000])
    except Exception as e:
        print('Error fetching', u, e)
