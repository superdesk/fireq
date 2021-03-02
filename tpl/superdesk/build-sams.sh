if [ `_get_json_value sams` == "true" ]; then
    ## clone SAMS repo
    [ -d {{repo}}/sams ] || (
        mkdir -p {{repo}}
        cd {{repo}}

        github=git@github.com:superdesk
        git clone -b develop --single-branch $github/sams.git sams
        unset github
    )

    ## server part
    cd {{repo}}/sams/src/server
    time pip install -e .

    ## client part
    cd {{repo}}/sams/src/clients/python
    time pip install -e .
fi
