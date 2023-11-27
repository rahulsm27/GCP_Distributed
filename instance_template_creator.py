
from enum import Enum
from dataclasses import dataclass
from utils import get_logger
from google.cloud import compute_v1
class VMType(Enum):
    STANDARD = "STANDARD"
    STOP  = "SPOT" # no deadline. can be prempted by google
    PREEMPTIBLE = "PREEMPTIBLE"  # it will be prempted after 24 hours


@dataclass
class BootDiskConfig:
    project_id : str
    name : str
    size_gb : int 
    labels : dict[str=Nonestr]

@dataclass
class VMConfig:
    machine_type : str
    accelerator_count : int 
    accelerator_type : str
    vm_type : VMType
    disks : list[str] # boot disk is used to operate the OS.# this is ssd disk for CV . cerate disk with image datasets. can be only attached  in read mode to multiple vm. if we want to write it can be attached in write mode only to single vm NSD can be attached in read and write mode but are slow.

@dataclass
class VMMetadataConfig:
    instance_group_name : str
    docker_imnage : str
    zone : str 
    python_hash_seed : int
    mlflow_tracking_uri : str
    node_count : int # how many vms
    disks : list[str] # in each vm we need to mount


class InstanceTemplateCreator:
    def __init__(self,
                 scopes:list[str], # permisions for vm,
                 network : str  ,
                 subnetwork : str,
                 startup_script_path : str,
                 vm_config : VMConfig,
                 boot_disk_config : BootDiskConfig,
                 vm_metadata_config: VMMetadataConfig,
                 temmplate_name : str,
                 project_id : str,
                 labels : dict[str,str] = {}
                
                 )  :
        
        self.logger = get_logger(self.__class__.__name__)


        self.scopes:list[str] = scopes# permisions for vm            
        self.network : str     = network      
        self.subnetwork : str = subnetwork
        self.startup_script_path : str =startup_script_path
        self.vm_config : VMConfig = vm_config
        self.boot_disk_config : BootDiskConfig = boot_disk_config
        self.vm_metadata_config: VMMetadataConfig = vm_metadata_config
        self.temmplate_name : str = temmplate_name.lower()
        self.project_id : str = project_id
        self.labels : dict[str,str] = labels


        self.template = compute_v1.InstanceTemplate()
        self.template.name = self.temmplate_name

    def create_template(self):
        self.logger.info("Started creating instance template ...")
        self.logger.info(f"{self.vm_metadata_confg=}")

        self.create_book_disk()

    def _create_book_disk(self) :
        boot_disk = compute_v1.AttachedDisk()
        boot_disk_initialize_params = compute_v1.AttachedDiskInitializeParams()
        boot_disk_image = self._get_disk_image(self.boot_disk_config.project_id,self.boot_disk_config.name)
        boot_disk_initialize_params.source_image = boot_disk_image.self_link
        boot_disk_initialize_params.disk_size_gb = self.boot_disk_config.size_gb
        boot_disk_initialize_params.labels = self.boot_disk_config.labels
        boot_disk.initialize_params = boot_disk_initialize_params
        boot_disk.auto_delete = True
        boot_disk.boot = True
        boot_disk.device_name = self.boot_disk_config.name

        self.template.properties.disks = [boot_disk]


    def _get_disk_image(self, project_id:str,image_name:str):
        image_client = compute_v1.ImagesClient()
        return image_client.get(project=project_id,image=image_name)
    

    def _attach_disks(self):
        disk_names = self.vm_config.disks
        for disk_name in disk_names:
            disk = compute_v1.AttachedDisk(auto_delete = False, boot =False, mode="Read_only",
                                           device_name = disk_name, source=disk_name)
            self.template.properties.disks.append(disk)

        if len(disk_names) > 0:
            self.template.properties.metadata.items.append(compute_v1.Items(key="disks",value="\n".join(disk_names)))




