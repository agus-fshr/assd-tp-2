import mido

def MetaMessageParser(track):
    track_data = {}
    
    ticks = 0
    refChannels = []
    for msg in track:
        ticks += msg.time

        # if "channel" is in msg, add it to refChannels
        if hasattr(msg, "channel"):
            if msg.channel not in refChannels:
                refChannels.append(msg.channel)

        if isinstance(msg, mido.MetaMessage):
            msg = msg.dict()
            t = msg["type"]

            if t == "track_name":
                track_data["name"] = msg["name"]
                        
            elif t == "midi_port":
                track_data["port"] = msg["port"]

            elif t == "channel_prefix":
                track_data["channel_prefix"] = msg["channel"]
    track_data["ticks"] = ticks
    track_data["refChannels"] = refChannels
    return track_data