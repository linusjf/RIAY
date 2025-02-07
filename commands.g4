grammar commands;

program: (command NEWLINE | NEWLINE)* command? EOF;

command: addvideo | genmonth  | lintall | genvidmd | stitch | gentoc;

addvideo: 'addvideo' videoId videoName;
videoId: STRING;
videoName: STRING;

genmonth: 'genmonth' month year;
month: MONTH_DIGIT;
year: YEAR;

lintall: 'lintall';

stitch: 'stitch';

gentoc: 'gentoc' pathtomdfile;
pathtomdfile: STRING;

genvidmd: 'genvidmd' videoId caption pathtoimg;
caption: STRING;
pathtoimg: STRING;

STRING: '"' .*? '"';
YEAR: [2][0-9][0-9][0-9];
MONTH_DIGIT: '1' '0'..'2' | '0' '1'..'9' | '1'..'9';

NEWLINE: '\r'? '\n';

WS: [ \t\r\n]+ -> skip;

COMMENT: '#' ~[\r\n]* '\r'? '\n'  -> type(NEWLINE);
