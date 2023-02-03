from vit import vit_lib
from vit.file_handlers import repo_config
from vit.vit_lib import infos
from vit.vit_lib import fetch

from neovit.model import RepoModel

def fetch_repo_and_update_model(model, repo_name):
    repo_path  = model.repo_models[repo_name]['path']
    repo_model = model.repo_models[repo_name]['model']
    # async ....
    #vit.fetch.fetch(repo_path)
    create_repo_model(model, repo_name)

def create_repo_model(repo_name, repo_path):
     host, origin_path, user = repo_config.get_origin_ssh_info(repo_path)
     return RepoModel(
        repo_hierarchy=fetch.get_repo_hierarchy(repo_path),
        assets_info=fetch.get_all_assets_info(repo_path),
        working_copy="prout", #infos.get_info_from_all_ref_files(repo_path),
        repo_origin_path=origin_path,
        user=user,
        host=host
    )
 
