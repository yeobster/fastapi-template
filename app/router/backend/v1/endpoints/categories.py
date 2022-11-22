import json
from fastapi.param_functions import Query
import phonenumbers
import pycountry

from fastapi import APIRouter, Path
from core.config import settings
from utils.iso_3166_korean import get_ko_name_by_alpha_2

CATEGORY_PATH = settings.BASE_DIR + "/json_categories"
COUNTRY_FLAGS_BASE = "https://www.countryflags.io"


router = APIRouter()


@router.get("/nations/iso3166")
def get_iso_3166_with_country_code(fuzzy: str = Query(None)):
    countries = pycountry.countries

    if fuzzy is not None:
        countries = pycountry.countries.search_fuzzy(fuzzy)

    r = []
    for c in countries:
        dictable = c.__dict__["_fields"]

        alpha2: str = dictable["alpha_2"]
        alpha2_lower = alpha2.lower()
        country_code = phonenumbers.country_code_for_region(
            dictable["alpha_2"]
        )
        dictable["country_code"] = str(country_code)
        dictable["ko_name"] = get_ko_name_by_alpha_2(dictable["alpha_2"])
        dictable["flag_url"] = (
            COUNTRY_FLAGS_BASE + "/" + alpha2_lower + "/flat/64.png"
        )
        r.append(dictable)

    return r


@router.get("/nations/iso3166/{alpha_2}")
def get_iso_3166_by_alpha_2(alpha_2: str = Path(None)):

    country = pycountry.countries.get(alpha_2=alpha_2)
    dictable = country.__dict__["_fields"]

    alpha2: str = dictable["alpha_2"]
    alpha2_lower = alpha2.lower()
    country_code = phonenumbers.country_code_for_region(dictable["alpha_2"])
    dictable["country_code"] = country_code
    dictable["flag_url"] = (
        COUNTRY_FLAGS_BASE + "/" + alpha2_lower + "/flat/64.png"
    )
    return dictable


@router.get("/user-types")
def get_user_type():
    """
    유저 타입
    """
    fpath = CATEGORY_PATH + "/user_types.json"
    with open(fpath, encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    return json_data


@router.get("/account-types")
def get_account_type():
    """
    유저, 슈퍼유저, 광고모델 구분
    production에서 마지막으로 수정한 계정타입
    """

    fpath = CATEGORY_PATH + "/account_types.json"
    with open(fpath, encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    return json_data
