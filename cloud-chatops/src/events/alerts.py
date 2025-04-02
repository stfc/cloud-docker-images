from slack_sdk import WebClient
from helper.read_config import get_token

def post_alert(content):
    client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
    kwargs = {"text": content, "channel": "C08L77UBBAS", "unfurl_links": False}
    client.chat_postMessage(**kwargs)


