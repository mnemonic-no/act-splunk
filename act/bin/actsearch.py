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

        for obj in fact.objects:
            if obj.direction == "FactIsDestination":
                event["source_object_type"] = obj.type.name
                event["source_object_value"] = obj.value
            elif obj.direction == "FactIsSource":
                event["dest_object_type"] = obj.type.name
                event["dest_object_value"] = obj.value
            elif (not obj.direction) or obj.direction == "BiDiractional":
                if "source_object_type" not in event:
                    event["source_object_type"] = obj.type.name
                    event["source_object_value"] = obj.value
                else:
                    event["dest_object_type"] = obj.type.name
                    event["dest_object_value"] = obj.value

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
