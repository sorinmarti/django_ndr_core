import json
import os
import requests
from django.conf import settings

from ndr_core.ndr_helpers import get_api_config


def get_base_string(api_config, repository, endpoint, query_type, page):
    """ Composes the base string for the API endpoint. Example https://api-host.com:80/endpoint/?s=10&p=1
        (This requests the first 10 results: page=1, size=10)"""
    config = api_config["repositories"][repository]
    base_string = f"{config['api_protocol']}://{config['api_host']}:{config['api_port']}/{endpoint}/{query_type}"
    if page != 0:
        base_string += f"?s={api_config['page_size']}&p={page}"
    return base_string


def create_advanced_search_string(repository, endpoint, query_type, get_params):
    """ Composes an advanced search query. There are a number of configured search fields in the config which are used
        to create the search form and thus create a URL which contains the search values filled in the form. With these
        values, a search query for the endpoint is composed."""

    api_config = get_api_config()
    # Get the page of the search result. For a new search it is not set and thus 1
    page_to_show = get_params.get("page", 1)
    api_request_str = get_base_string(api_config, repository, endpoint, query_type, page_to_show)
    all_values = list()

    # Walk through the configured search fields
    for field in api_config["search_fields"]:
        field_config = api_config["search_fields"][field]
        # Retrieve the name of the API parameter for the endpoint
        if "api_param" in field_config:
            api_param = field_config["api_param"]
        else:
            api_param = field

        # Join name and search value
        param_str = ""
        if field_config["type"] == "dictionary" and field_config["widget"] == "multi_search":
            value_list = get_params.getlist(field+"[]", [])
            if len(value_list) > 0:
                param_str = f"&{api_param}="+",".join(value_list)
        else:
            value = get_params.get(field, "")
            if value != "":
                param_str = f"&{api_param}="+value
                all_values.append(value)

        # Join name=value pairs to request
        api_request_str += param_str

    if query_type == "basic":
        api_request_str = get_base_string(api_config, repository, endpoint, query_type, page_to_show)
        api_request_str += "&t=" + " ".join(all_values)
    else:
        api_request_str += "&organisation_fuzzy=1&occupation_fuzzy=1"
    return api_request_str


def get_result(repository, query):
    """ Requests a search result from the endpoint based on the supplied query.
        For testing purposes, 'use_dummy_result' can be set to True in the configuration which returns
        a local dummy result and does not actually query the endpoint"""

    # Return dummy result if option is activated
    if get_api_config()["use_dummy_result"]:
        return dummy_get_result_list(repository)

    # Query the endpoint
    try:
        # Timeouts: 2s until connection, 5s until result
        result = requests.get(query, timeout=(2, 5))
    except requests.exceptions.ConnectTimeout as e:
        return {"error": "The connection timed out"}
    except requests.exceptions.RequestException as e:
        return {"error": "Query could not be requested"}

    # If request was successful: load json object from it
    if result.status_code == 200:
        try:
            json_obj = json.loads(result.text)
            return json_obj
        except json.JSONDecodeError:
            return {"error": "Result could not be loaded"}
    else:
        return {"error": f"The server returned status code: {result.status_code}"}


def dummy_get_result_list(repository):
    """ Composes a dummy result from a dummy result file which contains a mock up data result. This single gets loaded
        as many times to fill a single page (the page size is set in the configuration) and the result object is
        enhanced with result metadata (such as number of results etc.) """

    api_config = get_api_config()
    base_dummy_result = {
        "total": int(api_config["page_size"]),
        "page": 1,
        "size": int(api_config["page_size"]),
        "links": {
            "prev": None,
            "next": None,
            "self": ""
        },
        "hits": []
    }
    if api_config["repositories"][repository]["dummy_result_file"] is not None:
        with open(os.path.join(settings.STATIC_ROOT, api_config["repositories"][repository]["dummy_result_file"])) as f:
            dummy_search_line = json.load(f)
            for i in range(int(api_config["page_size"])):
                base_dummy_result["hits"].append(dummy_search_line)
            return base_dummy_result
    else:
        return base_dummy_result


def compose_id_query(record_id):
    """Composes and returns an id query"""
    api_config = get_api_config()
    query = get_base_string(api_config, "asiadir", "query", "id", page=0) + f"?id={record_id}"
    return query


def get_id_result(query):
    return get_result("asiadir", query)
