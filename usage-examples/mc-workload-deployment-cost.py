#
#Spec Reference: https://wiki.onap.org/display/DW/Edge+Scoping+MVP+for+Casablanca+-+ONAP+Enhancements#EdgeScopingMVPforCasablanca-ONAPEnhancements-Cloud-agnosticPlacement/Networking&HomingPolicies(Phase1-CasablancaMVP,Phase2-StretchGoal)
#

from jsonschema import validate

mc_workload_deployment_cost_policy_schema = {
	"cloudProviderWorkloadDeploymentCost": {
		"type": "array",
		"items": { "$ref": "#/definitions/xxx" }
	},
  	"definitions": {
		"xxx": {
			"type": "object",
			"required": [ "cloudProvider", "workloadDeploymentCost" ],
			"properties": {

				# VIM id
				"cloudProvider": {
				  "type": "string",
				},

				# For R3, netValue signifies cost per VIM id
				# Referring to cost-intent in the API from OOF -> MC
					# cost is fixed per cloud type for all workloads
					# cost specified in the respective plugin through a configuration file 
				"workloadDeploymentCost": {
				  "type": "number",
				}
			}
		}
	}
}

mc_workload_deployment_cost_policy_instance1 = {
	"cloudProviderWorkloadDeploymentCost": [
		{
			"cloudProvider": "Azure 1",
			"workloadDeploymentCost": 100
		},
		{
			"cloudProvider": "Azure 2",
			"workloadDeploymentCost": 101
		},
	],
}

mc_workload_deployment_cost_policy_instance2 = {
	"cloudProviderWorkloadDeploymentCost": [
		{
			"cloudProvider": "Wind River Titanium Cloud",
			"workloadDeploymentCost": 100
		},
	],
}

validate(mc_workload_deployment_cost_policy_instance1, mc_workload_deployment_cost_policy_schema)
validate(mc_workload_deployment_cost_policy_instance2, mc_workload_deployment_cost_policy_schema)
