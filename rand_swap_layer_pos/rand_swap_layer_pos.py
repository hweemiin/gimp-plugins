#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gtk

plug_in_proc   = "plug-in-py3-rand-swap-layer-pos"
plug_in_binary = "py3-rand-swap-layer-pos"

class RandSwapLayerPosPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return [ plug_in_proc ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")

        procedure.set_menu_label("Random Swap Layers Position")
        procedure.add_menu_path('<Image>/Layer/Custom/')

        procedure.set_documentation("Random Swap Layers Position",
                                    "Random Swap Layers Position",
                                    name)
        procedure.set_attribution("Koh Hwee Miin", "Koh Hwee Miin", "2025")
        
        procedure.add_boolean_argument("x", "Swap X", "Swap X coordinate", True, GObject.ParamFlags.READWRITE)
        procedure.add_boolean_argument("y", "Swap Y", "Swap Y coordinate", False, GObject.ParamFlags.READWRITE)

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, userdata):
        Gimp.message("Running rand_swap_layer_pos")
        if run_mode == Gimp.RunMode.INTERACTIVE:
            Gimp.message("Running rand_swap_layer_pos plugin in interactive mode")
            GimpUi.init(plug_in_binary)
            
            dialog = GimpUi.ProcedureDialog.new(procedure, config, "Randomly Swap Layers Position")
            dialog.fill(["x", "y"])
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
            else:
                dialog.destroy()
                
        swap_x = config.get_property("x")
        swap_y = config.get_property("y")
        
        Gimp.message("Getting active layers")
        layers = image.get_selected_layers()
        if layers is None or len(layers) <= 0:
            Gimp.message("Must select at least one layer")
        else:
            for layer in layers:
                children = layer.get_children()
                Gimp.message("Processing layer {} with {} children".format(layer.get_name(), len(children)))
                
                positions = []
                for child in children:
                    result, x, y = child.get_offsets()
                    if not result:
                        Gimp.message("Getting offset of {} return false".format(child.get_name()))
                        
                    positions.append((x, y))
                    
                random.shuffle(positions)
                
                image.undo_group_start()
                for child, (x, y) in zip(children, positions):
                    result, old_x, old_y = child.get_offsets()
                    if not result:
                        Gimp.message("Getting offset of {} return false".format(child.get_name()))                   
                    
                    new_x = x if swap_x else old_x
                    new_y = y if swap_y else old_y
                    child.set_offsets(new_x, new_y)
                image.undo_group_end()
                
            Gimp.displays_flush()
                
        # do what you want to do, then, in case of success, return:
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(RandSwapLayerPosPlugin.__gtype__, sys.argv)