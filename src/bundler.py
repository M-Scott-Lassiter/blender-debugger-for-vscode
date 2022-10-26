"""Bundle add-ons into the format Blender requires to install.

Add-ons consisting of multiple files must be packaged in a .zip archive and contain a __init__.py within.

If the add-on is a single file, it cannot be named __init__.py or else it will not load correctly.
"""
from distutils.dir_util import copy_tree
import os
import shutil
import tempfile

from src.console_messages.bundler import BundlerMessages as message

def isValidBlenderAddonPath(path: str) -> bool:
    """Determine if a file path is a valid candidate for a Blender add-on.
        
        The path must
        - exist
        - be a solitary .py file or .zip archive
        
        and cannot be
        - a folder.
        - __init__.py
        """
    path = str(path)    # Required to prevent errors in case a user tries to pass a non-string
    if os.path.exists(path) and os.path.isfile(path) and os.path.basename(path) != '__init__.py':
        return True

    return False

def bundle(source_files: list[str], output_folder: str, name: str, overwrite: bool=True) -> str:
    """Bundles source files into a .zip archive importable by Blender. Returns the output filepath. If it encounters an
    error it returns None.

    `source_files`: A list of file or folder absolute path strings. Must contain at least one entry. All specified files
        or folders must exist.

    `output_folder`: Absolute folder path to put the .zip archive. This must be a folder that already exists.

    `name`: The file name to give the created .zip archive. Should not include the '.zip' file extension as the script
        will add that on. Must be less than 189 characters to prevent operating system errors while creating the .zip.

    `overwrite`: If set to `True`, this script overwrites the output .zip archive if it already exists. If `False`, it
        will halt the operation without making any changes.
    """
    safe_name = str(name)   # Safely format the name in case something other than a string passed

    def isValidSource(file_list: any) -> bool:
        """Check for valid source_files"""
        if type(file_list) is list:
            if len(file_list) == 0:
                # Bundling nothing is pointless. Don't even allow this to continue.
                message.invalid_source_empty_list()
                return
            
            for file_or_folder in file_list:
                if not os.path.exists(file_or_folder):
                    # While I could have made it continue knowing a file or folder didn't exist, that would end up with
                    #   a bundled .zip archive that did not include everything the user thought it did. I figured this
                    #   would be a more frustrating bug trying to track down than dealing with a Bundler error about how
                    #   the specified file didn't exist in the first place. 
                    message.file_does_not_exist(file_or_folder)
                    return

            return True
        message.invalid_source_not_a_list(file_list) # Provided non-list, go ahead and fail now.
        return False
    
    def isValidName(name: str) -> bool:
        """Prevent proceeding forward with names that will cause operating system errors"""
        # COME BACK WHEN I FIGURE OUT HOW TO DO THIS
        return False
    
    def copy_files_to_working_directory(file_list: list[str], working_dir: str) -> None:
        """Takes a validated list of source files and copies them to the working directory"""
        # Note that files and folders must (annoyingly) be copied using different methods.
        for src_file in file_list:
            if os.path.isfile(src_file):
                shutil.copy2(src_file, working_dir)
            else:
                copy_tree(src_file, working_dir)

    ###############################################################
    # BEGIN GUARD CLAUSES
    ###############################################################

    # Source files to bundle must pass validation criteria
    if not isValidSource(source_files):
        return
    
    # Output path must exist
    if not os.path.exists(str(output_folder)) or os.path.isfile(str(output_folder)):
        # This was a decision of convenience because the path not existing was causing problems with very bad paths.
        #   Things like "C:\users\abcd would" make a new path fine, but things like "random\string" would cause all
        #   kinds of headaches. Rather than validating the operating system CAN create that path, I decided it was not
        #   that big of an imposition on the user to make sure their desired location actually exists.
        message.output_folder_does_not_exist(output_folder)
        return
    
    # Output file name must be < 190 characters and not contain any invalid operating system file characters.
    #   I discovered this experimentally. I do not know specifically why 190 is the limit.
    if len(safe_name) > 189:
        message.output_file_name_too_long()
        return

    ###############################################################
    # GUARDS SATISFIED, INPUTS SAFE - PRODUCE BUNDLE
    ###############################################################

    final_bundle_path = os.path.join(output_folder, safe_name + ".zip")

    if os.path.exists(final_bundle_path):
        # If there is a leftover file from running this before, you must delete it as long as the user has specified
        #   that `overwrite` is true. Otherwise, we don't want to delete the old file.
        if not overwrite:
            message.bundle_already_exists(final_bundle_path)
            return
        os.remove(final_bundle_path)
    
    temp_dir = tempfile.TemporaryDirectory()
    copy_files_to_working_directory(source_files, temp_dir.name)
    shutil.make_archive(temp_dir.name, 'zip', temp_dir.name) # Creates a .zip in the same location as the working folder

    temp_zippath = temp_dir.name + ".zip"
    final_zippath = os.path.join(os.path.dirname(temp_dir.name), safe_name + ".zip")
    
    os.rename(temp_zippath, final_zippath)
    shutil.move(final_zippath, output_folder)
    temp_dir.cleanup()

    message.complete(final_bundle_path)
    return final_bundle_path
