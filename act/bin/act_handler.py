import splunk.admin as admin

# If no default value is specified, use ""
fields = {
    "www_url": {},
    "api_url": {},
    "api_proxy": {},
    "act_userid": {"default": 0},
    "api_http_user": {},
    "api_http_password": {},
}

class ConfigApp(admin.MConfigHandler):
    '''
    Set up supported arguments
    '''

    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for field in fields:
                self.supportedArgs.addOptArg(field)

    '''
    Read the initial values of the parameters from the custom file
    act.conf, and write them to the setup page.

    If the app has never been set up,
    use .../app_name/default/act.conf.

    If app has been set up, looks at
    .../local/act.conf first, then looks at
    .../default/act.conf only if there is no value for a field in
    .../local/act.conf

    For text fields, if the conf file says None, set to the empty string.
    '''

    def process_workflow(self):
        """
        Update local/workflow_actions.conf with config applied to templates
        """
        if self.requestedAction == admin.ACTION_EDIT:
            for field in fields:
                self.supportedArgs.addOptArg(field)

        config = self.readConf("act")["config"]
        www_url = config.get("www_url")

        for entity, template in self.readConf("workflow_actions_template").iteritems():
            workflow = {}

            if template.get("label"):
                workflow["label"]= template["label"]
            else:
                # Construct label automatically
                workflow["label"]= "ACT: Search {act_field} for ${fields}$".format(**template)

            template["www_url"] = www_url
            workflow["link.uri"] = template["uri"].format(**template)
            workflow["fields"] = template["fields"]
            self.writeConf('workflow_actions', entity, workflow)

    def handleList(self, confInfo):
        confDict = self.readConf("act")
        if confDict is not None:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if not val:
                        val = fields[key].get("default", "")
                    confInfo[stanza].append(key, val)

    def handleEdit(self, confInfo):
        '''
        After user clicks Save on setup page, take updated parameters,
        normalize them, and save them somewhere
        '''

        name = self.callerArgs.id
        args = self.callerArgs

        for field in fields:
            if not self.callerArgs.data[field][0]:
                self.callerArgs.data[field][0] = fields[field].get("default", "")

        '''
        Since we are using a conf file to store parameters,
        write them to the [config] stanza in act/local/act.conf
        '''

        self.writeConf('act', 'config', self.callerArgs.data)

        # Update workflow from template
        self.process_workflow()

# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
