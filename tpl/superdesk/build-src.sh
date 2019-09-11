{{^develop}}
{{>build-src-repo.sh}}
{{/develop}}
{{#develop}}
{{>build-src-cores.sh}}
{{/develop}}
