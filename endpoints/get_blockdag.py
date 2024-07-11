# encoding: utf-8

from server import pugdagd_client


async def get_blockdag():
    """
    Get some global Pugdag BlockDAG information
    """
    resp = await pugdagd_client.request("getBlockDagInfoRequest")
    return resp["getBlockDagInfoResponse"]
