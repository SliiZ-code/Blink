import re
def srtToJson(filePath):
    regex = r'(?:\d+)\s(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\s+(.+?)(?:\n\n|$)'
    offset_seconds = lambda ts: sum(howmany * sec for howmany, sec in zip(map(int, ts.replace(',', ':').split(':')), [60 * 60, 60, 1, 1e-3]))

    transcript = [dict(startTime = offset_seconds(startTime), endTime = offset_seconds(endTime), text = ' '.join(text.split())) for startTime, endTime, text in re.findall(regex, open(filePath).read(), re.DOTALL)]

    return(transcript)