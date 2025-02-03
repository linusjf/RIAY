grammar commands;

program: (command NEWLINE)* command? EOF;

command: addVideo | genMonth | lintAll | genVidMD;

addVideo: 'addvideo' videoId videoName;
videoId: STRING;
videoName: STRING;

genMonth: 'genmonth' month year;
month: MONTH_DIGIT;
year: YEAR;

lintAll: 'lintall';

genVidMD: 'genvidmd' videoId caption pathtoimg;
caption: STRING;
pathtoimg: STRING;

STRING: '"' .*? '"';
YEAR: [2][0-9][0-9][0-9];
MONTH_DIGIT: '1' '0'..'2' | '0' '1'..'9' | '1'..'9';

NEWLINE: '\r'? '\n';

WS: [ \t\r\n]+ -> skip;
