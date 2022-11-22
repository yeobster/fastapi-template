from jinja2 import (
    Environment,
    FileSystemLoader,
)
from core.config import settings
from utils import _string


def generate(module_name: str, router_version: str):
    """템플릿 생성하기

    Args:
        module_name (str): 모듈명
        router_version (str): 생성할 라우터 버전
    """

    # set name
    model_name = module_name[0].capitalize() + module_name[1:]
    camelcase = _string.convert_camel(model_name)
    snakecase = _string.convert_snakecase(camelcase)
    model_cases = {
        "model_camel": camelcase,
        "model_snake": snakecase,
    }

    # set directory path
    path = settings.BASE_DIR
    template_path = path + "/template"
    crud_path = path + "/crud"
    model_path = path + "/models"
    router_path = path + "/router/backend/" + router_version

    # set file loader and env
    loader = FileSystemLoader([template_path], encoding="utf-8")
    env = Environment(loader=loader)

    ## add crud, router, model file.
    crud_template = env.get_template("crud.template")
    router_template = env.get_template("router.template")
    model_template = env.get_template("model.template")
    model_template.stream(**model_cases).dump(
        model_path + "/" + snakecase + ".py"
    )
    crud_template.stream(**model_cases).dump(
        crud_path + "/" + snakecase + ".py"
    )
    router_template.stream(**model_cases).dump(
        router_path + "/" + snakecase + ".py"
    )

    # add __init__.py
    init_py = "__init__.py"

    # model __init__
    with open(model_path + "/" + init_py, "r+", encoding="utf-8") as f:
        old_models = f.read()

    model_init_template = env.get_template("models__init__.template")
    model_init_template.stream({"old_models": old_models}, **model_cases).dump(
        model_path + "/__init__.py"
    )

    # crud __init__
    with open(crud_path + "/" + init_py, "r+", encoding="utf-8") as f:
        old_crud = f.read()

    crud_init_template = env.get_template("crud__init__.template")
    crud_init_template.stream({"old_crud": old_crud}, **model_cases).dump(
        crud_path + "/__init__.py"
    )

    # print paths
    print("아래 디렉토리에 파일이 생성됩니다.")
    print("CRUD: ", crud_path)
    print("Model: ", model_path)
    print("Router: ", router_path)
