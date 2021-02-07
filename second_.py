from concurrent.futures import as_completed
from pprint import pprint
from requests_futures.sessions import FuturesSession


def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr=[]

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values=extract(obj, arr, key)
    return values


from bs4 import BeautifulSoup


def Concurrent_Request(endpoint,
                       key,
                       request):
    session=FuturesSession()

    result=[]

    for i, item in enumerate(request):
        for g, base in enumerate(endpoint):
            print(base)
            resp=session.get(str(base)+str(item)).result()
            parsed=resp.json()

            print(json_extract(parsed, key[g]))

            if json_extract(parsed, key[g]) != [None] and json_extract(parsed, key[g]) != [] and json_extract(parsed,
                                                                                                              key[
                                                                                                                  g]) != None:
                for i in json_extract(parsed, key[g]):
                    result.append(BeautifulSoup(i, features="html.parser").get_text())
                break
            print(g)
            if g+1 == len(endpoint):
                result.append('')

    return result


def Abstract_Collector(doi_list):
    endpoint=['https://api.semanticscholar.org/v1/paper/',
              'https://api.crossref.org/v1/works/',
              'https://doaj.org/api/v2/search/articles/doi%3A',
              # 'https://api.test.datacite.org/dois/'
              ]

    key=['abstract',
         'abstract',
         'abstract',
         ]

    return Concurrent_Request(endpoint, key, doi_list)


# print(Abstract_Collector(['10.1093/CJE/BEY045',
#       '10.2307/2224288',
#       '10.1111/j.1467-999X.2011.04144.x',
#       '10.2307/2225182',
#       '10.1093/OXFORDJOURNALS.CJE.A035141']
# ))

from tqdm import tqdm


#

def Limited_Concurrent_Requests(
        root,
        suffix,
        root_rate_limit_dict,  # in format [number of calls] : [period, in seconds]

):
    limit=root_rate_limit_dict.keys()
    period=root_rate_limit_dict.values()

    for i, root in enumerate(root):

        @sleep_and_retry
        @limits(calls=limit[i], period=period[i])
        def Concurrent_Call(root, suffix, search_term='abstract'):

            suffix=[x for x in suffix if x is not None]
            suffix_2=[]

            session=FuturesSession()

            futures=[]

            result={}

            found=0
            for index, i in enumerate(suffix):
                print(i)
                future=session.get(str(root)+str(i))
                future.i=i
                futures.append(future)

            for future in as_completed(futures):
                print(future.i)
                resp=future.result()
                if resp.status_code == 200:
                    parsed=resp.json()
                    if json_extract(parsed, search_term) in [[None], [], None]:
                        print('test')
                        suffix_2.append(future.i)
                    else:
                        found+=1
                        for i in json_extract(parsed, search_term):
                            result[future.i]=(BeautifulSoup(i, features="html.parser").get_text())

            return result, suffix_2, found

        result=Concurrent_Call(root, suffix)

    result.append(Concurrent_Call(root, result[1])[0])

    return


def Concurrent_Abstract_Request(
        suffix,
):
    suffix_2=[]

    suffix=[x for x in suffix if x is not None]

    session=FuturesSession()

    futures=[]

    result={}

    found_cr=0
    found_doaj=0

    for index, i in enumerate(suffix):
        print(i)
        future=session.get('https://api.crossref.org/v1/works/'+str(i))
        future.i=i
        futures.append(future)

    for future in as_completed(futures):
        print(future.i)
        resp=future.result()
        if resp.status_code == 200:
            parsed=resp.json()
            if json_extract(parsed, 'abstract') in [[None], [], None]:
                print('test')
                suffix_2.append(future.i)
            else:
                found_cr+=1
                for i in json_extract(parsed, 'abstract'):
                    result[future.i]=(BeautifulSoup(i, features="html.parser").get_text())

    suffix_2=[x for x in suffix_2 if x is not None]
    print(suffix_2)
    futures_2=[]

    for index, i in enumerate(suffix_2):
        print('yoyoyo')
        print(i)
        future_2=session.get('https://doaj.org/api/v2/search/articles/doi%3A'+str(i))
        future_2.i=i
        futures_2.append(future_2)

    for future_2 in as_completed(futures_2):
        print('hello?!?!')
        print(future_2.i)
        resp=future_2.result()
        print(resp)
        if resp.status_code == 200:
            parsed=resp.json()
            print(json_extract(parsed, 'abstract'))
            if json_extract(parsed, 'abstract') in [[None], [], None]:
                print('Not found')
            else:
                found_doaj+=1
                print('found')
                for i in json_extract(parsed, 'abstract'):
                    result[future_2.i]=(BeautifulSoup(i, features="html.parser").get_text())

    print(found_cr)
    print(found_doaj)

    return result


#

from ratelimit import limits, sleep_and_retry
import requests


@sleep_and_retry
@limits(calls=10, period=1)
def api_call(i):
    try:
        response=requests.get("https://jsonplaceholder.typicode.com/posts", timeout=1)
    except Exception as e:
        response=e
    return response


print(Concurrent_Abstract_Request(
    ['10.1111/j.1467-999X.2011.04144.x', '10.1093/OXFORDJOURNALS.CJE.A035141', '10.1111/J.1467-999X.2006.00250.X',
     '10.1080/05775132.2016.1272966', '10.2753/PKE0160-3477340304', '10.1093/CJE/BEU040',
     '10.1093/OXFORDJOURNALS.CJE.A035533', '10.2307/1884513', '10.2307/2974425', '10.1257/AER.P20151060',
     '10.2307/2278703', '10.2139/ssrn.3333410', '10.36687/inetwp108', '10.2139/ssrn.3590339', '10.1111/meca.12285',
     '10.1017/9781108854443', None, '10.1080/09538259.2020.1837546', '10.1111/meca.12277', '10.1007/S00191-020-00680-W',
     None, None]
    ))