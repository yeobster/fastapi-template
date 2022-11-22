import sys
from template import base


if __name__ == "__main__":

    ### module name ###
    msg = "신규 모듈을 설치합니다.\n\
        하단에 추가할 모듈이름을 입력해 주세요.\n\
        모듈이름은 최대 20글자까지만 허용되며 \n\
        언더라인(_) 이나 영문만 가능합니다. \n\
        이름은 단수로 입력해주세요.\n\
        또한 입력한 모듈이름은 자동으로 trim됩니다.\n\
        입력 예) userGroup -> table name : user_group, crud : user_group.py, model: user_group, model_class_name: UserGroup"
    print(msg)

    module_name = sys.stdin.readline()
    module_name = module_name.strip()
    length = len(module_name)

    # check input length
    if length > 20 or length < 1:
        raise Exception(
            f"입력되지 않았거나 최대글자수를 초과했습니다.\
            입력된 내용 {module_name}({length})"
        )

    # # check name
    # if not module_name.isalpha() and module_name != "_":
    #     raise Exception("언더라인(_) 이나 영문이 아닙니다.")
    if not module_name[0].isalpha():
        raise Exception("영문이 아닙니다.")

    ### router version ###
    default_version = "v1"
    msg = "router에 추가할 버전을 숫자로 입력해주세요(기본: version 1). 기본으로 설정하실 경우 Enter."
    print(msg)

    router_version = sys.stdin.readline()
    router_version = router_version.strip()

    if not router_version.isnumeric() and router_version != "":
        raise Exception(f"숫자만 입력가능합니다.(입력: {router_version})")

    if router_version == "":
        router_version = default_version
    else:
        router_version = "v" + router_version

    base.generate(module_name=module_name, router_version=router_version)
