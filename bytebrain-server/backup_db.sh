#!/usr/bin/env bash

# List of source directories
source_dirs=(
  "./db/embeddings-cache"
  "./db/discord-cache"
)

# Create a timestamp for the backup folder
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
backup_dir="./backups/$timestamp"

# Loop through source directories
for source_dir in "${source_dirs[@]}"; do
  # Check if source directory exists
  if [ ! -d "$source_dir" ]; then
    echo "Source directory '$source_dir' does not exist. Backup aborted."
    continue  # Move to the next source directory if it doesn't exist
  fi

  if [ ! -d "$backup_dir" ]; then
    mkdir -p "$backup_dir"
    echo "Created backup directory: $backup_dir"
  fi

  # Create the backup using rsync
  rsync -av --delete "$source_dir" "$backup_dir"

  # Check the rsync exit code
  if [ $? -eq 0 ]; then
    echo "Backup of '$source_dir' completed successfully."
  else
    echo "Backup of '$source_dir' failed with error code $?."
  fi

done
