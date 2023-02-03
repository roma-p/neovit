from dataclasses import dataclass

@dataclass(frozen=True)
class RepoModel():
    repo_hierarchy: dict
    assets_info: dict
    working_copy: dict
    repo_origin_path: str
    host: str
    user: str

@dataclass()
class Model():
    repo_models: dict
    # 1 pour le moment, mais des onglets à prévoir... 


