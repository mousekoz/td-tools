# Mawusi Blewuada 2024
# Tool to find and re-link all missing scene textures

# **INSTRUCTIONS**
# Open Maya scene and run this script from the shelf or script editor
# The required texture files must be located within
# the scene file directory or descending directories

import maya.cmds as cmds
import os


class TexturePathTool:
    def __init__(self):
        self.window_name = "toolWindow"
        self.all_textures = cmds.ls(type="texture2d")
        self.current_dir = os.path.dirname(
            cmds.file(sceneName=True, query=True))
        self.missing_textures = self.find_invalid_texture_paths()

    def create_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)

        cmds.window(self.window_name, title="Texture Path Tool", sizeable=True)

        # UI ELEMENTS
        cmds.columnLayout(adjustableColumn=True, columnOffset=['both', 40])

        cmds.separator(height=10, style='none')

        if self.missing_textures:
            cmds.columnLayout(columnAttach=['left', 0])
            cmds.text("{} missing texture files.".format(
                len(self.missing_textures))
            )

            cmds.separator(height=10, style='none')

            for mtx in self.missing_textures:
                cmds.text(label=cmds.getAttr(mtx + ".fileTextureName"))

            cmds.setParent('..')

            cmds.separator(height=10, style='none')

            cmds.columnLayout()
            cmds.button(label="Repair",
                        command=self.fix_texture_paths,
                        width=100)

            cmds.separator(height=10, style='none')

            cmds.button(label="Cancel", command=self.close_window, width=100)

        else:  # If no missing paths have been found
            cmds.columnLayout(columnAttach=['left', 40])
            cmds.text(label="No missing texture files in current scene.")
            cmds.separator(height=10, visible=True, style='none')

            cmds.setParent('..')

            cmds.columnLayout(adjustableColumn=True,
                              columnOffset=['both', 160])

            cmds.button(label="OK", command=self.close_window, width=100)

        cmds.showWindow(self.window_name)

    def close_window(self, *args):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)

    def find_invalid_texture_paths(self):
        missing_textures = []

        # Check each texture file path,
        # if given path doesn't exist, add to missing_textures list
        for tx in self.all_textures:
            tx_file_attr = tx + ".fileTextureName"
            file_path = cmds.getAttr(tx_file_attr)

            if not os.path.exists(file_path):  # Check if the path is valid
                print("Node {}: Texture file {} doesn't exist".format(tx, file_path))
                missing_textures.append(tx)
            else:
                print("Node {} has a valid texture: {}".format(tx, file_path))

        return missing_textures

    def fix_texture_paths(self, *args):
        missing_textures = []  # Store any remaining missing file paths
        fixed_textures = []    # Store replacement paths
        fixed_path_count = 0

        for tx in self.missing_textures:
            tx_file_attr = tx + ".fileTextureName"
            file_path = cmds.getAttr(tx_file_attr)
            file_name = os.path.basename(file_path)

            path_found = False

            # Search scene file directory for file with matching name
            for root, dirs, files in os.walk(self.current_dir):
                if file_name in files:
                    update_path = os.path.join(root, file_name)
                    print("Valid texture file found: {}".format(update_path))

                    tx_file_attr = tx + ".fileTextureName"

                    # Replace invalid path with newly found path
                    cmds.setAttr(tx_file_attr, update_path, type="string")

                    # Ensure attribute has been updated
                    new_file_path = cmds.getAttr(tx_file_attr)
                    print("Path updated to {}".format(new_file_path))

                    path_found = True
                    fixed_path_count += 1
                    fixed_textures.append(new_file_path)

                    break  # Terminate search when first match is found

            if not path_found:
                missing_textures.append(tx)
                print("{} path not found".format(file_name))

        self.missing_textures = missing_textures

        if len(missing_textures) == 0:  # Check for remaining incorrect paths
            message = "All {} file paths repaired.\n\n{}".format(
                fixed_path_count,
                '\n\n'.join(fixed_textures)
                )
        else:
            message = "{} texture file paths could not be repaired.\
            \n{} file paths repaired.\n{}".format(
                len(missing_textures),
                fixed_path_count,
                '\n'.join(fixed_textures)
                )

        cmds.confirmDialog(
            title='Result',
            message=message,
            button=['OK'],
            defaultButton='OK',
            cancelButton='OK',
            dismissString='OK',
        )

        # Close GUI after closing confirmDialog
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)


tpt = TexturePathTool()
tpt.create_ui()
