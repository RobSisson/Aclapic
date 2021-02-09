import asyncio
from aiohttp import ClientSession, ClientConnectorError
import time


def Compile_Endpoint_List(
        endpoints,
        apis_to_call,

):

    endpoint = []

    for i, e in enumerate(endpoints):

        apis_to_call_temp = []
        for i, api in enumerate(apis_to_call[i]):
            apis_to_call_temp.append([0, api])

        array = [e,apis_to_call_temp,None]
        endpoint.append(array)

    return endpoint

def Compile_Kwargs_list(
        keys,
        values,
        positions
):
    kwargs = []

    if type(keys) != list:
        keys=[keys]

    if type(values) != list:
        values=[values]

    if type(positions) != list:
        positions=[positions]

    for i, item in enumerate(keys):

        array = [[keys[i],values[i]], positions[i]]
        kwargs.append(array)

    return kwargs

def Kwargs_list_dict(
        kwargs
):
    result = {}
    for i, item in enumerate(kwargs):
        result_id = item[1]

        for i, kwarg in enumerate(item):
            result[result_id] = (str(item[0][i-1])+str(item[0][i]))

    return result

def Kwargs_to_dict(
        keys,
        values,
        positions
):
    return Kwargs_list_dict(Compile_Kwargs_list(keys, values, positions))


def Compile_Api_List(   # Create usable API list out of input info
        apis, # base api (always first in url generation)
        filters, # the api response will be filtered for these keys, add in format  [[apikey1, apikey2],api2key1,...]
        limits, # add in format [api 1 limit, api 2 limit,... api n limit]
        periods, # add in format [api 1 period, api 2 period,... api n period]
        keys = None, # add in format [[api 1 key 1, ... api 1 key n], ... [api n key 1, ... api 1 key n]] add None for no keys
        values = None, # same format as keys
        positions = None #  same format as keys
):

    api = []
    kwargs = []

    if None not in [keys, values, positions] and (len(keys) == len(values) == len(positions)): # convert raw lists to the format [{position: key+value, ...}, {position: key+value, ...}, ... ]
        for i, item in enumerate(keys):
            # print(item)
            if item != None:
                kwargs.append(Kwargs_to_dict(keys[i], values[i], positions[i]))
            else:
                kwargs.append(None)


    for i, end in enumerate(apis):
        array = [apis[i],filters[i],limits[i],periods[i], kwargs[i], 0, 0]
        api.append(array)

    return api


def Create_URL(
        api,
        endpoint,
        # **kwargs,
):
    url = [api[0]]

    if api[4] != None: # api[4] is the column containing additional {positions:key+value,} including auth keys
        kwargs = api[4]

        for i in range(len(kwargs)+1): # for number of additional values + 1 (since the total string will include the key+values and the endpoint
            try:
                url.append(kwargs[i]) # append key+value that holds position i

            except:
                url.append(endpoint) # if not present, append endpoint

        url = ''.join(url) # list -> string
    else:
        url=str(api[0])+str(endpoint)

    return url

# def Create_Next_URLs(
#         api_list,
#         endpoint_list,
# ):
#     url_list = []
#
#
#     for i, endpoint in enumerate(endpoint_list):
#
#         # print(endpoint[2])
#         # print('endpoint above')
#         if endpoint[2] == None: # would it be faster to remove the called endpoints from this list?
#             done_count = 0
#             for i, api_to_call in enumerate(endpoint[1]):
#
#                 if api_to_call[0] == 0:
#                     api_number = api_to_call[1] # this would be the number of the api to call, not the api itself
#
#
#
#                     url_list.append(Create_URL(api_list[api_number], endpoint[0]))
#
#                     api_to_call[1] = 1
#                     break
#
#                 elif api_to_call[1] == 1:
#                     done_count += 1
#
#                 if len(endpoint[1]) <= done_count:
#                     print("All Api's for " + str(endpoint[0] + ' searched, and no result found'))
#
#     return url_list

async def check_api(api_list, api_number) -> bool:

    api_to_check = api_list[api_number]

    limit = api_to_check[2]
    period = api_to_check[3]

    # count = api_to_check[5]
    # timer = api_to_check[6]

    if api_to_check[6] == 0: # check is timer has been started, if not, start it
        api_to_check[6] = time.time() # start timer
        api_to_check[5] += 1 # add one to count
        return True

    else:
        elapsed=time.time()-api_to_check[6] # calculate elapsed time
        if (elapsed < period) & (api_to_check[5] < limit-1): # if timer is below period and count is below limit-1
            api_to_check[5] += 1 # add one to count
            return True

        elif (elapsed < period) & (api_to_check[5] >= limit-1): # if timer is below period and count is above limit-1
            return False

        elif elapsed >= period: # if timer is beyond period for that api, reset the timer and the count, then return true
            api_to_check[6] = time.time() # start timer
            api_to_check[5]  = 0 # reset count
            return True

