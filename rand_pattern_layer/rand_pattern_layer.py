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

plug_in_proc   = "plug-in-py3-rand-pattern-layer"
plug_in_binary = "py3-rand-pattern-layer"

class RandPatternLayerPlugin(Gimp.PlugIn):
    """ Need to crop source image layer before running.
    """
    def do_query_procedures(self):
        return [ plug_in_proc ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")

        procedure.set_menu_label("Random Pattern Layers")
        procedure.add_menu_path('<Image>/Layer/Custom/')

        procedure.set_documentation("Random Pattern Layers",
                                    "Random Pattern Layers",
                                    name)
        procedure.set_attribution("Koh Hwee Miin", "Koh Hwee Miin", "2025")

        procedure.add_int_argument("row", "Rows", "Number of rows to generate",
                                   1, 1000, 3, GObject.ParamFlags.READWRITE)

        return procedure

    def run(self, procedure, run_mode, image, drawables, config, userdata):
        Gimp.message("Running rand_pattern_layer")
        if run_mode == Gimp.RunMode.INTERACTIVE:
            Gimp.message("Running rand_pattern_layer plugin in interactive mode")
            GimpUi.init(plug_in_binary)
            
            dialog = GimpUi.ProcedureDialog.new(procedure, config, "Generate pattern using images in selected group")
            dialog.fill(["row"])
            if not dialog.run():
                dialog.destroy()
                return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
            else:
                dialog.destroy()
                
        max_row = config.get_property("row")
        
        Gimp.message("Getting active layers")
        layers = image.get_selected_layers()
        if layers is None or len(layers) <= 0:
            Gimp.message("Must select at least one layer")
        
        else:
            image_layers = []
            for layer in layers:
                image_layers.extend(layer.get_children())
                
            if len(image_layers) <= 0:
                Gimp.message("Selected layers must have children")
                return procedure.new_return_values(
                    Gimp.PDBStatusType.EXECUTION_ERROR,
                    GLib.Error(message="Selected layers must have children")
                )

            image.undo_group_start()
            try:
                result_group = Gimp.GroupLayer.new(image, "Random Pattern Results")
                image.insert_layer(result_group, None, 0)
                
                row_cnt = 0
                col_cnt = 0
                curr_x = 0
                curr_y = 0
                last_offset_x = 0
                last_offset_y = 0
                while curr_y < image.get_height():
                    row_result_group = Gimp.GroupLayer.new(image, f"Random Pattern Row {row_cnt}")
                    image.insert_layer(row_result_group, result_group, -1)
                
                    while curr_x < image.get_width():
                        choice = random.randint(0, len(image_layers) - 1)
                        
                        new_layer = image_layers[choice].copy()
                        new_layer.set_name(f"Random Pattern {row_cnt}-{col_cnt}")
                        col_cnt += 1
                        
                        layer_w = image_layers[choice].get_width()
                        layer_h = image_layers[choice].get_height()                        
                        last_offset_x = layer_w / 2
                        last_offset_y = layer_h / 2
                        curr_x += last_offset_x
                        
                        new_layer.set_offsets(curr_x, curr_y)
                        image.insert_layer(new_layer, row_result_group, -1)
                        Gimp.message(f"Insert layer {new_layer.get_name()} at {curr_x},{curr_y}")
                    
                    row_cnt += 1
                    if row_cnt >= max_row:
                        break
                    
                    curr_x = 0
                    curr_y += last_offset_y
                
                image.undo_group_end()
                return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())
            
            except Exception as e:
                image.undo_group_end()
                return procedure.new_return_values(
                    Gimp.PDBStatusType.EXECUTION_ERROR,
                    GLib.Error(message=str(e))
                )

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(RandPatternLayerPlugin.__gtype__, sys.argv)