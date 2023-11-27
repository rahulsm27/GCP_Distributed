from dataclasses import dataclass

from omegaconf import MISSING, SI

from configs.infrastructure.instance_group_creator_configs import InstanceGroupCreatorConfig

@dataclass
class MLFlowConfig:
    mlflow_external_tracking_uri = SI("${oc.env:MLFLOW_TRACKING_URI,localhost:6101}") # environement varialbe
    mlflow_internal_tracking_uri = SI("${oc.env:MLFLOW_INTERNAL_TRACKING_URI,localhost:6101}")
    experiment_name = "Default"
    run_name = None
    run_id = None
    experiment_id = None
    experiment_url = SI("${.mlflow_external_tracking_uri}/#/experiment/${.experiment_id}/runs/${.run_id}")



@dataclass
class InfrastructureConfig:
    project_id: str = MISSING
    region: str = MISSING
    zone: str = MISSING
    instance_group_creator: InstanceGroupCreatorConfig = InstanceGroupCreatorConfig()