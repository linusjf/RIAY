# TODOs

## Features

1. Add script addsummaryimagestodays.
1. Add unit tests using BATS.
1. Integrate artdb into artdownloader.py
   1.1 Add function to embedarttoday to check if image is from stock image website
   1.2 Remember to save url to {file_basename}.url.txt to enable above.

## Bugs/Issues

1. Update documentation.
   1.1 Document every script in its matching markdown file.
1. Optimize code where possible.
   1.1 Make downloads multi-threaded.
1. Refactor.
   1.1 Convert requests to httpx
   1.2 Convert python scripts to async
   1.3 Create configurator object for httpx retry logic using values from config.env
1. Use augmented art details to search especially Wiki in original language of artwork title. (Better results/matches?)
   1.1 Search using original_title and language on wikis.
   1.2 Use original_title to search for images on google and duckduckgo. (2 separate searches or integrated?)
1. Fix for wikimedia site down. Right now, hangs.

## Exploratory task

1. Related links feature.
