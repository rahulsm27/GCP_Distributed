import hydra
from hydra.utils import instantiate
from utils import TrainingInfo

from configs.config import setup_config
from omegaconf import DictConfig

setup_config()

@hydra.main(config_path=".",config_name="config", version_base=None )
def run(config:DictConfig):
    instance_group_creator = instantiate(config.infrastructure.instance_group_creator)
    instance_ids = instance_group_creator.launch_instance_group()

    training_info = TrainingInfo(

        project_id = config.infrastructure.project_id,
        zone = config.infrastructure.zone,
        instance_group_name = config.infrastructure.instance_group_creator.name,
        instance_ids = instance_ids,
        mlflow_experiment_url= config.infrastructure.mlflow.experiment_url

    )
    training_info.print_job_info()



if __name__ == "__main__":
    run()