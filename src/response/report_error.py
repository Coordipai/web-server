import httpx


async def report_error_to_discord(
    discord_channel_id: str,
    trace_id: str,
    type: str,
    title: str,
    status: int,
    detail: str,
    instance: str,
    method: str,
    trace: str,
) -> None:
    url = "https://errorping.jhssong.com/report-error"
    payload = {
        "discordChannelId": discord_channel_id,
        "error": {
            "traceId": trace_id,
            "type": type,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
            "method": method,
        },
        "trace": trace,
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload)

        if res.status_code != 200:
            print(f"Failed to report error: {res.status_code} - {res.text}")
