# callernotes-server
CallerNotes Server

This is the server component for CallerNotes.  It is meant to be run along side your PBX or on a seperate machine.

CallerNote desktop clients connect to this server and recieve real time call notifications on call events usually triggered by your PBX.

Data for the CallerNote's server is stored in a CouchDB instance that is specified in the callernotes.cfg file.

Caller ID information is retrived from either NextCaller directly or any of the other datasources in the Twilio AddOn capalog including Nextcaller.
To specify which datasource to use, set it in the callernotes.cfg file along with your other settings.

For more information on CallerNotes, check out our website at http://callernotesapp.com
