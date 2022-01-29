def parse_stream(output):
    parsed_output = dict()

    if output['output_type'] == "stream":
        parsed_output['stdout'] = ''.join(output['text'])
    else:
        parsed_output = None

    return parsed_output
