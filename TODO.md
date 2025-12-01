# TODOs

## Features

1. Add script addsummaryimagestodays.
1. Add unit tests using BATS.

## Bugs/Issues

1. Update documentation.
   1.1 Document every script in its matching markdown file.
1. Optimize code where possible.
   1.1 Make downloads multi-threaded.
1. Refactor.
   1.1 Convert requests to httpx
   1.2 Convert python scripts to async
   1.3 Create configurator object for httpx retry logic using values from config.env
1. Fix for wikimedia site down. Right now, hangs.
1. Migrate long, complex bash scripts to python.
   1.1 Migrate embedarttoday to python.
1. Append day number to AI-generated summary title to ensure uniqueness within markdown README.
1. Support open ai transcription models. Current one only support whisper from deepinfra.

## Exploratory task

1. Feature to convert AI-generated summary to audio file.
