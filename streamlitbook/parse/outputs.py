def parse_stream(output):
    parsed_output = dict()

    if output['output_type'] == "stream":
        parsed_output['stdout'] = ''.join(output['text'])
    else:
        parsed_output = None

    return parsed_output


def parse_plotly_output(output):
    parsed_output = dict()

    # If output type is either display_data or execute_result, the output is media type
    if output['output_type'] in ("display_data", "execute_result"):
        # If the below key exists, the output is Plotly figure
        if "application/vnd.plotly.v1+json" in output['data'].keys():
            plotly_data = output['data']['application/vnd.plotly.v1+json']['data']
            plotly_layout = output['data']['application/vnd.plotly.v1+json']['layout']

            # If config key exists in Plotly output dict,
            # user passed custom config to the chart
            if "config" in output['data']['application/vnd.plotly.v1+json'].keys():
                plotly_config = output['data']['application/vnd.plotly.v1+json']['config']
            else:
                plotly_config = None

            # Combine all parts for a Plotly output
            parsed_output["plotly_fig"] = {"data": plotly_data,
                                           "layout": plotly_layout,
                                           "config": plotly_config}
    else:
        parsed_output = None

    return parsed_output
