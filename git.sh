#!/usr/bin/env bash

# Git-related utility functions

function get_github_repo() {
  local git_url
  git_url=$(git remote get-url origin 2> /dev/null)

  if [[ "$git_url" == git@github.com:* ]]; then
    printf "%s" "$git_url" | sed -E 's|git@github.com:([^\.]+)(\.git)?|\1|'
  elif [[ "$git_url" == https://github.com/* ]]; then
    printf "%s" "$git_url" | sed -E 's|https://github.com/([^\.]+)(\.git)?|\1|'
  else
    die "Error: Could not determine GitHub repo from remote: $git_url"
  fi
}
