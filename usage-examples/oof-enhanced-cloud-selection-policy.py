#
#Spec Reference: https://wiki.onap.org/display/DW/Edge+Scoping+MVP+for+Casablanca+-+ONAP+Enhancements#EdgeScopingMVPforCasablanca-ONAPEnhancements-Cloud-agnosticPlacement/Networking&HomingPolicies(Phase1-CasablancaMVP,Phase2-StretchGoal)
#

from jsonschema import validate

oof_cloud_selection_policy_schema = {
	"service": {"type": "string"},
	"policyName": {"type": "string"},
	"policyDescription": {"type": "string"},
	"templateVersion": {"type": "string"},
	"version": {"type": "string"},
	"priority": {"type": "string"},
	"riskType": {"type": "string"},
	"riskLevel": {"type": "string"},
	"guard": {"type": "string"},

	"content": {
		"type": "object",
		"required": ["cost-intent", "deployment-intent"],
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
		},
	},

	"resources": {"type", "array"}, #"vgw" is also interchangeably used as "vg"
	"applicableResources": {"type", "string"},
	"identity": {"type", "string"},
	"policyScope": {"type", "array"},
	"policyType": {"type", "string"}
}

#
#Example 1: vCPE, Burstable QoS
#vCPE: Infrastructure Resource Isolation for VNF with Burstable QoS
#
oof_cloud_selection_policy_instance1 = {
	"service": "cloudSelectionPolicy",
	"policyName": "oofMulti-cloudCasablanca.cloudSelectionPolicy_vCPE_VNF",
	"policyDescription": "Cloud Selection Policy for vCPE VNFs",
	"templateVersion": "0.0.1",
	"version": "oofMulti-cloudCasablanca",
	"priority": "3",
	"riskType": "test",
	"riskLevel": "2",
	"guard": "False",

	"content": {
		"vnfc": "vgw",
		"cost-intent": True,
		"deployment-intent": {
            "Infrastructure Resource Isolation for VNF": "Burstable QoS",
            "Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": 25,

		},
	},

	"resources": ["vgw"], #"vgw" is also interchangeably used as "vg"
	"applicableResources": "any",
	"identity": "cloud-atrributes",
	"policyScope": ["vCPE", "US", "INTERNATIONAL", "ip", "vgw", "vgmux"],
	"policyType": "AllPolicy"
}

#
#Example 2:
#vCPE: Infrastructure Resource Isolation for VNF with Guaranteed QoS
#
oof_cloud_selection_policy_instance2 = {
	"service": "cloudSelectionPolicy",
	"policyName": "oofMulti-cloudCasablanca.cloudSelectionPolicy_vCPE_VNF",
	"policyDescription": "Cloud Selection Policy for vCPE VNFs",
	"templateVersion": "0.0.1",
	"version": "oofMulti-cloudCasablanca",
	"priority": "3",
	"riskType": "test",
	"riskLevel": "2",
	"guard": "False",

	"content": {
		"vnfc": "vgw",
		"cost-intent": True,
		"deployment-intent": {
			"Infrastructure Resource Isolation for VNF": "Guaranteed QoS",
		},
	},

	"resources": ["vgw"], #"vgw" is also interchangeably used as "vg"
	"applicableResources": "any",
	"identity": "cloud-atrributes",
	"policyScope": ["vCPE", "US", "INTERNATIONAL", "ip", "vgw", "vgmux"],
	"policyType": "AllPolicy"
}

#
#Example 3:
#vDNS: Infrastructure HA for VNF & Infrastructure Resource Isolation for VNF with Burstable QoS
#
oof_cloud_selection_policy_instance3 = {
	"service": "cloudSelectionPolicy",
	"policyName": "oofMulti-cloudCasablanca.cloudSelectionPolicy_vDNS_VNF",
	"policyDescription": "Cloud Selection Policy for vDNS VNFs",
	"templateVersion": "0.0.1",
	"version": "oofMulti-cloudCasablanca",
	"priority": "3",
	"riskType": "test",
	"riskLevel": "2",
	"guard": "False",

	"content": {
		"vnfc": "vdns",
		"cost-intent": True,
		"deployment-intent": {
			"Cloud Type (Cloud Provider)": "VMware VIO",
			"Infrastructure High Availability for VNF": True,
			"Infrastructure Resource Isolation for VNF": "Burstable QoS",
			"Infrastructure Resource Isolation for VNF - Burstable QoS Oversubscription Percentage": 25,
		},
	},

	"resources": ["vDNS"],
	"applicableResources": "any",
	"identity": "cloud-atrributes",
	"policyScope": ["vDNS", "US", "INTERNATIONAL", "vDNS"],
	"policyType": "AllPolicy"
}

#
# Example 4:
# vDNS: Infrastructure HA for VNF & Infrastructure Resource Isolation for VNF 
# with Guaranteed QoS
#
oof_cloud_selection_policy_instance4 = {
	"service": "cloudSelectionPolicy",
	"policyName": "oofMulti-cloudCasablanca.cloudSelectionPolicy_vDNS_VNF",
	"policyDescription": "Cloud Selection Policy for vDNS VNFs",
	"templateVersion": "0.0.1",
	"version": "oofMulti-cloudCasablanca",
	"priority": "3",
	"riskType": "test",
	"riskLevel": "2",
	"guard": "False",

	"content": {
		"vnfc": "vdns",
		"cost-intent": True,
		"deployment-intent": {
			"Infrastructure High Availability for VNF": True,
			"Infrastructure Resource Isolation for VNF": "Guaranteed QoS",
		},
	},

	"resources": ["vDNS"],
	"applicableResources": "any",
	"identity": "cloud-atrributes",
	"policyScope": ["vDNS", "US", "INTERNATIONAL", "vDNS"],
	"policyType": "AllPolicy"
}

validate(oof_cloud_selection_policy_instance1, oof_cloud_selection_policy_schema)
validate(oof_cloud_selection_policy_instance2, oof_cloud_selection_policy_schema)
validate(oof_cloud_selection_policy_instance3, oof_cloud_selection_policy_schema)
validate(oof_cloud_selection_policy_instance4, oof_cloud_selection_policy_schema)
