# This file helps to package the ndr-core project as a Django module.
# It copies the project files to a module directory and then runs the
# necessary commands to prepare the module for use.
import os
import shutil

# Initialize the source and destination paths
src = './ndr_core'
module_dest = 'C:/Users/sorin/Documents/python_modules/django-ndr-core/'
src_dest = os.path.join(module_dest, 'ndr_core')

# Create dest directory if it does not exist
try:
    os.makedirs(module_dest)
    print("Created module directory")
except FileExistsError:
    print("Module directory already exists")

# Remove the existing directory if it exists
if os.path.exists(src_dest):
    shutil.rmtree(src_dest, ignore_errors=True)
    print("Removed existing source directory")

# Copy the project files to the module directory
destination = shutil.copytree(src, src_dest)
print("Copied files to " + destination)

# Move the files in the deployment directory to the root
deploy_dir = os.path.join(src_dest, 'deployment')
shutil.copytree(deploy_dir, module_dest, dirs_exist_ok=True)
print("Copied configuration files to " + module_dest)

# Remove the files that are not needed in the source
files_to_remove = ["__pycache__/", "deployment"]
for file in files_to_remove:
    shutil.rmtree(os.path.join(destination, file), ignore_errors=False)
    print("Removed " + file)

# Print the commands to run to prepare the module
print("Run the following commands to prepare the module:")
print("cd " + module_dest)
print("python setup.py sdist")
