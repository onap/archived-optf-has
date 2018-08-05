#
#Spec Reference: https://wiki.onap.org/display/DW/Edge+Scoping+MVP+for+Casablanca+-+ONAP+Enhancements#EdgeScopingMVPforCasablanca-ONAPEnhancements-Cloud-agnosticPlacement/Networking&HomingPolicies(Phase1-CasablancaMVP,Phase2-StretchGoal)
#
#The same information is opaquely passed from OOF to SO
#

from jsonschema import validate

so_mc_policy_api_request_schema = {
    "type" : "object",
    "properties" : {

        # vnfc is not used in the OOF->MC path for R3, this is kept to be consistent 
        # with the SO-> MC path
		"vnfc": {"type": "string"}, 

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
	},
	"required": ["deployment-intent"] 
}

#
#Example 1: vCPE, Burstable QoS
#vCPE: Infrastructure Resource Isolation for VNF with Burstable QoS
#
so_mc_policy_api_instance1 = {
	"vnfc": "vgw",
	"deployment-intent": {
		"Cloud Type (Cloud Provider)": "VMware VIO",
		"Infrastructure Resource Isolation for VNF": "Burstable QoS",
		"Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": 25,
	},
}

#
#Example 2:
#vCPE: Infrastructure Resource Isolation for VNF with Guaranteed QoS
#
so_mc_policy_api_instance2 = {
	"vnfc": "vgw",
	"deployment-intent": {
		"Infrastructure Resource Isolation for VNF": "Guaranteed QoS",
	},
}

#
#Example 3:
#vDNS: Infrastructure HA for VNF & Infrastructure Resource Isolation for VNF with Burstable QoS
#
so_mc_policy_api_instance3 = {
	"vnfc": "vdns",
	"deployment-intent": {
		"Cloud Type (Cloud Provider)": "VMware VIO",
		"Infrastructure High Availability for VNF": True,
		"Infrastructure Resource Isolation for VNF": "Burstable QoS",
		"Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": 25,
	},
}

#
# Example 4:
# vDNS: Infrastructure HA for VNF & Infrastructure Resource Isolation for VNF 
# with Guaranteed QoS
#
so_mc_policy_api_instance4 = {
	"vnfc": "vdns",
	"deployment-intent": {
		"Infrastructure High Availability for VNF": True,
		"Infrastructure Resource Isolation for VNF": "Guaranteed QoS",
	},
}

validate(so_mc_policy_api_instance1, so_mc_policy_api_request_schema)
validate(so_mc_policy_api_instance2, so_mc_policy_api_request_schema)
validate(so_mc_policy_api_instance3, so_mc_policy_api_request_schema)
validate(so_mc_policy_api_instance4, so_mc_policy_api_request_schema)
