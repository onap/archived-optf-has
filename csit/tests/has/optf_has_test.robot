*** Settings ***
Library       OperatingSystem
Library       RequestsLibrary
Library       json

*** Variables ***
${MESSAGE}    {"ping": "ok"}
${BASIC}    Basic
${Music_AUTHVALUE}    Y29uZHVjdG9yOmMwbmR1Y3Qwcg==
${HAS_AUTHVALUE}    YWRtaW4xOnBsYW4uMTU=
${Music_Auth}    ${BASIC} ${Music_AUTHVALUE}
${HAS_Auth}    ${BASIC} ${HAS_AUTHVALUE}
${RESP_STATUS}     "error"
${RESP_MESSAGE_WRONG_VERSION}    "conductor_template_version must be one of: 2016-11-01"
${RESP_MESSAGE_WITHOUT_DEMANDS}    Undefined Demand

#global variables
${generatedPlanId}
${generatedAID}
${resultStatus}

*** Test Cases ***

Check ConductorApi Docker Container
    [Documentation]    It checks conductor-api docker container is running
    ${rc}    ${output}=    Run and Return RC and Output    docker ps
    Log To Console              *********************
    Log To Console              retrurn_code = ${rc}
    Log To Console              output = ${output}
    Should Be Equal As Integers    ${rc}    0
    Should Contain    ${output}    cond-api

Check ConductorController Docker Container
    [Documentation]    It checks conductor-controller docker container is running
    ${rc}    ${output}=    Run and Return RC and Output    docker ps
    Log To Console              *********************
    Log To Console              retrurn_code = ${rc}
    Log To Console              output = ${output}
    Should Be Equal As Integers    ${rc}    0
    Should Contain    ${output}    cond-cont

Check ConductorSolver Docker Container
    [Documentation]    It checks conductor-solver docker container is running
    ${rc}    ${output}=    Run and Return RC and Output    docker ps
    Log To Console              *********************
    Log To Console              retrurn_code = ${rc}
    Log To Console              output = ${output}
    Should Be Equal As Integers    ${rc}    0
    Should Contain    ${output}    cond-solv

Check ConductorReservation Docker Container
    [Documentation]    It checks conductor-reservation docker container is running
    ${rc}    ${output}=    Run and Return RC and Output    docker ps
    Log To Console              *********************
    Log To Console              retrurn_code = ${rc}
    Log To Console              output = ${output}
    Should Be Equal As Integers    ${rc}    0
    Should Contain    ${output}    cond-resv

Check ConductorData Docker Container
    [Documentation]    It checks conductor-data docker container is running
    ${rc}    ${output}=    Run and Return RC and Output    docker ps
    Log To Console              *********************
    Log To Console              retrurn_code = ${rc}
    Log To Console              output = ${output}
    Should Be Equal As Integers    ${rc}    0
    Should Contain    ${output}    cond-data

Get Root Url
    [Documentation]    It sends a REST GET request to root url
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Sleep    10s    Wait For 10 seconds

Healthcheck
    [Documentation]    It sends a REST GET request to healthcheck url
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/healthcheck     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200

SendPlanWithWrongVersion
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_wrong_version.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    10s    Wait Plan Resolution

GetPlanWithWrongVersion
    [Documentation]    It sends a REST GET request to capture error
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    error    ${resultStatus}

SendPlanWithoutDemandSection
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_without_demand_section.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    10s    Wait Plan Resolution

GetPlanWithoutDemandSection
    [Documentation]    It sends a REST GET request to capture error
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    error    ${resultStatus}

SendPlanWithWrongConstraint
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_wrong_distance_constraint.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    10s    Wait Plan Resolution

GetPlanWithWrongConstraint
    [Documentation]    It sends a REST GET request to capture error
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    error    ${resultStatus}


SendPlanWithLatiAndLongi
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_lati_and_longi.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithLatiAndLongi
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}

SendPlanWithShortDistanceConstraint
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_short_distance_constraint.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithShortDistanceConstraint
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    not found    ${resultStatus}

SendPlanWithVimFit
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_vim_fit.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithVimFit
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}

SendPlanWithHpa
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_hpa.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithHpa
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}

