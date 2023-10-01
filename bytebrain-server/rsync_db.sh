#!/usr/bin/env bash

# Define the source directories
source_dirs=(
  "./db"
  "./embeddings-cache"
  "./discord-cache"
)

# Prompt the user for the remote username
read -p "Enter the remote username: " remote_user

# Define remote machine information
remote_host="ziochatdirect"
remote_directory="~/workspace/zio-chat-dev"

# Loop through source directories and sync to remote
for source_dir in "${source_dirs[@]}"; do
  # Check if source directory exists
  if [ ! -d "$source_dir" ]; then
    echo "Source directory '$source_dir' does not exist. Skipping."
    continue
  fi

  # Use rsync to sync the source directory to the remote machine
  rsync -avz --delete "$source_dir" "$remote_user@$remote_host:$remote_directory/"

  # Check the rsync exit code
  if [ $? -eq 0 ]; then
    echo "Sync of '$source_dir' to '$remote_host:$remote_directory' completed successfully."
  else
    echo "Sync of '$source_dir' to '$remote_host:$remote_directory' failed with error code $?."
  fi
done
