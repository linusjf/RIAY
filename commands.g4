grammar commands;

// Define a comment as a line starting with '#'
COMMENT: '#' ~[\r\n]* -> skip;

// The program rule matches one of the available commands
program: addVideo | genMonth | lintAll | genVidMD;

// The addVideo command requires a video ID and a video name
addVideo: 'addvideo' videoId videoName;
videoId: STRING; // Video ID is a string
videoName: STRING; // Video name is a string

// The genMonth command requires a month and a year
genMonth: 'genmonth' month year;
month: MONTH_DIGIT;
year: DIGIT DIGIT DIGIT DIGIT; // Year is a 4-digit number

// The lintAll command has no arguments
lintAll: 'lintall';

// The genVidMD command requires a video ID, caption, and path to image
genVidMD: 'genvidmd' videoId caption pathtoimg;
caption: STRING; // Caption is a string
pathtoimg: STRING; // Path to image is a string

// Define a string as a sequence of characters enclosed in quotes
STRING: '"' .*? '"';

MONTH_DIGIT: [1-9] | '1' '0'..'2';

// Define a digit as a single character between 0 and 9
DIGIT: [0-9];

// Define an integer as a sequence of digits
INTEGER: [0-9]+;

// Ignore whitespace characters
WS: [ \t\r\n]+ -> skip;
