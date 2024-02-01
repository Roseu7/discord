import re

def extract_user_mentions(text):
    pattern = r"<@(!?\d+)>"
    mentions = re.findall(pattern, text)
    return [f"<@{mention}>" for mention in mentions]

def find_related_user(message, links):
    user_mentions = extract_user_mentions(message.content)
    return_mention = []
    for mention in user_mentions:
        for link_pair in links:
            try:
                index = link_pair.index(mention)
                if index == 0:
                    return_mention.append(link_pair[1])
                elif index == 1:
                    return_mention.append(link_pair[0])
            except:
                pass
    return return_mention