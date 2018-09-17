

class LatencyCandidate(object):

    candidate_countries = list()

    def __init__(self,  candidate_countries):
        self.candidate_countries = candidate_countries




    def get_candidate_countries_list(self):
        cust_candidates = list()

        cust_candidates.append("USA")
        cust_candidates.append("CAN")
        cust_candidates.append("MEX")
        cust_candidates.append("RSA")
        cust_candidates.append("EST")
        cust_candidates.append("SDN")
        cust_candidates.append("LAT")
        cust_candidates.append("UAE")
        cust_candidates.append("GBR")
        cust_candidates.append("SDA")

        return cust_candidates


    def get_latency_candidate_countries(self):
        latency_candidates = list()

        latency_candidates.append("USA")
        latency_candidates.append("CAN")
        latency_candidates.append("XX1")
        latency_candidates.append("RSA")
        latency_candidates.append("XX2")
        latency_candidates.append("SDN")
        latency_candidates.append("XX3")
        latency_candidates.append("UAE")
        latency_candidates.append("XX4")
        latency_candidates.append("SDA")

        return latency_candidates


    def drop_candidates_with_no_latency_weight(self,lista, listb):
        pass
        #get the list of candidates and compare it with the list of assigned weights.
        # If there is no weight assigned to the countries in the candidate list, drop those candidates
        #new_list = [v for v in lista if v not in listb ]

        new_list = filter(lambda x: x not in lista, listb)

        #new_list = list(set(lista).difference(listb))
        return new_list # drop the items of this list from candidate list

    def assign_higher_weight_to_rest_of_the_world(self):
        pass
        #get the list of candidates and compare it with the list of assigned weights list.
        #if the list of candidates have countries that are not present in the weighted list countries, assign them the higher weight.





test = LatencyCandidate(None)
#test.printKV(countries_map)
print("Candidate List")
print(test.get_candidate_countries_list())
print("weight List")
print(test.get_latency_candidate_countries())
print("Difference")
print(test.drop_candidates_with_no_latency_weight(test.get_candidate_countries_list(),test.get_latency_candidate_countries()))
