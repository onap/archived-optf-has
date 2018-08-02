#
#Spec Reference: https://wiki.onap.org/display/DW/Edge+Scoping+MVP+for+Casablanca+-+ONAP+Enhancements#EdgeScopingMVPforCasablanca-ONAPEnhancements-Cloud-agnosticPlacement/Networking&HomingPolicies(Phase1-CasablancaMVP,Phase2-StretchGoal)
#

from jsonschema import validate

oof_mc_policy_capacity_check_api_request_schema = {
    "type" : "object",
    "properties" : {

        # vnfc is not used in the OOF->MC path for R3, this is kept to be consistent 
        # with the SO-> MC path
		"vnfc": {"type": "string"}, 

		# evaluate cloud cost if set 
		# cost is fixed per cloud type for all workloads -- simplifying assumption for R3
		# cost specified in the respective plugin through a configuration file 
        "cost-intent" : {"type" : "boolean"}, 

		"deployment-intent": {"type": "object"},
		"properties" : {

			# Azure, K8S, OpenStack, VMware VIO, Wind River Titanium
			"Cloud Type (Cloud Provider)": {"type", "string"},

			"Infrastructure High Availability for VNF": {"type", "boolean"},

			"Infrastructure Resource Isolation for VNF": {"type", "string"},

			# Infrastructure Resource Isolation for VNF
			# Only certain pre-defined over-subscription values are allowed to 
			# reflect practical deployment and simplify implementation for R3
			"Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": {"type": "int"},
		},

		# vCPU, Memory, Storage, VIMs - part of R2 capacity check
		"vCPU": {"type": "number"},  # number of cores
		"Memory": {"type": "number"},  # size of memory, GB
		"Storage": {"type": "number"},  # size of storage, GB
	    "VIMs": {"type": "array"},  # VIMs OOF wish to check with
	},
	"required": ["cost-intent", "deployment-intent", "vCPU", "Memory", "Storage", "VIMs"] 
}

#
#Example 1: vCPE, Burstable QoS
#vCPE: Infrastructure Resource Isolation for VNF with Burstable QoS
#
oof_mc_policy_api_instance1 = {
"vnfc": "vgw",
"cost-intent": True,
"deployment-intent": {
	"Cloud Type (Cloud Provider)": "VMware VIO",
	"Infrastructure Resource Isolation for VNF": "Burstable QoS",
	"Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": 25,
},
"vCPU": 16,
"Memory": 96,
"Storage": 512,
"VIMs": ["VMware 1", "VMware 2", "Azure 1", "Wind River 1"],
}

#
#Example 2:
#vCPE: Infrastructure Resource Isolation for VNF with Guaranteed QoS
#
oof_mc_policy_api_instance2 = {
	"vnfc": "vgw",
	"cost-intent": True,
	"deployment-intent": {
		"Infrastructure Resource Isolation for VNF": "Guaranteed QoS",
	},
	"vCPU": 16,
	"Memory": 96,
	"Storage": 512,
	"VIMs": ["VMware 1", "VMware 2", "Azure 1", "Wind River 1"],
}

#
#Example 3:
#vDNS: Infrastructure HA for VNF & Infrastructure Resource Isolation for VNF with Burstable QoS
#
oof_mc_policy_api_instance3 = {
	"vnfc": "vdns",
	"cost-intent": True,
	"deployment-intent": {
		"Cloud Type (Cloud Provider)": "VMware VIO",
		"Infrastructure High Availability for VNF": True,
		"Infrastructure Resource Isolation for VNF": "Burstable QoS",
		"Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": 25,
	},
	"vCPU": 16,
	"Memory": 96,
	"Storage": 512,
	"VIMs": ["VMware 1", "VMware 2", "Azure 1", "Wind River 1"],
}

#
# Example 4:
# vDNS: Infrastructure HA for VNF & Infrastructure Resource Isolation for VNF 
# with Guaranteed QoS
#
oof_mc_policy_api_instance4 = {
	"vnfc": "vdns",
	"cost-intent": True,
	"deployment-intent": {
		"Infrastructure High Availability for VNF": True,
		"Infrastructure Resource Isolation for VNF": "Guaranteed QoS",
	},
	"vCPU": 16,
	"Memory": 96,
	"Storage": 512,
	"VIMs": ["VMware 1", "VMware 2", "Azure 1", "Wind River 1"],
}

oof_mc_policy_capacity_check_api_response_schema = {
	"cloudRegionNetValue": {
		"type": "array",
		"items": { "$ref": "#/definitions/xxx" }
	},
  	"definitions": {
		"xxx": {
			"type": "object",
			"required": [ "VIM", "netValue" ],
			"properties": {

				# VIM id
				"VIM": {
				  "type": "string",
				},

				# For R3, netValue signifies cost per VIM id
				# Referring to cost-intent in the API from OOF -> MC
					# cost is fixed per cloud type for all workloads
					# cost specified in the respective plugin through a configuration file 
				"netValue": {
				  "type": "number",
				}
			}
		}
	}
}

oof_mc_policy_api_response_instance = {
	"cloudRegionNetValue": [
		{
			"VIM": "Azure",
			"netValue": 100
		},
		{
			"VIM": "VMware 1",
			"netValue": 101
		},
		{
			"VIM": "Wind River Titanium 2",
			"netValue": 102
		},
		{
			"VIM": "Wind River Titanium 1",
			"netValue": 102
		},
	],
}

validate(oof_mc_policy_api_instance1, oof_mc_policy_capacity_check_api_request_schema)
validate(oof_mc_policy_api_instance2, oof_mc_policy_capacity_check_api_request_schema)
validate(oof_mc_policy_api_instance3, oof_mc_policy_capacity_check_api_request_schema)
validate(oof_mc_policy_api_instance4, oof_mc_policy_capacity_check_api_request_schema)

validate(oof_mc_policy_api_response_instance, oof_mc_policy_capacity_check_api_response_schema)
