# Developer Automation: Compressing and archiving development source paths dynamically

import os
import shutil
from datetime import datetime
import zipfile

def package_workspace_backup(source_dir, backup_destination_root):
    """
    Scans a source development path, generates an archive target directory,
    and compresses all active assets into a timestamp-labeled zip profile.
    """
    print("--- Developer Tools: Automated Projects Backup Packager ---")
    
    if not os.path.exists(source_dir):
        print(f" Source directory error: Target folder '{source_dir}' does not exist.")
        return False
        
    # 1. Generate an automated timestamp string for the backup profile label
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = os.path.basename(os.path.normpath(source_dir))
    archive_name = f"backup_{folder_name}_{timestamp}.zip"
    
    # 2. Ensure the destination backup directory exists on the system filesystem
    if not os.path.exists(backup_destination_root):
        os.makedirs(backup_destination_root)
        print(f" Generated fresh target storage directory: {backup_destination_root}")
        
    final_archive_path = os.path.join(backup_destination_root, archive_name)
    print(f" Compressing source folder: '{source_dir}'...")
    
    try:
        # 3. Open a zip write stream and iterate through local file structures
        with zipfile.ZipFile(final_archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                # Skip archiving existing compressed files or hidden tracking trees
                if '.git' in root or 'backups_vault' in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    # Compute relative paths inside the archive to keep structure clean
                    relative_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                    zipf.write(file_path, relative_path)
                    
        print(f" Backup generated successfully!")
        print(f" Compressed archive file exported to: {final_archive_path}")
        return True
        
    except Exception as err:
        print(f" Archiving process interrupted: {err}")
        return False

if __name__ == "__main__":
    # Target path: Set to scan your active project workspace folder dynamically
    active_source_workspace = os.getcwd()
    
    # Target destination: A separate storage vault folder inside the workspace path
    backup_vault_destination = os.path.join(active_source_workspace, "backups_vault")
    
    # Run the automated backup sequence
    package_workspace_backup(active_source_workspace, backup_vault_destination)