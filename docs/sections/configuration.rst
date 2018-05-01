.. This work is licensed under a Creative Commons Attribution 4.0 International License.

Configuration
=============================================

For the configuration inside the config-file, please refer to the README inside Gerrit  

It is worth noting that A&AI and MUSIC may be needed to run HAS project. Please refer to their setup page for installation.

For MUSIC version 2.4.x and newer refer Setup for Developing MUSIC

Running the example
-----------------------
To start the process, execute the following commands:
    
    $ conductor-api --port=8091 -- --config-file={conductor_conf_file_location} 
    
    $ conductor-controller --config-file={conductor_conf_file_location}
    
    $ conductor-solver --config-file={conductor_conf_file_location}
    
    $ conductor-reservation --config-file={conductor_conf_file_location}
    
    $ conductor-data --config-file={conductor_conf_file_location}

Committing the Code
-----------------------    
    $ git commit -am "Initial proj struct"
    
    $ git review -s
    
    $ git commit -as --amend

# scroll down 2 lines (above your Change-ID) insert "Issue-ID: {issue_id}"
    
    $ git review
