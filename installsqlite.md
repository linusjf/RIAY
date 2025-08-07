# Steps to install sqlite from source

To access sources directly using Fossil, first install Fossil version 2.0 or later. Source tarballs and precompiled binaries available at <https://fossil-scm.org/home/uv/download.html>. Fossil is a stand-alone program. To install, simply download or build the single executable file and put that file someplace on your $PATH. Then run commands like this:

```bash
mkdir -p ~/sqlite
cd ~/sqlite
fossil open https://sqlite.org/src
```

Source: <https://sqlite.org/src/doc/trunk/README.md>