async def Create_Next_URLs(
        api_list,
        endpoint_list,
):

    url_list=[]
    print(endpoint_list)
    for i, endpoint in enumerate(endpoint_list):
        for i, api_to_call in enumerate(endpoint[1]):

            check = await check_api(api_list, api_to_call[1])


            if (api_to_call[0]) == 0 and check == True:
                api_number=api_to_call[1]  # this would be the number of the api to call, not the api itself

                url_list.append(Create_URL(api_list[api_number], endpoint[0])) # append created url to list

                # endpoint[1].remove(api_to_call) # once url is appended, remove the relevant api_to_call from the endpoint

                # api_to_call[1] = 1 # alt version of checking if an endpoint has been called
                break #


            # if len(endpoint[1]) == 0:
            #     print("All Api's for "+str(endpoint[0]+' searched, and no result found'))
            #     endpoint_list.remove(endpoint)

    return url_list


async def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr=[]

    async def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    await extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                await extract(item, arr, key)
        return arr

    values= await extract(obj, arr, key)
    return values




async def fetch_html(url: str, session: ClientSession, id, **kwargs) -> list:
    try:
        resp = await session.request(method="GET", url=url, **kwargs)
        resp_json = await resp.json()

        result=await json_extract(resp_json, 'abstract')

        test_abstract_presence = result[0] # will cause an exception if no search key is found and fail out to the 2nd except statement

    except ClientConnectorError:
        return [id, url, 404]
    except:
        return [id, url, None]

    return [id, url, result[0]]







async def make_requests(urls: list, **kwargs):

    async with ClientSession() as session:
        tasks = []
        for i, url in enumerate(urls):
            tasks.append(
                fetch_html(url=url, session=session, id=i, **kwargs)
            )
        responses = await asyncio.gather(*tasks)

    return responses

if __name__ == "__main__":
    import pathlib
    import sys

    if sys.version_info[0] == 3 and sys.version_info[1]>=8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent


async def DOI_List_to_Result(
        endpoint_list,
        apis_to_call = None, # add info in format: [[0, 1], [2], [0, 1, 2]...] Using the value of the API, leave blank for all
):


    apis=['https://api.semanticscholar.org/v1/paper/',
          'https://api.crossref.org/v1/works/',
          #'https://doaj.org/api/v2/search/articles/doi%3A'
          ]
    filters=[['abstract'],
             ['abstract'],
             #['abstract']
             ]
    limits=[100, 50]
    period=[300, 100]
    keys=[None, None]
    values=[None, None]
    positions=[None, None]

    api_list = Compile_Api_List(apis=apis,
                                filters=filters,
                                limits=limits,
                                periods=period,
                                keys=keys,
                                values=values,
                                positions=positions)

    
    if apis_to_call == None:
        apis_to_call = []
        api_values = []

        for i, api in enumerate(apis):
            api_values.append(i)

        for i, item in enumerate(endpoint_list):
            apis_to_call.append(api_values)

    endpoint_list = Compile_Endpoint_List(endpoints=endpoint_list,
                                          apis_to_call=apis_to_call)

    result = []

    loop = 0

    while len(endpoint_list) > len(result):
        loop +=1
        print(len(endpoint_list) - len(result))
        url_list = await Create_Next_URLs(api_list, endpoint_list)

        response = await asyncio.gather(make_requests(urls=url_list))

        for i, item in enumerate(response[0]):
            print('below')
            print(item)

            print(item[0])

            if item[2] not in [[], None, '']:
                print('gogogo')
                result.append(item)
                for i, api_to_call in enumerate(endpoint_list[item[0]][1]):
                    api_to_call[0]= 1
            else:
                for i, api_to_call in enumerate(endpoint_list[item[0]][1]):
                    if i < loop:
                        api_to_call[0]= 1
                    else:
                        break
    
    return result

dois = ['10.1093/CJE/BEY045',
        '10.2307/2224288',
        '10.1111/j.1467-999X.2011.04144.x',
        '10.2307/2225182',
        '10.1093/OXFORDJOURNALS.CJE.A035141',
        '10.1111/J.1467-999X.2006.00250.X',
        '10.1080/05775132.2016.1272966',
        '10.2753/PKE0160-3477340304',
        '10.1093/CJE/BEU040',
        '10.1111/J.1475-4932.1956.TB00434.X',
        '10.1093/OXFORDJOURNALS.CJE.A035533',
        '10.2307/1884513',
        '10.2307/2974425',
        '10.2307/2227704',
        '10.1257/AER.P20151060',
        '10.2307/2278703',
        '10.1017/9781108854443.005',
        '10.2139/ssrn.3333410',
        '10.36687/inetwp108',
        '10.2139/ssrn.3590339',
        '10.1111/meca.12285',
        '10.1017/9781108854443',
        '10.1017/9781108854443.007',
        '10.1080/09538259.2020.1837546',
        '10.1111/meca.12277',
        '10.1007/S00191-020-00680-W',]




print(asyncio.run(DOI_List_to_Result(dois)))