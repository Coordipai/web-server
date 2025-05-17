import httpx


async def report_error(
    discord_channel_id: str,
    traceId: str,
    type: str,
    title: str,
    status: int,
    detail: str,
    instance: str,
    method: str,
) -> None:
    url = "https://errorping.jhssong.com/report-error"
    payload = {
        "discordChannelId": discord_channel_id,
        "error": {
            "traceId": traceId,
            "type": type,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
            "method": method,
        },
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)

        if res.status_code != 200:
            print(f"Failed to report error: {res.status_code} - {res.text}")
