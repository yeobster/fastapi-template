def convert_list_to_string(org_list, seperator=","):
    """
    list to string
    """
    return seperator.join(org_list)


def convert_snakecase(in_str: str):
    snakecase: str
    flag: bool = False

    for word in in_str:
        # 첫번째 글자만 소문자로 변경
        if flag == False:
            flag = True
            snakecase = word.lower()
            continue

        # 나머지 글자에 대문자가 있다면 _로 변경
        if word.isupper():
            snakecase = snakecase + "_" + word.lower()
            continue

        # append
        snakecase = snakecase + word

    return snakecase


def convert_camel(in_str: str):
    camelcase: str = ""
    upper_flag: bool = True

    for word in in_str:
        if word == "_":
            upper_flag = True
            continue

        if upper_flag is False:
            camelcase = camelcase + word
            continue

        camelcase = camelcase + word.upper()
        upper_flag = False

    return camelcase
