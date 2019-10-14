import traceback
from splunk import Intersplunk

import actconfig

def fact_search(client, **kwargs):
    result = []
    for fact in client.fact_search(**kwargs):
        event = {
            "fact_type": fact.type.name,
            "fact_value": fact.value
        }

        if fact.source_object:
            event["source_object_type"] = fact.source_object.type.name
            event["source_object_value"] = fact.source_object.value

        if fact.destination_object:
            event["dest_object_type"] = fact.destination_object.type.name
            event["dest_object_value"] = fact.destination_object.value

        if fact.bidirectional_binding:
            event["bidirectional_binding"] = "true"

        result.append(event)

    return result


def main():
    client = actconfig.setup()

    # Parse arguments from splunk search
    opts, kwargs = Intersplunk.getKeywordsAndOptions()

    results = []

    if opts and "keywords" not in kwargs:
        kwargs["keywords"] = " ".join(opts)

    results += fact_search(client, **kwargs)
    Intersplunk.outputResults(results)


try:
    main()
except Exception as e:
    Intersplunk.parseError(traceback.format_exc())
