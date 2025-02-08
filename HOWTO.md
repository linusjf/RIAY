# HOWTO

<!-- toc -->

- [Prerequisites](#prerequisites)
- [Add the daily Youtube video](#add-the-daily-youtube-video)
- [Add today's sharing](#add-todays-sharing)
- [Generate markdown for Youtube video](#generate-markdown-for-youtube-video)
- [Merge monthly markdown files into one large README](#merge-monthly-markdown-files-into-one-large-readme)
- [Generate table of contents for markdown files](#generate-table-of-contents-for-markdown-files)
- [Using the commands utility that accepts text commands in file `commands.txt`](#using-the-commands-utility-that-accepts-text-commands-in-file-commandstxt)

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
- [vale](https://github.com/errata-ai/vale)

1. Create an empty `videos.txt` file under the root directory.
2. Create a directory for each month of the year under the root directory.
3. Add a `header.md` file under each monthly directory with the following content.
Example for January:

```markdown
<!-- toc -->

# January 2025

RIAY January 2025
```

`markdown-toc` won't generate the table of contents
for the monthly markdown (in this case, `January2025.md`) without the mandatory `<!-- toc -->` comment header.

You can replace the top-level markdown header

```markdown
# January 2025

RIAY January 2025
```

with your own if you wish.

Add a `compact.txt` file with the first line as `header.md` under each monthly directory.
This ensures the presence of the header for each month's markdown.

4. Export an environment variable `GIT_USER` by adding the following line to your `.bash_profile` file.
```
export GIT_USER="<userid>"
```
   Substitute your Github user id for `<userid>`.

5. Initialize `vale` styles by executing the command `vale sync`. This should download the specified styles in `.vale.ini`.

## Add the daily Youtube video

Execute the script `addvideo` with the following parameters:

- video id - the id of the Youtube video
- caption or title (in double quotes)

Example:

```bash
./addvideo 5I2BbalTOPo "Hagar and Ishmael"
```

Results:

1. Computes the `day of year` from the length of the videos.txt file.
`day of year = (number of lines in videos.txt) + 1`
    In this case, 10.
2. Appends the Video id to the file `videos.txt` present in the root directory.
3.  Generates markdown file `Day010.md` in the `January` subdirectory.
4.  Generates image file `Day010.jpg` in the `January/jpgs` directory.
5.  Appends `Day010.md` filename to the `January/compact.txt` file.
6.  Updates `January20XX.md` file in the root directory with the contents of `Day010.md`.
7. Updated files:
  7.1 `./videos.txt`
  7.2 `./January20XX.md`
  7.3 `./January/compact.txt`
8. Created files:
  8.1 `./January/Day010.md`
  8.2 `./January/jpgs/Day010.jpg`

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

  Updates the `January2025.md` file with the sharing text added to the `Day010.md` file.

You can add sharing to other days as well in a similar fashion.
Don't forget to execute `genmonth` with the appropriate month index for that day.

You can get the month index by executing the following bash command:

```bash
date --date="$(date --date='jan 1 + 30 days' '+%B %d,      %Y')" +%m
```

Decrement the day of year by 1 and substitute it in the command.
The preceding gives the month index for day 31.

## Generate markdown for Youtube video

Execute the `genvidmd` script with the following parameters:

- vid - video id
- caption - video title
- pathtoimg - relative path and filename of jpeg image

Example:

```bash
./genvidmd g7o7WjQc3as "Bringing the Bible back to Catholics" January/jpgs/bringingback.jpg
```

Results:

1.  Generates markdown on the command line. Used this to insert video markdown in your markdown files.
2.  Generates overlaid image file for the video as `January/jpgs/bringingback.jpg`.

## Merge monthly markdown files into one large README

1.  Edit the `stitch.md` file provided to include the markdown files you wish to merge.

2.  The file format follows:

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

Generates README with all the contents of the listed markdown files in `stitch.md`.

## Generate table of contents for markdown files

Execute the `gentoc` script as follows:

```bash
./gentoc <path to markdown file>
```

Before executing the script, update the file and place the comment `<!-- toc -->` and `<!-- tocstop -->` to generate  the table of contents inside these markers.

Results:

Generates the table of contents per the existing headings in the markdown file.

## Using the commands utility that accepts text commands in file `commands.txt`

1. Install ANTLR4

Assuming that you have Python3 and its installer pip3 installed on your machine.
You can download and install Python3 from <https://www.python.org/downloads/>.

```bash
pip install antlr4-tools antlr4-python3-runtime
```
2. Add commands to the `commands.txt` file.

Available commands:
- addvideo
- genmonth
- lintall
- genvidmd
- stitch
- gentoc

For simplicity and consistency, the commands wrap their command line equivalents.

3. Execute the commands.py script.
```
./commands.py
```
This executes the commands in order as placed in the `commands.txt`. If any command fails, the program outputs an error message for that command and executes all following commands.

4. Example `commands.txt` file
```
# example commands
addvideo "abc123456" "Example video" # add example video
genmonth 01 2025 # generate markdown for month January, 2025
genvidmd "abc123456" "Example video" "February/jpgs/examplevideo.jpg" # generate markdown for video including jpeg image
lintall # lint all the markdown files
```

The program ignores everything after the `#` symbol and treats it like a new line character.
