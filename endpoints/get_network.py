# encoding: utf-8

from server import pugdagd_client


async def get_network():
    """
    Get some global pugdag network information
    """
    resp = await pugdagd_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