SendPlanWithHpaSimple
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_hpa_simple.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithHpaSimple
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}

SendPlanWithHpaMandatory
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_hpa_requirements_mandatory.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithHpaMandatory
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}

SendPlanWithHpaOptionals
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_hpa_requirements_optionals.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithHpaOptionals
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}

SendPlanWithHpaUnmatched
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_hpa_unmatched.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithHpaUnmatched
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    not found    ${resultStatus}

# HPA Score Multi objective Optimization
SendPlanWithHpaScoreMultiObj
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}plan_with_hpa_score_multi_objective.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithHpaScoreMultiObj
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    ${vim-id}=    Convert To String      ${response_json['plans'][0]['recommendations'][0]['vG']['candidate']['vim-id']}
    # ${hpa_score}=    Convert To String      ${response_json['plans'][0]['recommendations']['vG']['hpa_score']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}
    Should Be Equal    HPA-cloud_cloud-region-1    ${vim-id}

# NSI selection template
SendPlanWithNsiSelection
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}nsi_selection_template_with_reuse.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithNsiSelection
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    ${instance_name}=    Convert To String      ${response_json['plans'][0]['recommendations'][0]['URLLC']['candidate']['instance_name']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}
    Should Be Equal    nsi_test_0211    ${instance_name}

SendPlanWithNsiSelectionSliceProfile
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}nsi_selection_template_with_create.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithNsiSelectionSliceProfile
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    ${candidate_type}=    Convert To String      ${response_json['plans'][0]['recommendations'][0]['URLLC']['candidate']['inventory_type']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}
    Should Be Equal    slice_profiles    ${candidate_type}

SendPlanWithNoNsi
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}nsi_selection_template_with_nonsi.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithNoNsi
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    ${candidate_type}=    Convert To String      ${response_json['plans'][0]['recommendations'][0]['URLLC']['candidate']['inventory_type']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}
    Should Be Equal    slice_profiles    ${candidate_type}

SendPlanWithNssiSelection
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}nssi_selection_template.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithNssiSelection
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    ${instance_name}=    Convert To String      ${response_json['plans'][0]['recommendations'][0]['URLLC_core']['candidate']['instance_name']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}
    Should Be Equal    nssi_test_0211    ${instance_name}

SendPlanWithNssiSelectionUnmatched
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}nssi_selection_template_unmatched.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithNssiSelectionUnmatched
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    not found    ${resultStatus}

# NST selection template
SendPlanWithNSTSelection
    [Documentation]    It sends a POST request to conductor
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    ${data}=         Get Binary File     ${CURDIR}${/}data${/}nst_selection_template.json
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Post Request        optf-cond   /v1/plans     data=${data}     headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    Log To Console              body = ${resp.text}
    ${response_json}    json.loads    ${resp.content}
    ${generatedPlanId}=    Convert To String      ${response_json['id']}
    Set Global Variable     ${generatedPlanId}
    Log To Console              generatedPlanId = ${generatedPlanId}
    Should Be Equal As Integers    ${resp.status_code}    201
    Sleep    60s    Wait Plan Resolution

GetPlanWithNsTSelection
    [Documentation]    It sends a REST GET request to capture recommendations
    Create Session   optf-cond            ${COND_HOSTNAME}:${COND_PORT}
    &{headers}=      Create Dictionary    Authorization=${HAS_Auth}    Content-Type=application/json  Accept=application/json
    ${resp}=         Get Request        optf-cond   /v1/plans/${generatedPlanId}    headers=${headers}
    Log To Console              *********************
    Log To Console              response = ${resp}
    ${response_json}    json.loads    ${resp.content}
    ${resultStatus}=    Convert To String      ${response_json['plans'][0]['status']}
    ${instance_name}=    Convert To String      ${response_json['plans'][0]['recommendations'][0]['nst_demand']['candidate']['model_name']}
    Set Global Variable     ${resultStatus}
    Log To Console              resultStatus = ${resultStatus}
    Log To Console              body = ${resp.text}
    Should Be Equal As Integers    ${resp.status_code}    200
    Should Be Equal    done    ${resultStatus}
    Should Be Equal    EmbbNst    ${instance_name}


*** Keywords ***


