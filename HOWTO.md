# HOWTO

<!-- toc -->

- [Prerequisites](#prerequisites)
- [Add the daily Youtube video](#add-the-daily-youtube-video)
- [Add today's sharing](#add-todays-sharing)
- [Generate markdown for Youtube video](#generate-markdown-for-youtube-video)
- [Merge monthly markdown files into one large README](#merge-monthly-markdown-files-into-one-large-readme)
- [Generate table of contents for markdown file(s)](#generate-table-of-contents-for-markdown-files)

<!-- tocstop -->

## Prerequisites

- [curl](https://curl.se/)
- [gm](http://www.graphicsmagick.org/)
- [m4](https://www.gnu.org/software/m4/)
- [markdown-toc](https://github.com/jonschlinkert/markdown-toc)
- [stitchmd](https://github.com/abhinav/stitchmd)
- [markdown-toc-gen](https://github.com/thesilk-tux/markdown-toc-gen)
- [mdformat](https://github.com/hukkin/mdformat)
- [mdl](https://github.com/markdownlint/markdownlint)

1. Create an empty `videos.txt` file under the root directory.
2. Create a directory for each month of the year under the root directory.
3. Add a `header.md` file under each monthly directory with the following content.
4. Export an environment variable `GIT_USER` by adding the following line to your `.bash_profile` file.
```
export GIT_USER="<userid>"
```
   Substitute your Github user id for <userid>.

Example for January:

```markdown
<!-- toc -->

# January 2025

RIAY January 2025
```

The `<!-- toc -->` comment header is mandatory else markdown-toc will not generate the table of contents
for the monthly markdown (in this case, `January2025.md`).

You can replace the top-level markdown header

```markdown
# January 2025

RIAY January 2025
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

1.  The day is generated from the length of the videos.txt file. The day is the number of lines in the file + 1.
    In this case, 10.
2.  Video id is appended to the `videos.txt` file in the root directory.
3.  `Day010.md` is generated in the January subdirectory.
4.  `Day010.jpg` image is generated in the `January/jpgs` directory.
5.  `Day010.md` file name is appended to the `January/compact.txt` file.
6.  `January20XX.md` file is updated (in the root directory) with the `Day010.md` contents.

## Add today's sharing

1.  First, add today's video.
2.  Edit the generated `Dayxxx.md` file for today.
3.  Paste the sharing text into the file adding appropriate markdown headers as needed.
4.  Save the file.
5.  Execute script `genmonth` with the following parameters:

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

1.  The markdown is generated on the command line. This can be used to insert video markdown in your markdown files.
2.  The overlaid image file for the video is generated as `January/jpgs/bringingback.jpg`.

## Merge monthly markdown files into one large README

1.  Edit the `stitch.md` file provided to include the markdown files you wish to merge.

2.  The file format is as follows:

    ```markdown
    # README

    - [RIAY](redme.md)
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

3.  Execute the `stitch` script.

```bash
./stitch
```

Results:

A huge README is generated with all the contents of the listed markdown files in `stitch.md`.

## Generate table of contents for markdown file(s)

Execute the `gentoc` script as follows:

```bash
./gentoc <path to markdown file>
```

Before executing the script, update the file and place the comment `<!-- toc -->` and `<!-- tocstop -->` where you want the table of contents to be generated.

Results:

The table of contents will be generated as per the existing headings in the markdown file.

## Using the commands utility that accepts text commands in file `commands.txt`

1. Install ANTLR4

Assuming that you have Python3 and its installer pip3 installed on your machine.
You can download and install Python3 from <https://www.python.org/downloads/>.

```bash
pip install antlr4-tools antlr4-python3-runtime
```
2. Add commands to the `commands.txt` file.

The commands available are:
- addvideo
- genmonth
- lintall
- genvidmd

For simplicity and consistency, the commands are the command line equivalents above. They are wrappers around the existing
command line scripts.

3. Execute the commands.py script.
```
./commands.py
```
This will execute the commands in the `commands.txt` file.

Commands are executed in sequence as placed in the file `commands.txt`. If any command fails, the program outputs an error message for that command and the subsequent commands (if any) are executed.

4. Sample commands.txt
```
# Sample commands
addvideo "abc123456" "Sample video" # add sample video
genmonth 01 2025 # generate markdown for month January, 2025
genvidmd "abc123456" "Sample video" "February/jpgs/samplevideo.jpg" # generate markdown for video including jpeg image
lintall # lint all the markdown files
```

Everything after the `#` symbol is a comment and ignored by the program.
