# Steps to install sqlite from source

To access sources directly using Fossil, first install Fossil version 2.0 or later. Source tarballs and precompiled binaries available at <https://fossil-scm.org/home/uv/download.html>. Fossil is a stand-alone program. To install, simply download or build the single executable file and put that file someplace on your $PATH. Then run commands like this:

```bash
mkdir -p ~/sqlite
cd ~/sqlite
fossil open https://sqlite.org/src
mkdir bld
cd bld
../configure --enable-all   CFLAGS="-DSQLITE_ENABLE_FTS5 -DSQLITE_ENABLE_LOAD_EXTENSION"
make OPTIONS=-DSQLITE_DEFAULT_FOREIGN_KEYS=1 OPTS=-DSQLITE_ENABLE_UPDATE_DELETE_LIMIT OPTS=-DSQLITE_ENABLE_FTS5 OPTS=-DSQLITE_ENABLE_LOAD_EXTENSION sqlite3
sudo ln -s  ~/sqlite/bld/sqlite3 /usr/local/bin/sqlite3
```

Source: <https://sqlite.org/src/doc/trunk/README.md>
