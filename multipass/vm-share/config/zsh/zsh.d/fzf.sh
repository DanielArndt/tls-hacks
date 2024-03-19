# shellcheck shell=bash

git_repo_locations_file="${HOME}/.git_repo_locations"

function fupdb {
    zle -R "Updating locate database for ${HOME}..."
    find "${HOME}" -name .git -exec dirname {} \; -prune > "${git_repo_locations_file}"
}

# Fuzzy search for git repo
function frepo {
    # If .locatedb doesn't exist, print a message and abort
    if [ ! -f "${git_repo_locations_file}" ]; then
        fupdb
    fi

    REPO_NAME=$(fzf < "${git_repo_locations_file}")
    if [ "$REPO_NAME" ]; then
        cd "$REPO_NAME" || echo "Repo no longer exists... update locate database again (\`fupdb\`)"
    fi
    zle reset-prompt
}

# Define a widget called "frepo", mapped to our function above.
zle -N frepo

# Bind it to ESC-i.
bindkey "^[g" frepo

fzf-in-pwd() {
    ls_output=$("ls" -A)
    non_hidden_files=$(echo "$ls_output" | grep -v "^\.")
    hidden_files=$(echo "$ls_output" | grep "^\.")
    file_name=$( (echo "${non_hidden_files}" && echo ${hidden_files}) | fzf --multi --preview 'tree-or-bat {}' --bind 'tab:toggle+up,btab:toggle+down' | tr '\n' ' ')
    BUFFER+="$file_name"
    CURSOR=$((CURSOR + ${#file_name}))
}
zle -N fzf-in-pwd
bindkey "^F" fzf-in-pwd
