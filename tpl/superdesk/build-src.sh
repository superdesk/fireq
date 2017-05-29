{{^develop}}
{{>build-src-repo.sh}}
{{/develop}}
{{#develop}}
{{>build-src-cores.sh}}

cd {{repo}}/client-core
time npm link
{{/develop}}
