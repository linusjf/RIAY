grammar commands;

program: (command NEWLINE | NEWLINE)* command? EOF;

command: addvideo | genmonth | lintall | stitch | gentoc | addvideotoday | addimgtoday;

addvideo: 'addvideo' videoId videoName;
videoId: STRING;
videoName: STRING;

genmonth: 'genmonth' month year?;
month: MONTH;
year: YEAR;

lintall: 'lintall';

stitch: 'stitch';

gentoc: 'gentoc' pathtomdfile;
pathtomdfile: STRING;

addvideotoday: 'addvideotoday' videoId dayofyear;
dayofyear: DAY_NUMBER;

addimgtoday: 'addimgtoday' imagepath caption dayofyear;
imagepath: STRING;
caption: STRING;

STRING: '"' .*? '"';
YEAR: [2][0-9][0-9][0-9];
MONTH: '1' '0'..'2' | '0' '1'..'9' | '1'..'9';

DAY_NUMBER: THREE_DIGIT;

fragment THREE_DIGIT
  : '36' [0-6]            // 360–366
  | '3' [0-5] [0-9]       // 300–359
  | [12] [0-9] [0-9]      // 100–299
  | '0' [1-9] [0-9]      // 010 - 099
  | '0' '0' [1-9]        // 001 - 009
  ;

NEWLINE: '\r'? '\n';

WS: [ \t\r\n]+ -> skip;

COMMENT: '#' ~[\r\n]* '\r'? '\n'  -> type(NEWLINE);
ANY: .;
