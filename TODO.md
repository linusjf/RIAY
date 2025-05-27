# TODOs

## Features

1. Use a local LLM.
1. Add script addsummaryimagestodays.
1. Add unit tests using BATS.

## Bugs/Issues

1. Identify and refactor scripts to clean up intermediate, temporary and backup files created on normal exit and error.
1. Identify cause of intermittent failure in summarizevideo.
1. Add logic to summarize video to check if caption file already exists. If yes, skip downloading the captions by default. This can be overwritten by an additional command line option to redownload, if necessary. Unlikely, since auto-generated captions don't change. Only reason to do so would be if subititles were added by the video creator. Are Ascension likely to do so?
