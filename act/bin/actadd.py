import traceback

import actconfig
from splunk import Intersplunk


def fact_search(client, object_value, **kwargs):
    event = {}

    for fact in client.fact_search(object_value=object_value, **kwargs):
        heading = fact.type.name

        for obj in [fact.source_object, fact.destination_object]:
            if not obj:
                continue

            value = obj.value
            if fact.value and fact.value != "-":
                # Append fact value if it is set
                fact_value = ":{}".format(fact.value)
            else:
                fact_value = ""

            field = "{}{}".format(heading, fact_value)

            if obj.value not in object_value:
                event[field] = event.get(field, []) + [value]

    return event


def main():
    client = actconfig.setup()

    # Parse arguments
    opts, kwargs = Intersplunk.getKeywordsAndOptions()

    if not opts:
        Intersplunk.generateErrorResult(
            "Usage: | actadd <field1> ... <fieldN> [fact_type=<fact type>] [fact_value=<fact value]")
        return

    events, _, _ = Intersplunk.getOrganizedResults()

    # Annotate events
    for event in events:
        object_value = []
        for field in opts:
            if event.get(field):
                object_value.append(event[field])

        if not object_value:
            continue

        event.update(fact_search(client, object_value, **kwargs))

    Intersplunk.outputResults(events)


try:
    main()
except Exception as e:
    Intersplunk.parseError(traceback.format_exc())
