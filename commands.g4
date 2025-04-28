grammar commands;

program: (command NEWLINE | NEWLINE)* command? EOF;

command: addvideo | genmonth | lintall | stitch | gentoc | addvideotoday;

addvideo: 'addvideo' videoId videoName;
videoId: STRING;
videoName: STRING;

genmonth: 'genmonth' month year?;
month: MONTH_DIGIT;
year: YEAR;

lintall: 'lintall';

stitch: 'stitch';

gentoc: 'gentoc' pathtomdfile;
pathtomdfile: STRING;

addvideotoday: 'addvideotoday' videoId dayofyear;
dayofyear: DAY_NUMBER;

STRING: '"' .*? '"';
YEAR: [2][0-9][0-9][0-9];
MONTH_DIGIT: '1' '0'..'2' | '0' '1'..'9' | '1'..'9';
DAY_NUMBER
  : '0'? [1-9]                         // 1-9 with optional leading zero
  | '0'? [1-9] [0-9]                    // 10-99 with leading zero
  | [1-2] [0-9] [0-9]                  // 100-299
  | '3' [0-5] [0-9]                    // 300-359
  | '36' [0-6]                         // 360-366
  ;


NEWLINE: '\r'? '\n';

WS: [ \t\r\n]+ -> skip;

COMMENT: '#' ~[\r\n]* '\r'? '\n'  -> type(NEWLINE);
