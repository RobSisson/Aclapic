import asyncio

async def queue():

    return

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

# # CONFIRMED
# suffixes = ['endpoint1', 'endpoint2', 'endpoint3','endpoint4']
# end_points_to_call = [[0,1],[2],[0,1,2],[1]]
#
# print('Compile Endpoint list below')
# print(Compile_Endpoint_List(endpoints=suffixes,
#                            apis_to_call=end_points_to_call))

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

# CONFIRMED
# keys = ['key1','key2','key3']
# values = ['value1','value2','value3']
# position = [3,2,0]
#
# print('Kwargs Dict Below')
# print(Kwargs_to_dict(keys, values, position))


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
        array = [apis[i],filters[i],limits[i],periods[i], kwargs[i]]
        api.append(array)

    return api

# CONFIRMED
# apis = ['api1','api2','api3']
# filters = [['1','2','3'],['1','2'],['2','3']]
# limits = [5,10,20]
# period = [60,100,30]
# keys = [None,['api2 key 1', 'api2 key 2'], 'api3 key 1']
# values = [None,['api2 value 1', 'api2 value 2'], 'api3 value 1']
# positions = [None,[0, 1], 3]
#
# print('Compile Api List below')
# print(Compile_Api_List(apis=apis,
#                        filters=filters,
#                        limits=limits,
#                        periods=period,
#                        keys = keys,
#                        values=values,
#                        positions=positions))


def Create_URL(
        api,
        endpoint,
        # **kwargs,
):
    url = [api[0]]

    # print('api abo')

    if api[4] != None:
        print('kwards below')
        print(api[4])
        kwargs = api[4]
        print('len below')
        print(len(kwargs)+1)
        for i in range(len(kwargs)+1):
            # print('item bel')
            try:
                # print('kwarg i')
                # print(kwargs[i])
                url.append(kwargs[i])

            except:
                print('Endpoint Added')
                url.append(endpoint)

        url = ''.join(url)
    else:
        print('Kwargs is empty, creating url without additional arguments')
        url=str(api[0])+str(endpoint)
        print(url)


    return url

def Create_Next_URLs(
        api_list,
        endpoint_list,
):
    example_queue = []
    for i, endpoint in enumerate(endpoint_list):

        # print(endpoint[2])
        # print('endpoint above')
        if endpoint[2] == None: # would it be faster to remove the called endpoints from this list?
            done_count = 0
            for i, api_to_call in enumerate(endpoint[1]):

                if api_to_call[0] == 0:
                    api_number = api_to_call[1] # this would be the number of the api to call, not the api itself
                    ep = endpoint[0]


                    example_queue.append(Create_URL(api_list[api_number], endpoint[0]))


                    api_to_call[1] = 1
                    break

                elif api_to_call[1] == 1:
                    done_count += 1

                if len(endpoint[1]) <= done_count:
                    print("All Api's for " + str(endpoint[0] + ' searched, and no result found'))

    return print(example_queue)








# print('Compile Endpoint list below')
# print(Compile_Endpoint_List(endpoints=suffixes,
#                            apis_to_call=end_points_to_call))


endpoints = ['endpoint 1 - ', 'endpoint 2 - ', 'endpoint 3 - ','endpoint 4 - ']
apis_to_call = [[0,1],[2],[0,1,2],[1]]

apis = ['api 1 - ','api 2 - ','api 3 -']
filters = [['1','2','3'],['1','2'],['2','3']]
limits = [5,10,20]
period = [60,100,30]
keys = [None,[' api 2 key 1:', ' api 2 key 2:'], ' api 3 key 1:']
values = [None,[' api 2 value 1 - ', ' api 2 value 2 - '], ' api 3 value 1 - ']
positions = [None,[2, 0], 1]

# api 1 - endpoint 1
# api 3 - endpoint 2 - # api 3 key 1: api 3 value 1
# api 1 - endpoint 3
# api 2 - api2 key 2: api2 value 2 - endpoint4 - # api2 key 1: api2 value 1


# print('Compile Api List below')
# print()

Create_Next_URLs(Compile_Api_List(apis=apis,
                                  filters=filters,
                                  limits=limits,
                                  periods=period,
                                  keys = keys,
                                  values=values,
                                  positions=positions),
                 Compile_Endpoint_List(endpoints=endpoints,
                                       apis_to_call=apis_to_call)
                                                         )

#
#
#
# print(
#     Create_Next_URL(
#
#     Compile_Endpoint_Array(endpoints=endpoints,
#                            keys=keys,
#                            limits=limits,
#                            periods=period),
#
#     Compile_Suffix_Array(suffixes=suffixes,
#                          endpoints_to_call=end_points_to_call),
#                )
#       )

[['api1', ['1', '2', '3'], 5, 60, None],
 ['api2', ['1', '2'], 10, 100, [{'api2 position 1': 'api2 key 1api2 value 1', 'api2 position 2': 'api2 key 2api2 value 2'}]],
 ['api3', ['2', '3'], 20, 30, [{'api3 position 1': 'api3 key 1api3 value 1'}]]]
