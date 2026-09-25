import requests as r


def _get_response() -> r.Response:
    """
    Makes a request to the ZenQuotes API for a random quote
    """
    url = "https://zenquotes.io/api/random"
    # Try except for http timeout
    response: r.Response = r.get(url)
    return response


def _get_quote(response: r.Response) -> tuple[str, str]:
    """
    Format the ZenQuotes API response
    Args:
        response:
            requests response object containing the full api response
    Returns:
        tuple containing the quote and the author
    """
    json_response = response.json()[0]
    return json_response["q"], json_response["a"]
