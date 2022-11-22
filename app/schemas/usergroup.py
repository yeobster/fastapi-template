# id=1, name="level 1", desc="게스트 유저그룹"
# models.UserGroup(id=2, name="level 2", desc="기본 유저그룹", created_at=now)
# models.UserGroup(id=3, name="level 3", desc="관리자 유저그룹", created_at=now)


class UserGroup:
    guest = {"id": 1, "name": "level 1", "desc": "게스트 유저그룹"}
    base = {"id": 2, "name": "level 2", "desc": "기본 유저그룹"}
    admin = {"id": 3, "name": "level 3", "desc": "관리자 유저그룹"}


def get_usergroup_id_list():
    return [UserGroup.guest["id"], UserGroup.base["id"], UserGroup.admin["id"]]
