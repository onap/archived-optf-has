import collections


class LatencyReduction(object):

    region_weight = collections.OrderedDict()
    countries = list()
    regions = collections.OrderedDict()

    def __init__(self, region_weight, countries, regions):
        self.region_weight = region_weight
        self.countries = countries
        self.regions = regions


    def printKV(self, countries_map):
        for k,v in countries_map.items():
            print("country : {0}, Value :{1}".format(k,v))



    def resolve_region_countries(self, countries_list, regions_map):
        # check the map with given location and retrieve the values
        if countries_list is None:
            return countries_list

        invalid_entries = list()

        map_index = 0
        for i, e in enumerate(countries_list):
            if e is None: continue

            for k, region in enumerate(e.split(',')):
                if region.__len__() != 3:
                    if region == "*":
                        continue
                    region_list = regions_map.get(region)
                    map_index = map_index + 1
                    if region_list is None:
                        invalid_entries.append(region)
                        #countries_list.remove(region)  # remove the invalid entries from list
                        continue
                    countries_list.remove(countries_list[i])
                    countries_list.insert(i, region_list)

        print(countries_list)
        print(invalid_entries)

        countries_list = list(filter(lambda country: ( country not in invalid_entries ),countries_list ))
        print(countries_list)
        #filter(lambda x: x not in countries_list)

        print(countries_list)
        print(self.get_candidate_countries_list())

        temp_list = list()

        if countries_list.__getitem__(countries_list.__len__()-1) == "*":
            candidate_countries = ''
            countries_list.remove(countries_list.__getitem__(countries_list.__len__()-1))

            for country_group in countries_list:
                for country in country_group.split(','):
                    temp_list.append(country)

            print(temp_list)


            new_list = list(set(temp_list).difference(self.get_candidate_countries_list()))
            print(new_list)
            for c_group in new_list:
                candidate_countries+=c_group
                candidate_countries +=','

            print(candidate_countries[:-1])
            countries_list.append(candidate_countries[:-1])
            #print countries_list
        else:
            pass
            #filterout the candidates that does not match the countries list
            #filter(lambda x: x not in countries_list, self.get_candidate_countries_list())

        return countries_list


    """def resolve_region_countries2(self, countries, regions):
        ## check the map with given location and retrieve the values
        temp = list();


        for j, o in enumerate(countries):
            for k, region in enumerate(o.split(',')):
                if region.__len__() > 3:
                    region_list = regions.get(region)
                    self.countries.remove(region)
                    self.countries.insert(k, region_list)
                    # self.countries.append(region_list)
                    continue

        return countries"""




    def assign_region_group_weight(self, countries):
        """ assign the latency group value to the country and returns a map"""
        region_latency_weight = collections.OrderedDict()
        weight = 0

        for i, e in enumerate(countries):
            #for j, o in enumerate(e):
            for k, x in enumerate(e.split(',')):
                region_latency_weight[x] = weight
            weight = weight + 1

        return region_latency_weight


    def drop_candidates_with_no_latency_weight(self, latency_weight_candidates,candidates_list):
        pass
        #get the list of candidates and compare it with the list of assigned weights.
        # If there is no weight assigned to the countries in the candidate list, drop those candidates


    def get_candidate_countries_list(self):
        cust_candidates = list()

        cust_candidates.append("USA")
        cust_candidates.append("CAN")
        cust_candidates.append("MEX")
        cust_candidates.append("AUT")
        cust_candidates.append("BEL")
        cust_candidates.append("CZE")
        cust_candidates.append("DNK")


        return cust_candidates



listusa = list()
listusa.append("AUT,BEL,CZE,DNK,EST,FIN,FRA,DEU,GBR")
listusa.append("USA,CAN,MEX")

listafrica = list()
listafrica.append('DZA,AGO,BWA,BFA,BDI,CMR,COG,CIV,ZAF,ZWE')

listDEU = list()
listDEU.append('AUT,BEL,CZE,DNK,EST,FIN,FRA,DEU,GBR')

countires = list()
#countires.append('None')
countires.append('USA,CAN,MEX')
countires.append('WESTERN-EUROPE')
countires.append('WE')
countires.append('XXXX')
#countires.append('AFRICA')
countires.append('*')



#countries_map = collections.OrderedDict()
#countries_map = {
#                'USA':  listusa,
#                'SAF' : listafrica,
#                'DEU' : listDEU#
#
#}
#countryMap = collections.OrderedDict()
#countryMap = {
#               'USA':"USA,CAN,MEX",
#               'Europe':"AUT,BEL,CZE,DNK,EST,FIN,FRA,DEU,GBR",
#               'Africa':"DZA,AGO,BWA,BFA,BDI,CMR,COG,CIV,ZAF,ZWE"
#}

#lista = countryMap.values()
regionMap = collections.OrderedDict()
regionMap = {
                'WESTERN-EUROPE':"AUT,BEL,CZE,DNK,EST,FIN,FRA,DEU,GBR",
                'AFRICA' :  "DZA,AGO,BWA,BFA,BDI,CMR,COG,CIV,ZAF,ZWE"
}


region_weight = collections.OrderedDict()

test = LatencyReduction(region_weight,countires,regionMap)
#test.printKV(countries_map)


print(test.resolve_region_countries(countires,regionMap ))

#print(test.assign_region_group_weight(countires))

#test.get_candidate_countries_list()