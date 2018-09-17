import collections

usa = list()
usa.append("USA,CAN,MEX")

w_europe = list()
w_europe.append("AUT, BEL, CZE, DNK,EST,FIN,FRA,DEU,GBR")

africa = list()
africa.append("DZA, AGO, BWA,BFA, BDI,CMR, COG, CIV, ZAF, ZWE")

#print(africa)

usa_europe = list();
usa_europe.append('WESTERN-EUROPE')



listall = list()
listall.append(usa)
listall.append(w_europe)
listall.append(africa)

#print(listall)

listall2 = list()
listall2.append(usa)
listall2.append(usa_europe)

listall2.remove(usa_europe)
print(listall2)
listall2.insert(1,w_europe)

print(listall2)
#print(usa)
#print(w_europe)
#print(usa_europe)

#for c in w_europe:
#    usa.append(c)

#print(usa)







#resolve countries
"""
for i, e in enumerate(listall2):
    for j, o in enumerate(e):
        for k, x in enumerate(o.split(',')):
            print(x.__len__())
            if x.__len__()>3 :
                pass
                print('resolve Countries')
                print(x, k)
            else:
                print(x, k)
"""


#print(listall2)


weight_map =collections.OrderedDict()
weight=0

for i, e in enumerate(listall):
    #print("i ")
    #print(i, e)
    for j, o in enumerate(e):
        for k, x in enumerate(o.split(',')):
            #print(k, x)
            weight_map[x] = weight
        weight = weight +1


            #print('\n')

        #weight_map = {}
        #print(" j ")
        #print(+j,o)
#print("---------------------------")
#print(weight_map)




"""class LatencyReductionTest(object):

    region_weight = collections.OrderedDict()

    def resolve_region_countries(self,  countries):
        #check the map with given location and
        #retrieve the values
        for c in countries:
           pass



    def assign_region_group_weight(self, countries):
         assign the latency group value to the country and returns a map
        region_latency_weight = dict()
        for i, e in enumerate(countries):
            for j, o in enumerate(e):
                for k, x in enumerate(o.split(',')):
                    region_latency_weight[x] = k

        return region_latency_weight

"""

"""for i in range(len(listall)):
    print(len(listall[i]))
    for j in range(len(listall[i])):
      print(listall[j])
      print(j)
      weight = {all[j]: "0"}
      weight_map.update(weight)
"""






