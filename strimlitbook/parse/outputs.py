def _parse_stream_output(output):
    """
    Parse a text output of a code cell.
    The output_type in the notebook JSON is given as "stream".

    Parameters
    ----------
    output : dict
        A single code cell output as a dictionary.

    Returns
    -------
        parsed_output : dict
            A dictionary containing the parsed output with "stdout" key.

    Notes
    -----
        The difference between this function and _parse_plain_text_output is that this
        function only parses outputs of the Python print function.
        While _parse_plain_text_output parses all text outputs from executing the code
        cell by running Shift + Enter or Ctrl + Enter commands.
    """
    parsed_output = dict()

    if output['output_type'] == "stream":
        parsed_output['stdout'] = ''.join(output['text'])
    else:
        parsed_output = None

    return parsed_output


def _parse_plotly_output(output):
    """
    Parse a Plotly HTML code of a code cell.
    The output_type in the notebook JSON is given as "application/vnd.plotly.v1+json"
    under the "data" key.

    Parameters
    ----------
    output : dict
        A single code cell output as a dictionary.
        

    Returns
    -------
        parsed_output : dict
            A dictionary containing the parsed output with a dictionary of data,
            layout, and config items under the "plotly_fig" key.
    """
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
    """
    Parse HTML of a code cell. The output_type in the notebook JSON is given as
    "text/html" under the "data" key.

    Parameters
    ----------
    output : dict
        A single code cell output as a dictionary.

    Returns
    -------
        parsed_output : dict
            A dictionary containing the parsed output with "text/html" key.
    """
    parsed_output = dict()
    plotly_key = "application/vnd.plotly.v1+json"

    if output['output_type'] in ("display_data", "execute_result"):
        if ("text/html" in output['data'].keys()) and \
                (plotly_key not in output['data'].keys()):
            parsed_output['text/html'] = ''.join(output['data']['text/html'])
        else:
            parsed_output = None
    else:
        parsed_output = None

    return parsed_output


def _parse_image_output(output):
    """
    Parse binary image data of a code cell. The output_type in the notebook JSON is given
    as "image/png" under the "data" key.

    Parameters
    ----------
    output : dict
        A single code cell output as a dictionary.

    Returns
    -------
        parsed_output : dict
            A dictionary containing the parsed output with "image/png" key.
    """
    parsed_output = dict()
    plotly_key = "application/vnd.plotly.v1+json"

    if (output['output_type'] in ("display_data", "execute_result")) and \
            (plotly_key not in output['data'].keys()):
        if "image/png" in output['data'].keys():
            parsed_output['image/png'] = output['data']['image/png'].strip()
        else:
            parsed_output = None
    else:
        parsed_output = None

    return parsed_output


def _parse_plain_text_output(output):
    """
    Parse a text output of a code cell after it was run with Shift + Enter or Ctrl + Enter
    commands. See notes on the difference between _parse_stream_output and this function.
    The output_type in the notebook JSON is given as "text/plain".

    Parameters
    ----------
    output : dict
        A single code cell output as a dictionary.

    Returns
    -------
        parsed_output : dict
            A dictionary containing the parsed output with "text/plain" key.

    Notes
    -----
        The difference between this function and _parse_stream_output is that
        _parse_stream_output function only parses outputs of the Python print function.
        While this function parses all text outputs from executing the code
        cell by running Shift + Enter or Ctrl + Enter commands.
    """
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
    """
    Parse an error output of a code cell. The output_type in the notebook JSON is given as
    "error" and the error name is under "ename".

    Parameters
    ----------
    output : dict
        A single code cell output as a dictionary.

    Returns
    -------
        parsed_output : dict
            A dictionary containing the parsed output with "error" key.
    """
    parsed_output = dict()

    if output['output_type'] == "error":
        parsed_output['error'] = output['ename']
    else:
        parsed_output = None

    return parsed_output
