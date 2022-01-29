def _parse_stream_output(output):
    parsed_output = dict()

    if output['output_type'] == "stream":
        parsed_output['stdout'] = ''.join(output['text'])
    else:
        parsed_output = None

    return parsed_output


def _parse_plotly_output(output):
    parsed_output = dict()

    # If output type is either display_data or execute_result, the output is media type
    if output['output_type'] in ("display_data", "execute_result"):
        # If the below key exists, the output is Plotly figure
        plotly_key = "application/vnd.plotly.v1+json"
        if plotly_key in output['data'].keys():
            plotly_data = output['data'][plotly_key]['data']
            plotly_layout = output['data'][plotly_key]['layout']

            # If config key exists in Plotly output dict,
            # user passed custom config to the chart
            if "config" in output['data'][plotly_key].keys():
                plotly_config = output['data'][plotly_key]['config']
            else:
                plotly_config = None

            # Combine all parts for a Plotly output
            parsed_output["plotly_fig"] = {"data": plotly_data,
                                           "layout": plotly_layout,
                                           "config": plotly_config}
    else:
        parsed_output = None

    return parsed_output


def _parse_html_output(output):
    parsed_output = dict()

    if output['output_type'] in ("display_data", "execute_result"):
        if "text/html" in output['data'].keys():
            parsed_output['text/html'] = ''.join(output['data']['text/html'])
        else:
            parsed_output = None
    else:
        parsed_output = None

    return parsed_output


def _parse_image_output(output):
    parsed_output = dict()

    if output['output_type'] in ("display_data", "execute_result"):
        if "image/png" in output['data'].keys():
            parsed_output['image/png'] = output['data']['image/png'].strip()
        else:
            parsed_output = None
    else:
        parsed_output = None

    return parsed_output


def _parse_plain_text_output(output):
    parsed_output = dict()

    if output['output_type'] in ("display_data", "execute_result"):
        if ("text/plain" in output['data'].keys()) and \
                ("text/html" not in output['data'].keys()):
            parsed_output['text/plain'] = ''.join(output['data']['text/plain'])
        else:
            parsed_output = None
    else:
        parsed_output = None

    return parsed_output


def _parse_error_output(output):
    parsed_output = dict()

    if output['output_type'] == "error":
        parsed_output['error'] = output['ename']
    else:
        parsed_output = None

    return parsed_output
