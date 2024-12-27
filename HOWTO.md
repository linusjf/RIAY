# HOWTO

<!-- vim-markdown-toc GFM -->

* [Prerequisites](#prerequisites)
* [Add the daily Youtube video](#add-the-daily-youtube-video)
* [Add today's sharing](#add-todays-sharing)
* [Generate markdown for Youtube video](#generate-markdown-for-youtube-video)
* [Merge monthly markdown files into one large README](#merge-monthly-markdown-files-into-one-large-readme)

<!-- vim-markdown-toc -->

## Prerequisites

- [curl](https://curl.se/)
- [gm](http://www.graphicsmagick.org/)
- [m4](https://www.gnu.org/software/m4/)
- [markdown-toc](https://github.com/jonschlinkert/markdown-toc)
- [stitchmd](https://github.com/abhinav/stitchmd)

Create a directory for each month of the year under the root directory.
Add a `header.md` file under each monthly directory with the following content.

Example for January:

```text
<!-- toc -->
# January 2025 #

RIAY January 2025
```

The `<!-- toc -->` comment header is mandatory else markdown-toc will not generate the table of contents
for the monthly markdown (in this case, `January2025.md`).

You can replace the top-level markdown header

```markdown
# January 2025

BIAY January 2025
```

with your own if you wish.

Add a `compact.txt` file with the first line as `header.md` under each monthly directory.
This ensures that the header is present for each month's markdown.

## Add the daily Youtube video

Execute the script `addvideo` with the following parameters:

- video id - the id of the youtube video
- caption or title (in double quotes)

Example:

```bash
./addvideo 5I2BbalTOPo "Hagar and Ishmael"
```

Results:

1. The day is generated from the length of the videos.txt file. The day is the number of lines in the file + 1.
   In this case, 10.
2. Video id is appended to the `videos.txt` file in the root directory.
3. `Day010.md` is generated in the January subdirectory.
4. `Day010.jpg` image is generated in the `January/jpgs` directory.
5. `Day010.md` file name is appended to the `January/compact.txt` file.
6. `January20XX.md` file is updated (in the root directory) with the `Day010.md` contents.

## Add today's sharing

1. First, add today's video.
2. Edit the generated `Dayxxx.md` file for today.
3. Paste the sharing text into the file adding appropriate markdown headers as needed.
4. Save the file.
5. Execute script `genmonth` with the following parameters:

- month index - 1 - 12

- four digit year - 20XX

  Example:

  ```bash
  ./genmonth 01 2025
  ```

  Results:

  The `January2025.md` file is updated with the sharing text added to the `Day010.md` file.

You can add sharing to other days as well in a similar fashion.
Don't forget to execute `genmonth` with the appropriate month index for that day.

You can obtain the month index by executing the following bash command:

```bash
date --date="$(date --date='jan 1 + 30 days' '+%B %d,      %Y')" +%m
```

The day of year has to be decremented by 1 and substituted in the command.
The above gives the month index for day 31.

## Generate markdown for Youtube video

Execute the `genvidmd` script with the following parameters:

- vid - video id
- caption - video title
- pathtoimg - relative path to jpeg image file to be generated

Example:

```bash
./genvidmd g7o7WjQc3as "Bringing the Bible back to Catholics" January/jpgs/bringingback.jpg
```

Results:

1. The markdown is generated on the command line. This can be used to insert video markdown in your markdown files.
2. The overlaid image file for the video is generated as `January/jpgs/bringingback.jpg`.

## Merge monthly markdown files into one large README

1. Edit the `stitch.md` file provided to include the markdown files you wish to merge.

2. The file format is as follows:

   ```markdown
   # README

   - [BIAY](redme.md)
   - [January 2025](January2025.md)
   - [February 2025](February2025.md)
   - [March 2025](March2025.md)
   - [April 2025](April2025.md)
   - [May 2025](May2025.md)
   - [June 2025](June2025.md)
   - [July 2025](July2025.md)
   - [August 2025](August2025.md)
   - [September 2025](September2025.md)
   - [October 2025](October2025.md)
   - [November 2025](November2025.md)
   - [December 2025](December2025.md)
   ```

   Include or exclude any files you need or don't need.

3. Execute the `stitch` script.

```bash
./stitch
```

Results:

A huge README is generated with all the contents of the listed markdown files in `stitch.md`.
